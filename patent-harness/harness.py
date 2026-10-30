#!/usr/bin/env python3
"""Run bounded, checkpointed patent tasks over the remote MCP service."""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "patent-search"))
from patent_mcp import DEFAULT_ENDPOINT, McpError, PatentMcpClient


def now():
    return datetime.now(timezone.utc).isoformat()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def save(path: Path, data: dict):
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def validate_plan(plan):
    if not isinstance(plan, dict) or plan.get("version") != 1:
        raise ValueError("任务计划 version 必须为 1")
    steps = plan.get("steps")
    if not isinstance(steps, list) or not 1 <= len(steps) <= 50:
        raise ValueError("任务计划需包含 1–50 步")
    seen = set()
    for step in steps:
        if not isinstance(step, dict) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]{0,63}", str(step.get("id", ""))):
            raise ValueError("每步需要有效的 id")
        if step["id"] in seen:
            raise ValueError("步骤 id 不能重复")
        if not isinstance(step.get("arguments"), dict) or not isinstance(step.get("tool"), str):
            raise ValueError("每步需要 tool 和 arguments")
        # Resolve references only to earlier outputs; no arbitrary code or shell expansion.
        def check(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    ref = value["$ref"]
                    if set(value) != {"$ref"} or not isinstance(ref, str) or "#/" not in ref or ref.split("#", 1)[0] not in seen:
                        raise ValueError("$ref 必须引用前面的步骤，例如 search#/patents/0/id")
                else:
                    for v in value.values(): check(v)
            elif isinstance(value, list):
                for v in value: check(v)
        check(step["arguments"])
        seen.add(step["id"])
    return steps


def resolve(value, results):
    if isinstance(value, dict):
        if "$ref" in value:
            step, pointer = value["$ref"].split("#", 1)
            out = results[step]
            try:
                for key in pointer[1:].split("/"):
                    key = key.replace("~1", "/").replace("~0", "~")
                    out = out[int(key)] if isinstance(out, list) else out[key]
            except (KeyError, IndexError, TypeError, ValueError):
                raise ValueError("引用结果不存在: " + value["$ref"]) from None
            return out
        return {key: resolve(val, results) for key, val in value.items()}
    if isinstance(value, list):
        return [resolve(item, results) for item in value]
    return value


def write_report(directory, state):
    lines = ["# 专利任务执行结果", "", "状态：" + state["status"],
             "", "工具调用尝试次数：" + str(state["attempts"]),
             "", "完整原始结果保存在 checkpoint.json。每次工具调用沿用原 API 的权限和配额。", ""]
    for key, item in state["steps"].items():
        lines.extend(["## " + key, "", "状态：" + item["status"], ""])
        data = item.get("result", {})
        if isinstance(data, dict) and isinstance(data.get("patents"), list):
            lines.extend(["| 公开号 | 标题 |", "| --- | --- |"])
            for patent in data["patents"]:
                def cell(value): return str(value or "").replace("|", "\\|").replace("\n", " ")
                lines.append("| " + cell(patent.get("id")) + " | " + cell(patent.get("title")) + " |")
        if item.get("error"):
            lines.append(item["error"])
        lines.append("")
    (directory / "report.md").write_text("\n".join(lines), encoding="utf-8")


def execute(plan, directory: Path, client, *, max_calls=10, resume=False, retry_failed=False):
    steps = validate_plan(plan)
    if not 1 <= max_calls <= 50:
        raise ValueError("max-calls 必须在 1–50 之间")
    directory.mkdir(parents=True, exist_ok=True)
    checkpoint = directory / "checkpoint.json"
    with (directory / ".lock").open("a+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("此任务正在执行，不能同时运行两个进程") from None
        identity = fingerprint({"plan": plan, "endpoint": client.endpoint,
                                "credential": hashlib.sha256(client.token.encode()).hexdigest()})
        if resume:
            state = json.loads(checkpoint.read_text(encoding="utf-8"))
            if state.get("identity") != identity:
                raise ValueError("计划、MCP 地址或 Token 已改变；请创建新的输出目录")
        else:
            if checkpoint.exists():
                raise ValueError("目录已有任务，请使用 resume 或选择新目录")
            if len(steps) > max_calls:
                raise ValueError("任务步骤超过调用预算，请减少步骤或显式增加 --max-calls")
            state = {"version": 1, "identity": identity, "created_at": now(), "status": "pending",
                     "attempts": 0, "steps": {step["id"]: {"status": "pending"} for step in steps}}
            save(checkpoint, state)
        results = {key: item["result"] for key, item in state["steps"].items() if item["status"] == "succeeded"}
        for step in steps:
            item = state["steps"][step["id"]]
            if item["status"] == "succeeded":
                continue
            if item["status"] in ("running", "uncertain", "failed") and not retry_failed:
                raise ValueError("步骤 " + step["id"] + " 上次未成功，可能已经计次。检查 checkpoint 后用 --retry-failed 显式重试")
            if state["attempts"] >= max_calls:
                state["status"] = "budget_exhausted"
                save(checkpoint, state); write_report(directory, state)
                raise ValueError("调用预算已用尽；已完成步骤不会重跑")
            try:
                arguments = resolve(step["arguments"], results)
            except ValueError as error:
                item.update(status="failed", error=str(error)); state["status"] = "failed"
                save(checkpoint, state); write_report(directory, state)
                return state
            item.update(status="running", started_at=now())
            item.pop("error", None)
            state["attempts"] += 1; state["status"] = "running"
            # Persist before network IO so a process crash can never silently replay a call.
            save(checkpoint, state)
            try:
                data = client.call(step["tool"], arguments)
                item["result"] = data
                if data.get("success") is not True:
                    item.update(status="failed", error="API 返回失败，请查看 result 中的 code / message")
                    state["status"] = "failed"
                else:
                    item["status"] = "succeeded"
                    results[step["id"]] = data
            except McpError as error:
                item.update(status="uncertain" if error.uncertain else "failed", error=str(error))
                state["status"] = item["status"]
            item["finished_at"] = now()
            save(checkpoint, state); write_report(directory, state)
            if item["status"] != "succeeded":
                return state
        state["status"] = "succeeded"; state["finished_at"] = now()
        save(checkpoint, state); write_report(directory, state)
        return state


def main():
    parser = argparse.ArgumentParser(description="9235 专利任务 Harness：MCP、多步执行、断点恢复")
    parser.add_argument("command", choices=("doctor", "tools", "run", "resume"))
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--out", type=Path, default=Path("runs/research"))
    parser.add_argument("--max-calls", type=int, default=10)
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.command in ("run", "resume"):
            if not args.plan:
                raise ValueError("请提供 --plan plan.json")
            plan = json.loads(args.plan.read_text(encoding="utf-8"))
            steps = validate_plan(plan)
            if args.dry_run:
                print(json.dumps({"steps": steps, "planned_calls": len(steps), "max_calls": args.max_calls}, ensure_ascii=False, indent=2))
                return 0
        client = PatentMcpClient(os.environ.get("PATENT_API_TOKEN", ""), os.environ.get("PATENT_MCP_URL", DEFAULT_ENDPOINT))
        if args.command in ("doctor", "tools"):
            tools = client.tools()
            print(json.dumps({"ok": True, "endpoint": client.endpoint, "tool_count": len(tools),
                              "tools": tools if args.command == "tools" else [tool["name"] for tool in tools]}, ensure_ascii=False, indent=2))
            return 0
        state = execute(plan, args.out, client, max_calls=args.max_calls,
                        resume=args.command == "resume", retry_failed=args.retry_failed)
        print(json.dumps({"status": state["status"], "attempts": state["attempts"], "output": str(args.out)}, ensure_ascii=False))
        return 0 if state["status"] == "succeeded" else 1
    except (ValueError, McpError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
