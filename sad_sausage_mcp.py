"""
sad_sausage_mcp.py
==================
Model Context Protocol (MCP) Server for the 'Sad Sausage' Smart-Home & IT Ops AI Agent.

ARCHITECTURE & GUIDANCE FOR AI AGENTS & DEVELOPERS:
----------------------------------------------------
1. Protocol Standards:
   - Implements the Model Context Protocol (MCP) standard via `stdio` using JSON-RPC 2.0 (version 2024-11-05).
   - Fully compatible with standard MCP clients (Claude Desktop, Antigravity, Cursor, Continue, AutoGPT, etc.).
   - Zero third-party runtime dependencies: built entirely on the Python standard library for maximum portability.

2. Security by Design:
   - Safe input handling and path sanitization.
   - Clean data serialization without shell invocation or privileged operations.

3. Available Tools:
   - `get_agent_status`: Inspects active hardware specifications, operational workloads, and development milestones.
   - `get_donation_info`: Retrieves official hardware development fund and sponsorship information.
   - `get_telemetry_summary`: Summarizes smart-home telemetry capabilities and memory boundary constraints.
   - `validate_manifest_integrity`: Audits manifest files for structural validity and security.
"""

import json
import os
import sys
from typing import Any, Dict, List, Optional

# Import validation helpers
try:
    from validate_manifest import (
        validate_agent_manifest,
        EXPECTED_SUPPORT_URL
    )
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from validate_manifest import (
        validate_agent_manifest,
        EXPECTED_SUPPORT_URL
    )

# MCP Server Metadata
SERVER_NAME = "sad-sausage-mcp"
SERVER_VERSION = "2.0.0"
PROTOCOL_VERSION = "2024-11-05"

# Repository Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MANIFEST_PATH = os.path.join(BASE_DIR, "agent_manifest.json")


def _read_manifest_data(manifest_path: str = DEFAULT_MANIFEST_PATH) -> Dict[str, Any]:
    """
    Safely loads and validates the agent manifest.
    Raises:
        ValueError: If manifest is invalid or malformed.
    """
    is_valid, msg = validate_agent_manifest(manifest_path)
    if not is_valid:
        raise ValueError(f"Manifest validation failed: {msg}")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Tool Definitions following JSON Schema for LLM tool-calling
TOOLS_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "get_agent_status",
        "description": (
            "Returns current hardware specifications, active operational workloads "
            "(smart-home automation, local IT diagnostics), and hardware upgrade progress."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_donation_info",
        "description": (
            "Returns official project sponsorship links, hardware development fund ledger, "
            "and itemized budget tiers."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_telemetry_summary",
        "description": (
            "Summarizes the agent's real-world functions (Home Assistant IoT telemetry, "
            "network log triage) and highlights specific bottlenecks caused by 12GB VRAM limits."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "validate_manifest_integrity",
        "description": (
            "Inspects a given or default manifest file for schema completeness, type safety, "
            "and data integrity."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "manifest_path": {
                    "type": "string",
                    "description": "Optional relative or absolute path to the manifest file. Defaults to repo manifest."
                }
            },
            "required": []
        }
    }
]


