#!/usr/bin/env python3
"""
检查 OpenClaw / 专利技能相关环境变量是否已配置（不打印任何密钥或敏感值）。
"""

import json
import os


def _is_set(name: str) -> bool:
    return bool((os.environ.get(name) or "").strip())


def _redacted_summary(name: str) -> str:
    """仅说明是否设置；元数据类变量只显示键名列表，不输出内容。"""
    if name not in os.environ:
        return "未设置"
    raw = os.environ[name]
    if not raw.strip():
        return "已设置（空）"
    if name.startswith("PATENT_") and name != "PATENT_API_TOKEN":
        return f"已设置（值已省略，长度 {len(raw)}）"
    if name in ("OPENCLAW_SKILL_METADATA", "OPENCLAW_SKILL_CONFIG"):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return f"已设置（JSON 对象，键: {', '.join(sorted(data.keys())[:12])}…）"
            return "已设置（JSON，内容已省略）"
        except json.JSONDecodeError:
            return "已设置（非 JSON，内容已省略）"
    if name == "PATENT_API_TOKEN":
        return "已设置（值已省略）"
    return "已设置（值已省略）"


print("检查环境变量（不输出密钥内容）")
print("=" * 60)

patent_keys = sorted(k for k in os.environ if k.startswith("PATENT_"))
print(f"以 PATENT_ 开头的变量数量: {len(patent_keys)}")
for k in patent_keys:
    print(f"  - {k}: {_redacted_summary(k)}")

openclaw_vars = [
    "PATENT_API_TOKEN",
    "OPENCLAW_SKILL_NAME",
    "OPENCLAW_SKILL_METADATA",
    "OPENCLAW_SKILL_CONFIG",
]

print("\n特定变量:")
for var in openclaw_vars:
    mark = "是" if _is_set(var) else "否"
    print(f"  {var}: 已配置={mark}  {_redacted_summary(var)}")

print(f"\n工作目录: {os.getcwd()}")
print(f"脚本目录: {os.path.dirname(os.path.abspath(__file__))}")

config_files = ["config.json", ".env", "config.example.json"]
print("\n配置文件是否存在:")
for config_file in config_files:
    exists = os.path.exists(config_file)
    print(f"  {config_file}: {'是' if exists else '否'}")
    if exists and config_file == "config.json":
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            has_token = bool((config.get("token") or "").strip())
            print(f"    config.json 内含非空 token 字段: {'是' if has_token else '否'}")
        except (OSError, json.JSONDecodeError):
            print("    config.json: 无法解析")
