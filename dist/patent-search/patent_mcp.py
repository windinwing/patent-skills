"""Small synchronous MCP client for the 9235 JSON/Streamable HTTP service.

Used by OpenClaw, mchat's existing patent-search nodes, and the task harness.
Credentials stay in request headers. Requests that might consume quota are never retried.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_ENDPOINT = "https://www.9235.net/api/mcp"
PROTOCOL = "2025-06-18"
MAX_RESPONSE = 16 * 1024 * 1024


class McpError(Exception):
    def __init__(self, message: str, *, code: int | None = None, uncertain: bool = False):
        super().__init__(message)
        self.code, self.uncertain = code, uncertain


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class PatentMcpClient:
    def __init__(self, token: str, endpoint: str = DEFAULT_ENDPOINT, timeout: int = 60):
        parsed = urllib.parse.urlsplit(endpoint)
        local_http = parsed.scheme == "http" and parsed.hostname in ("127.0.0.1", "localhost", "::1")
        if (parsed.scheme != "https" and not local_http) or not parsed.hostname:
            raise ValueError("MCP 地址必须使用 HTTPS（本地测试允许 loopback HTTP）")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("MCP 地址不能包含凭证、查询参数或 fragment")
        if not token or "\n" in token or "\r" in token:
            raise ValueError("缺少有效的 PATENT_API_TOKEN")
        self.token, self.endpoint, self.timeout = token, endpoint, timeout
        self._id, self._ready = 0, False
        self._opener = urllib.request.build_opener(NoRedirect())

    def _request(self, method: str, params: dict | None = None, *, notification: bool = False) -> dict:
        self._id += 1
        body: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if not notification:
            body["id"] = self._id
        if params is not None:
            body["params"] = params
        request = urllib.request.Request(
            self.endpoint, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
            headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": PROTOCOL},
        )
        charged = method == "tools/call"
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                if notification and response.status == 202:
                    return {}
                raw = response.read(MAX_RESPONSE + 1)
                content_type = response.headers.get_content_type()
        except urllib.error.HTTPError as error:
            raise McpError("MCP HTTP %s，请检查 Token、权限和服务状态" % error.code,
                           code=error.code, uncertain=charged and error.code >= 500) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise McpError("MCP 连接中断或超时；未自动重试", uncertain=charged) from None
        if len(raw) > MAX_RESPONSE:
            raise McpError("MCP 返回内容超出上限", uncertain=charged)
        try:
            if content_type == "text/event-stream":
                # JSON response mode is used by 9235; accept a bounded SSE response too.
                result = None
                for event in raw.decode("utf-8").replace("\r\n", "\n").split("\n\n"):
                    data = "\n".join(line[5:].lstrip() for line in event.splitlines() if line.startswith("data:"))
                    if data:
                        candidate = json.loads(data)
                        if candidate.get("id") == body.get("id"):
                            result = candidate
                if result is None:
                    raise ValueError("Missing SSE response")
            elif content_type == "application/json":
                result = json.loads(raw)
            else:
                raise ValueError("Unexpected content type")
            if not isinstance(result, dict) or result.get("jsonrpc") != "2.0" or result.get("id") != body.get("id"):
                raise ValueError("Invalid response envelope")
            if "error" in result:
                code = result["error"].get("code")
                raise McpError("MCP 协议错误 %s" % code, code=code,
                               uncertain=charged and code not in (-32600, -32601, -32602))
            if not isinstance(result.get("result"), dict):
                raise ValueError("Invalid result")
            return result["result"]
        except (ValueError, TypeError, AttributeError, UnicodeError):
            raise McpError("MCP 返回格式无效；未自动重试", uncertain=charged) from None

    def initialize(self) -> dict:
        result = self._request("initialize", {"protocolVersion": PROTOCOL, "capabilities": {},
                               "clientInfo": {"name": "9235-patent-harness", "version": "1.0.0"}})
        if result.get("protocolVersion") != PROTOCOL:
            raise McpError("服务器未协商到受支持的协议版本")
        self._request("notifications/initialized", notification=True)
        self._ready = True
        return result

    def tools(self) -> list[dict]:
        if not self._ready:
            self.initialize()
        return self._request("tools/list").get("tools", [])

    def call(self, name: str, arguments: dict) -> dict:
        if not self._ready:
            self.initialize()
        result = self._request("tools/call", {"name": name, "arguments": arguments})
        data = result.get("structuredContent")
        if not isinstance(data, dict):
            for part in result.get("content", []):
                if part.get("type") == "text":
                    try:
                        candidate = json.loads(part["text"])
                        if isinstance(candidate, dict):
                            data = candidate
                            break
                    except (ValueError, TypeError):
                        pass
        if not isinstance(data, dict):
            raise McpError("MCP 工具未返回结构化结果，本次可能已计次", uncertain=True)
        if result.get("isError"):
            data = dict(data)
            data["success"] = False
        return data


_ENDPOINTS = {
    "/s": ("patent_search", {"q": "query", "p": "page", "ps": "page_size", "ds": "scope", "s": "sort"}),
    "/patent/base": ("patent_detail", {"id": "patent_id"}),
    "/patent/claims": ("patent_claims", {"id": "patent_id"}),
    "/patent/desc": ("patent_description", {"id": "patent_id"}),
    "/patent/tx": ("patent_legal", {"id": "patent_id"}),
    "/patent/like": ("patent_similar", {"id": "patent_id"}),
    "/patent/family": ("patent_family", {"id": "patent_id"}),
    "/patent/citing": ("patent_citations", {"id": "patent_id"}),
    "/ration/analysis": ("patent_analysis", {"q": "query", "field": "dimension", "ds": "scope", "size": "size"}),
    "/a/portrait": ("patent_company", {"en": "company"}),
}


def call_legacy_api(client: PatentMcpClient, endpoint: str, params: dict, method: str) -> dict:
    """Keep the existing mchat node/result format while replacing the transport."""
    spec = _ENDPOINTS.get("/" + endpoint.lstrip("/"))
    if method.upper() != "GET" or spec is None:
        return {"success": False, "code": 210, "message": "此功能尚未提供 MCP 工具，可显式选择 REST 模式"}
    name, mapping = spec
    args = {target: params[source] for source, target in mapping.items() if params.get(source) is not None}
    if name == "patent_search" and "page_size" in args:
        args["page_size"] = min(50, max(1, int(args["page_size"])))
    try:
        return client.call(name, args)
    except McpError as error:
        return {"success": False, "errorCode": error.code or 503, "message": str(error),
                "outcome_uncertain": error.uncertain}
