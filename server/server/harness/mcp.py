"""Minimal MCP (Model Context Protocol) server, dependency-free.

Implements the JSON-RPC 2.0 subset an MCP *tools* server needs — ``initialize``,
``notifications/initialized``, ``ping``, ``tools/list``, ``tools/call`` — over
whatever transport the caller wires up (stdio in ``server/mcp_server.py``). Tool
schemas come from the OpenAPI spec via :class:`OpenApiToolset`, and tool calls
are dispatched to the HTTP API. Keeping ``MCPServer.handle`` pure makes the whole
interface unit-testable without real stdio or network.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional, Tuple

from .openapi_mcp import OpenApiToolset

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "neoscaffold"

# A tool caller takes (tool_name, arguments) and returns
# {"text": <str>, "isError": <bool>}.
ToolCaller = Callable[[str, Dict[str, Any]], Dict[str, Any]]
# An HTTP call takes (method, path, query, body) and returns (status, text).
HttpCall = Callable[[str, str, Dict[str, Any], Optional[Dict[str, Any]]], Tuple[int, str]]


def _response(msg_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def make_http_tool_caller(toolset: OpenApiToolset, http_call: HttpCall) -> ToolCaller:
    """Build a tool caller that resolves a tool to an HTTP request and runs it."""

    def caller(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        method, path, query, body = toolset.resolve(name, arguments)
        status, text = http_call(method, path, query, body)
        return {"text": text, "isError": status >= 400}

    return caller


class MCPServer:
    """Handles MCP JSON-RPC messages against an OpenAPI-derived toolset."""

    def __init__(
        self,
        toolset: OpenApiToolset,
        tool_caller: ToolCaller,
        *,
        server_version: str = "1.0.0",
    ):
        self.toolset = toolset
        self.tool_caller = tool_caller
        self.server_version = server_version

    def handle(self, message: Any) -> Optional[Dict[str, Any]]:
        """Handle one JSON-RPC message. Returns a response, or None for notifications."""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            msg_id = message.get("id") if isinstance(message, dict) else None
            return _error(msg_id, -32600, "Invalid Request")

        method = message.get("method")
        msg_id = message.get("id")
        is_notification = "id" not in message
        params = message.get("params") or {}

        if method == "initialize":
            return _response(
                msg_id,
                {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {"listChanged": False}},
                    "serverInfo": {"name": SERVER_NAME, "version": self.server_version},
                },
            )

        if method in ("notifications/initialized", "initialized"):
            return None

        if method == "ping":
            return _response(msg_id, {})

        if method == "tools/list":
            return _response(msg_id, {"tools": self.toolset.tools()})

        if method == "tools/call":
            name = params.get("name")
            arguments = params.get("arguments") or {}
            if not name or not self.toolset.has_tool(name):
                return _error(msg_id, -32602, f"unknown tool '{name}'")
            try:
                outcome = self.tool_caller(name, arguments)
            except Exception as exc:  # surface tool failures as MCP tool errors
                return _response(
                    msg_id,
                    {"content": [{"type": "text", "text": f"error: {exc}"}], "isError": True},
                )
            return _response(
                msg_id,
                {
                    "content": [{"type": "text", "text": outcome.get("text", "")}],
                    "isError": bool(outcome.get("isError", False)),
                },
            )

        if is_notification:
            return None
        return _error(msg_id, -32601, f"method not found: {method}")

    def handle_line(self, line: str) -> Optional[str]:
        """Handle one newline-delimited JSON message; return serialized response."""
        line = line.strip()
        if not line:
            return None
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            return json.dumps(_error(None, -32700, "Parse error"))
        response = self.handle(message)
        return None if response is None else json.dumps(response)
