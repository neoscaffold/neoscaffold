#!/usr/bin/env python
"""Runnable MCP (Model Context Protocol) server for NeoScaffold.

Speaks the MCP JSON-RPC subset over stdio (newline-delimited JSON) and proxies
tool calls to a running NeoScaffold HTTP server. Tools are derived from the
OpenAPI spec, so external agents (Claude Desktop, Cursor, etc.) can build
graphs, run prompts, list extensions, and read metrics/health.

Usage:
    NEOSCAFFOLD_URL=http://localhost:6166 python mcp_server.py

Configure it in an MCP client as a stdio server running this script.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

# Allow running as a script (python mcp_server.py) from the server/ directory.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from server.harness.mcp import MCPServer, make_http_tool_caller  # noqa: E402
from server.harness.openapi import build_openapi_spec  # noqa: E402
from server.harness.openapi_mcp import OpenApiToolset  # noqa: E402

BASE_URL = os.environ.get("NEOSCAFFOLD_URL", "http://localhost:6166").rstrip("/")


def http_call(
    method: str, path: str, query: Dict[str, Any], body: Optional[Dict[str, Any]]
) -> Tuple[int, str]:
    url = BASE_URL + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        return 599, json.dumps({"error": f"cannot reach NeoScaffold at {BASE_URL}: {exc}"})


def build_server() -> MCPServer:
    spec = build_openapi_spec()
    toolset = OpenApiToolset(spec)
    version = spec.get("info", {}).get("version", "1.0.0")
    return MCPServer(
        toolset,
        make_http_tool_caller(toolset, http_call),
        server_version=version,
    )


def main() -> int:
    server = build_server()
    for line in sys.stdin:
        response = server.handle_line(line)
        if response is not None:
            sys.stdout.write(response + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
