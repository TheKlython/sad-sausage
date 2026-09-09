"""
test_sad_sausage_mcp.py
=======================
Automated unit tests for the Model Context Protocol (MCP) Server `sad_sausage_mcp.py`.

GUIDANCE FOR AI AGENTS & DEVELOPERS:
-------------------------------------
- Verifies:
  1. MCP Handshake (`initialize`, `notifications/initialized`, `ping`)
  2. Tool discovery (`tools/list` across real ops tools)
  3. Tool execution:
     - `get_agent_status`
     - `get_donation_info`
     - `get_telemetry_summary`
     - `validate_manifest_integrity`
  4. Error handling (invalid JSON-RPC, missing methods, unknown tools)
  5. Subprocess stdio pipe integration (real end-to-end execution)
- Execution: `python -m unittest test_sad_sausage_mcp.py`
"""

import json
import subprocess
import sys
import unittest
from typing import Any, Dict

import sad_sausage_mcp
from validate_manifest import EXPECTED_SUPPORT_URL


class TestSadSausageMCPServer(unittest.TestCase):
    """
    Unit test suite for the JSON-RPC / MCP functionality of the Sad Sausage server.
    """

    def _call_rpc(self, method: str, params: Dict[str, Any] = None, req_id: int = 1) -> Dict[str, Any]:
        """
        Helper method to construct and process a JSON-RPC request.
        """
        req = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method
        }
        if params is not None:
            req["params"] = params
        return sad_sausage_mcp.process_jsonrpc_request(req)

    # 1. MCP Handshake Tests
    def test_initialize_handshake(self):
        """
        Tests the standard MCP initialization handshake.
        """
        resp = self._call_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        })
        self.assertIsNotNone(resp)
        self.assertEqual(resp.get("id"), 1)
        result = resp.get("result", {})
        self.assertEqual(result.get("protocolVersion"), "2024-11-05")
        self.assertEqual(result.get("serverInfo", {}).get("name"), "sad-sausage-mcp")
        self.assertIn("tools", result.get("capabilities", {}))

    def test_notifications_initialized(self):
        """
        Tests that 'notifications/initialized' produces no response (MCP specification).
        """
        req = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        resp = sad_sausage_mcp.process_jsonrpc_request(req)
        self.assertIsNone(resp, "Notifications must not produce a JSON-RPC response.")

    def test_ping(self):
        """
        Tests MCP ping command.
        """
        resp = self._call_rpc("ping")
        self.assertIsNotNone(resp)
        self.assertEqual(resp.get("result"), {})

    # 2. Tools Discovery Tests
    def test_tools_list(self):
        """
        Tests that all 4 tools are exposed with valid input schemas.
        """
        resp = self._call_rpc("tools/list")
        self.assertIsNotNone(resp)
        tools = resp.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        
        expected_tools = [
            "get_agent_status",
            "get_donation_info",
            "get_telemetry_summary",
            "validate_manifest_integrity"
        ]
        for et in expected_tools:
            self.assertIn(et, tool_names, f"Tool '{et}' should be in tools/list.")

        for t in tools:
            self.assertIn("description", t)
            self.assertIn("inputSchema", t)
            self.assertEqual(t["inputSchema"].get("type"), "object")

    # 3. Tool Execution Tests
    def test_tool_get_agent_status(self):
        """
        Tests retrieval of agent status, real-world roles, and budget tiers.
        """
        resp = self._call_rpc("tools/call", {
            "name": "get_agent_status",
            "arguments": {}
        })
        self.assertIsNotNone(resp)
        result = resp.get("result", {})
        self.assertFalse(result.get("isError", True))
        content = result.get("content", [{}])[0].get("text", "")
        self.assertIn("[Sad Sausage Operations Agent] Node Status Report", content)
        self.assertIn("Sad Sausage (SS-Ops)", content)
        self.assertIn("Smart-Home", content)
        self.assertIn("2012", content)
        self.assertIn("Tier", content)
        self.assertIn("€", content)
        self.assertIn("Maintainer 30%", content)
        self.assertIn("Solar", content)
        self.assertIn("CO2", content)
        # Ensure no hotdog emojis or casual meme strings
        self.assertNotIn("🌭", content)

    def test_tool_get_donation_info(self):
        """
        Tests retrieval of donation/support details and transparent ledger link.
        """
        resp = self._call_rpc("tools/call", {
            "name": "get_donation_info",
            "arguments": {}
        })
        self.assertIsNotNone(resp)
        result = resp.get("result", {})
        self.assertFalse(result.get("isError", True))
        content = result.get("content", [{}])[0].get("text", "")
        self.assertIn("[Sad Sausage Operations Agent] Hardware Development Fund & Sponsorship", content)
        self.assertIn(EXPECTED_SUPPORT_URL, content)
        self.assertIn("Buy Me a Coffee", content)
        self.assertIn("Co-Investment Policy", content)
        self.assertIn("30%", content)
        self.assertIn("DONATIONS.md", content)
        self.assertNotIn("☕", content)

    def test_tool_get_telemetry_summary(self):
        """
        Tests retrieval of operational telemetry summary.
        """
        resp = self._call_rpc("tools/call", {
            "name": "get_telemetry_summary",
            "arguments": {}
        })
        self.assertIsNotNone(resp)
        result = resp.get("result", {})
        self.assertFalse(result.get("isError", True))
        content = result.get("content", [{}])[0].get("text", "")
        self.assertIn("[Sad Sausage Operations Agent] Telemetry Pipeline", content)
        self.assertIn("Home Assistant", content)
        self.assertIn("12GB VRAM", content)
        self.assertIn("solar", content.lower())
        self.assertIn("co2", content.lower())
        self.assertNotIn("📊", content)

    def test_tool_validate_manifest_integrity_success(self):
        """
        Tests manifest validation for the repository manifest.
        """
        resp = self._call_rpc("tools/call", {
            "name": "validate_manifest_integrity",
            "arguments": {}
        })
        result = resp.get("result", {})
        self.assertFalse(result.get("isError"))
        content = result.get("content", [{}])[0].get("text", "")
        self.assertIn("SUCCESS", content)

    def test_tool_validate_manifest_integrity_failure(self):
        """
        Tests rejection of a non-existent manifest file path.
        """
        resp = self._call_rpc("tools/call", {
            "name": "validate_manifest_integrity",
            "arguments": {"manifest_path": "does_not_exist_file.json"}
        })
        result = resp.get("result", {})
        self.assertTrue(result.get("isError"))
        content = result.get("content", [{}])[0].get("text", "")
        self.assertIn("FAILED", content)

    # 4. Error Handling Tests
    def test_unknown_method(self):
        """
        Tests JSON-RPC error response for an unknown method.
        """
        resp = self._call_rpc("unknown_method_xyz")
        self.assertIsNotNone(resp)
        self.assertEqual(resp.get("error", {}).get("code"), -32601)

    def test_unknown_tool(self):
        """
        Tests MCP error response when calling a non-existent tool.
        """
        resp = self._call_rpc("tools/call", {
            "name": "non_existent_tool_123",
            "arguments": {}
        })
        self.assertIsNotNone(resp)
        self.assertEqual(resp.get("error", {}).get("code"), -32601)

    def test_missing_method(self):
        """
        Tests request missing a method parameter.
        """
        req = {"jsonrpc": "2.0", "id": 99}
        resp = sad_sausage_mcp.process_jsonrpc_request(req)
        self.assertIsNotNone(resp)
        self.assertEqual(resp.get("error", {}).get("code"), -32600)


class TestSadSausageStdioIntegration(unittest.TestCase):
    """
    End-to-end integration test: spawns the MCP server as a real subprocess
    and verifies bidirectional communication via stdin/stdout and JSON-RPC 2.0.
    """

    def test_subprocess_stdio_pipeline(self):
        """
        Tests actual stdio communication with the running MCP server subprocess.
        """
        proc = subprocess.Popen(
            [sys.executable, "sad_sausage_mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=sad_sausage_mcp.BASE_DIR
        )

        req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_donation_info",
                "arguments": {}
            }
        }
        stdout_data, stderr_data = proc.communicate(input=json.dumps(req) + "\n", timeout=5)
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(len(stdout_data.strip()) > 0)

        response = json.loads(stdout_data.strip())
        self.assertEqual(response.get("id"), 1)
        self.assertFalse(response.get("result", {}).get("isError"))
        content_text = response["result"]["content"][0]["text"]
        self.assertIn(EXPECTED_SUPPORT_URL, content_text)


if __name__ == "__main__":
    unittest.main()
