#!/usr/bin/env python3
"""
Composio MCP CLI Utility
Provides command-line interaction with Composio MCP Remote Server (https://connect.composio.dev/mcp).
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error
import ssl

DEFAULT_SERVER_URL = "https://connect.composio.dev/mcp"
DEFAULT_ENV_FILE = "/Users/malcolm/.gemini/config/composio.env"

def load_api_key():
    key = os.environ.get("COMPOSIO_API_KEY")
    if key:
        return key
    if os.path.exists(DEFAULT_ENV_FILE):
        with open(DEFAULT_ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("COMPOSIO_API_KEY="):
                    return line.split("=", 1)[1].strip()
    # Fallback: read ~/.gemini/config/.env before failing
    global_env = "/Users/malcolm/.gemini/config/.env"
    if os.path.exists(global_env):
        with open(global_env, "r", encoding="utf-8") as f:
            for raw_line in f:
                s = raw_line.strip()
                if s.startswith("COMPOSIO_API_KEY="):
                    val = s.split("=", 1)[1].strip().strip("\"'")
                    if val:
                        return val
    raise RuntimeError("COMPOSIO_API_KEY not found in environment, ~/.gemini/config/.env, or composio.env")

def make_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def mcp_request(method, params=None, session_id=None, api_key=None, server_url=None):
    if not api_key:
        api_key = load_api_key()
    if not server_url:
        server_url = os.environ.get("COMPOSIO_MCP_SERVER_URL", DEFAULT_SERVER_URL)

    headers = {
        "x-consumer-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }

    req = urllib.request.Request(
        server_url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )

    ctx = make_ssl_context()
    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            resp_session_id = resp.headers.get("mcp-session-id") or session_id
            body_raw = resp.read().decode('utf-8')
            
            # Parse SSE format data: line if present
            json_data = body_raw
            if body_raw.startswith("event: message\ndata: "):
                json_data = body_raw.split("data: ", 1)[1].strip()
            elif "data: " in body_raw:
                parts = body_raw.split("data: ")
                json_data = parts[-1].strip()

            parsed = json.loads(json_data) if json_data else {"raw": body_raw}
            return {
                "status": resp.status,
                "session_id": resp_session_id,
                "data": parsed
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        return {
            "status": e.code,
            "error": err_body
        }
    except Exception as e:
        return {
            "status": 500,
            "error": str(e)
        }

def cmd_init(args):
    print("[+] Initializing session with Composio MCP server...")
    res = mcp_request("initialize", params={
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "antigravity-cli", "version": "1.0.0"}
    })
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(res, f, indent=2)
        print(f"[+] Output written to: {args.output}")
    else:
        print(json.dumps(res, indent=2))

def cmd_list_tools(args):
    print("[+] Fetching tools list from Composio MCP server...")
    # First initialize to get session_id
    init_res = mcp_request("initialize", params={
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "antigravity-cli", "version": "1.0.0"}
    })
    session_id = init_res.get("session_id")
    tools_res = mcp_request("tools/list", session_id=session_id)
    if args.output:
        with open(args.output, "w") as f:
            json.dump(tools_res, f, indent=2)
        print(f"[+] Output written to: {args.output}")
    else:
        print(json.dumps(tools_res, indent=2))

def cmd_get_schemas(args):
    slugs = args.slugs.split(",")
    print(f"[+] Fetching schemas for tool slugs: {slugs}...")
    init_res = mcp_request("initialize", params={
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "antigravity-cli", "version": "1.0.0"}
    })
    session_id = init_res.get("session_id")

    call_res = mcp_request("tools/call", session_id=session_id, params={
        "name": "COMPOSIO_GET_TOOL_SCHEMAS",
        "arguments": {
            "tool_slugs": slugs
        }
    })
    if args.output:
        with open(args.output, "w") as f:
            json.dump(call_res, f, indent=2)
        print(f"[+] Output written to: {args.output}")
    else:
        print(json.dumps(call_res, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Composio MCP Server Utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize Composio MCP session")
    init_parser.add_argument("--output", help="Output file path")
    init_parser.set_defaults(func=cmd_init)

    list_parser = subparsers.add_parser("list-tools", help="List available MCP tools")
    list_parser.add_argument("--output", help="Output file path")
    list_parser.set_defaults(func=cmd_list_tools)

    schema_parser = subparsers.add_parser("get-schemas", help="Get schemas for tool slugs")
    schema_parser.add_argument("--slugs", required=True, help="Comma-separated tool slugs (e.g. GMAIL_SEND_EMAIL)")
    schema_parser.add_argument("--output", help="Output file path")
    schema_parser.set_defaults(func=cmd_get_schemas)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
