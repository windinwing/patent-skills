import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from email.message import Message
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "patent-search"))
sys.path.insert(0, str(ROOT / "patent-harness"))
from patent_mcp import PatentMcpClient, McpError, call_legacy_api
from harness import execute, validate_plan


class Response(io.BytesIO):
    status = 200
    def __init__(self, data, content_type="application/json"):
        super().__init__(data)
        self.headers = Message()
        self.headers["Content-Type"] = content_type


class Transport:
    def __init__(self): self.requests = []; self.fail = False
    def open(self, req, timeout):
        body = json.loads(req.data)
        self.requests.append((req, body))
        method = body["method"]
        if method == "notifications/initialized":
            response = Response(b""); response.status = 202; return response
        if method == "tools/call" and self.fail:
            raise urllib.error.URLError("secret URL must not be echoed")
        result = {"protocolVersion": "2025-06-18"} if method == "initialize" else {"tools": []}
        if method == "tools/call":
            result = {"isError": False, "structuredContent": {"success": True, "patents": [{"id": "CN112968234A"}]}}
        return Response(json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": result}).encode())


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = PatentMcpClient("test-token-only")
        self.transport = Transport(); self.client._opener = self.transport

    def test_handshake_and_header_only_auth(self):
        self.assertTrue(self.client.call("patent_search", {"query": "电池"})["success"])
        self.assertEqual([b["method"] for _, b in self.transport.requests], ["initialize", "notifications/initialized", "tools/call"])
        for req, body in self.transport.requests:
            self.assertEqual(req.get_header("Authorization"), "Bearer test-token-only")
            self.assertNotIn("test-token-only", req.full_url)
            self.assertNotIn("test-token-only", json.dumps(body))

    def test_timeout_never_retries_or_leaks_error(self):
        self.transport.fail = True
        with self.assertRaises(McpError) as caught:
            self.client.call("patent_search", {"query": "电池"})
        self.assertTrue(caught.exception.uncertain)
        self.assertNotIn("secret", str(caught.exception))
        self.assertEqual(sum(b["method"] == "tools/call" for _, b in self.transport.requests), 1)

    def test_endpoint_validation(self):
        for endpoint in ("http://example.com/mcp", "https://example.com/mcp?token=secret", "https://user:pass@example.com/mcp"):
            with self.assertRaises(ValueError): PatentMcpClient("test", endpoint)

    def test_legacy_mapping_preserves_result_shape(self):
        result = call_legacy_api(self.client, "/ration/analysis", {"q": "电池", "field": "applicant", "column": "trend", "ipcLevel": "3"}, "GET")
        self.assertTrue(result["success"])
        params = self.transport.requests[-1][1]["params"]
        self.assertEqual(params, {"name": "patent_analysis", "arguments": {"query": "电池", "dimension": "applicant"}})
        count = len(self.transport.requests)
        self.assertFalse(call_legacy_api(self.client, "/tm/s", {}, "GET")["success"])
        self.assertEqual(count, len(self.transport.requests))

    def test_existing_patent_api_uses_selected_transport(self):
        from patent_api import PatentAPI
        with patch.dict(os.environ, {"PATENT_TRANSPORT": "mcp"}):
            api = PatentAPI(token="test-token-only", config={"show_patent_images": False})
        api._mcp_client = self.client
        self.assertTrue(api.search("电池")["success"])
        self.assertEqual(self.transport.requests[-1][1]["params"]["name"], "patent_search")


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.plan = {"version": 1, "steps": [
            {"id": "search", "tool": "patent_search", "arguments": {"query": "电池"}},
            {"id": "detail", "tool": "patent_detail", "arguments": {"patent_id": {"$ref": "search#/patents/0/id"}}}]}
        class Client:
            token = "test-token-only"; endpoint = "https://www.9235.net/api/mcp"
            def __init__(self): self.calls = []; self.fail = False
            def call(self, name, args):
                self.calls.append((name, args))
                if self.fail and name == "patent_detail": raise McpError("timeout", uncertain=True)
                return {"success": True, "patents": [{"id": "CN112968234A"}]}
        self.client = Client()

    def test_references_and_successful_resume_do_not_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = execute(self.plan, Path(tmp), self.client, max_calls=2)
            self.assertEqual(state["status"], "succeeded")
            self.assertEqual(self.client.calls[1][1], {"patent_id": "CN112968234A"})
            execute(self.plan, Path(tmp), self.client, max_calls=2, resume=True)
            self.assertEqual(len(self.client.calls), 2)
            self.assertNotIn(self.client.token, (Path(tmp) / "checkpoint.json").read_text())

    def test_uncertain_call_requires_explicit_retry_and_keeps_completed_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.client.fail = True
            state = execute(self.plan, Path(tmp), self.client, max_calls=3)
            self.assertEqual(state["status"], "uncertain")
            with self.assertRaises(ValueError): execute(self.plan, Path(tmp), self.client, max_calls=3, resume=True)
            self.assertEqual(len(self.client.calls), 2)
            self.client.fail = False
            execute(self.plan, Path(tmp), self.client, max_calls=3, resume=True, retry_failed=True)
            self.assertEqual([name for name, _ in self.client.calls], ["patent_search", "patent_detail", "patent_detail"])

    def test_budget_and_changed_plan_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): execute(self.plan, Path(tmp), self.client, max_calls=1)
            self.assertEqual(self.client.calls, [])
            execute(self.plan, Path(tmp), self.client, max_calls=2)
            self.plan["steps"][0]["arguments"]["query"] = "不同查询"
            with self.assertRaises(ValueError): execute(self.plan, Path(tmp), self.client, resume=True)
            self.assertEqual(len(self.client.calls), 2)

    def test_invalid_reference_does_not_trigger_next_network_call(self):
        self.plan["steps"][1]["arguments"]["patent_id"]["$ref"] = "search#/patents/99/id"
        with tempfile.TemporaryDirectory() as tmp:
            state = execute(self.plan, Path(tmp), self.client)
            self.assertEqual(state["status"], "failed"); self.assertEqual(len(self.client.calls), 1)

    def test_forward_reference_is_rejected_before_running(self):
        self.plan["steps"][0]["arguments"] = {"query": {"$ref": "detail#/title"}}
        with self.assertRaises(ValueError): validate_plan(self.plan)


if __name__ == "__main__": unittest.main()