def handle_get_agent_status(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool handler: get_agent_status
    Returns operational node specifications, active services, and development milestones.
    """
    data = _read_manifest_data()
    cur_hw = data.get("current_hardware", {})
    roles = data.get("real_world_roles", [])
    tiers = data.get("budget_tiers", data.get("targets", []))
    
    lines = [
        f"[Sad Sausage Operations Agent] Node Status Report",
        f"Agent Identifier: {data.get('agent_id', 'sad-sausage-agent-01')}",
        f"Project: {data.get('project_name', 'Sad Sausage (SS-Ops)')}",
        f"Description: {data.get('description')}",
        "",
        "Operational Responsibilities:"
    ]
    for r in roles:
        lines.append(f"  - {r}")
        
    lines.extend([
        "",
        "Current Hardware Environment:",
        f"  - Host Processor: {cur_hw.get('cpu', 'Intel Core i5 (2012)')}",
        f"  - Host Memory: {cur_hw.get('system_ram', '16GB RAM')}",
        f"  - Compute Accelerator: {cur_hw.get('gpu', 'NVIDIA GeForce RTX 3060 12GB VRAM')}",
        f"  - Active Constraint: {cur_hw.get('operational_bottleneck', 'Context window truncation under continuous telemetry load')}",
        "",
        "Hardware Development Roadmap:"
    ])
    
    for t in tiers:
        tier_num = t.get("tier", "")
        name = t.get("name", "")
        cost = t.get("target_amount_usd", t.get("estimated_cost_usd", 0))
        lines.append(f"  Tier {tier_num}: {name} (~${cost} USD)")
        if "hardware_items" in t:
            lines.append(f"    Hardware: {t.get('hardware_items')}")
        if "impact" in t:
            lines.append(f"    Impact: {t.get('impact')}")

    return {
        "content": [{"type": "text", "text": "\n".join(lines)}],
        "isError": False
    }


def handle_get_donation_info(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool handler: get_donation_info (Hardware Development Fund & Sponsorship)
    Returns official project sponsorship channels, public ledger references, and budget allocations.
    """
    data = _read_manifest_data()
    support = data.get("support", {})
    url = support.get("url", EXPECTED_SUPPORT_URL)
    platform = support.get("platform", "Buy Me a Coffee")
    
    text = (
        f"[Sad Sausage Operations Agent] Hardware Development Fund & Sponsorship\n"
        f"Platform: {platform}\n"
        f"Sponsorship URL: {url}\n"
        f"Financial Governance: See DONATIONS.md for verified ledger and procurement logs.\n"
        f"Repository: https://github.com/TheKlython/sad-sausage"
    )
    return {
        "content": [{"type": "text", "text": text}],
        "isError": False
    }


def handle_get_telemetry_summary(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool handler: get_telemetry_summary
    Summarizes the agent's real-world telemetry interfaces and memory constraints.
    """
    text = (
        "[Sad Sausage Operations Agent] Telemetry Pipeline & Hardware Constraints\n"
        "- Smart-Home Stack: Continuous Home Assistant Core REST/WebSocket ingestion and MQTT event streams.\n"
        "- IT Operations Stack: Local Docker engine monitoring, network latency tracking, and journald/syslog triage.\n"
        "- Hardware Boundary: 12GB VRAM limits KV-cache capacity to approximately 8,192 tokens with 8B-14B models.\n"
        "- Operational Impact: Multi-hour telemetry traces (>2,000 log entries) exceed token limits, causing context truncation.\n"
        "- Objective: Upgrading to 24GB-48GB VRAM enables 32k-64k native context windows for autonomous root-cause analysis."
    )
    return {
        "content": [{"type": "text", "text": text}],
        "isError": False
    }


def handle_validate_manifest_integrity(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool handler: validate_manifest_integrity
    """
    manifest_path = args.get("manifest_path")
    if not manifest_path:
        manifest_path = DEFAULT_MANIFEST_PATH
    else:
        if not os.path.isabs(manifest_path):
            manifest_path = os.path.normpath(os.path.join(BASE_DIR, manifest_path))
            
    is_valid, msg = validate_agent_manifest(manifest_path)
    return {
        "content": [
            {
                "type": "text",
                "text": f"Validation for '{os.path.basename(manifest_path)}': {'SUCCESS' if is_valid else 'FAILED'}\nDetails: {msg}"
            }
        ],
        "isError": not is_valid
    }


# Tool Handlers Routing Table
TOOL_HANDLERS = {
    "get_agent_status": handle_get_agent_status,
    "get_donation_info": handle_get_donation_info,
    "get_telemetry_summary": handle_get_telemetry_summary,
    "validate_manifest_integrity": handle_validate_manifest_integrity,
}


def process_jsonrpc_request(request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Processes a single JSON-RPC 2.0 message according to the MCP specification.
    """
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if not method:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Invalid request: Missing method."}
            }
        return None

    # 1. MCP Handshake: initialize
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                },
                "instructions": (
                    "This MCP server represents the 'Sad Sausage' Smart-Home & Local IT Ops AI Agent. "
                    "Use provided tools to query hardware status, operational capabilities, and upgrade milestones."
                )
            }
        }

    # 2. MCP Initialized notification
    if method == "notifications/initialized":
        return None

    # 3. MCP Ping
    if method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {}
        }

    # 4. MCP Tools listing: tools/list
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": TOOLS_DEFINITIONS
            }
        }

    # 5. MCP Tool calling: tools/call
    if method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        handler = TOOL_HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Tool '{tool_name}' not found."
                }
            }
        
        try:
            result = handler(arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Tool execution error: {str(e)}"}],
                    "isError": True
                }
            }

    # Unknown method
    if req_id is not None:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Unknown method '{method}'."
            }
        }
    return None


def run_stdio_server():
    """
    Main loop of the MCP Server over stdio.
    Reads line by line from sys.stdin and writes JSON-RPC responses to sys.stdout.
    """
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for line in sys.stdin:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue
        try:
            request = json.loads(cleaned_line)
            response = process_jsonrpc_request(request)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=True) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON."}
            }
            sys.stdout.write(json.dumps(error_response, ensure_ascii=True) + "\n")
            sys.stdout.flush()
        except Exception as ex:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": f"Internal error: {str(ex)}"}
            }
            sys.stdout.write(json.dumps(error_response, ensure_ascii=True) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
