"""Tests for the OpenAPI spec, the OpenAPI->MCP toolset, and the MCP server."""

import json

from server.harness.mcp import MCPServer, make_http_tool_caller
from server.harness.openapi import build_openapi_spec
from server.harness.openapi_mcp import OpenApiToolset


# --- OpenAPI spec ---
def test_openapi_spec_shape():
    spec = build_openapi_spec()
    assert spec["openapi"].startswith("3.")
    assert spec["info"]["title"] == "NeoScaffold API"
    paths = spec["paths"]
    for path in (
        "/v1/agent/build-graph",
        "/v1/agent/import-workflow",
        "/v1/agent/export-workflow",
        "/v1/agent/suggest-fix",
        "/prompt",
        "/extensions",
        "/v1/metrics",
        "/v1/healthz",
        "/v1/agent/events",
    ):
        assert path in paths, path
    # every operation has an operationId (required for MCP tool derivation)
    for path_item in paths.values():
        for method, operation in path_item.items():
            assert operation.get("operationId"), (method, operation)


# --- OpenAPI -> MCP tools ---
def test_toolset_lists_tools_from_operations():
    toolset = OpenApiToolset(build_openapi_spec())
    names = {t["name"] for t in toolset.tools()}
    assert {
        "buildGraph",
        "runPrompt",
        "listExtensions",
        "getMetrics",
        "getHealth",
        "getAgentEvents",
        "importWorkflow",
        "exportWorkflow",
        "suggestFix",
    } <= names
    for tool in toolset.tools():
        assert "description" in tool
        assert tool["inputSchema"]["type"] == "object"


def test_toolset_build_graph_input_schema_requires_prompt():
    toolset = OpenApiToolset(build_openapi_spec())
    build = next(t for t in toolset.tools() if t["name"] == "buildGraph")
    assert "prompt" in build["inputSchema"]["properties"]
    assert "prompt" in build["inputSchema"].get("required", [])


def test_toolset_resolve_post_body():
    toolset = OpenApiToolset(build_openapi_spec())
    method, path, query, body = toolset.resolve("buildGraph", {"prompt": "log x"})
    assert method == "post"
    assert path == "/v1/agent/build-graph"
    assert query == {}
    assert body == {"prompt": "log x"}


def test_toolset_resolve_get_query_param():
    toolset = OpenApiToolset(build_openapi_spec())
    method, path, query, body = toolset.resolve("getAgentEvents", {"limit": 5})
    assert method == "get"
    assert path == "/v1/agent/events"
    assert query == {"limit": 5}
    assert body is None


# --- MCP server protocol ---
def _server_with_fake_http(calls):
    toolset = OpenApiToolset(build_openapi_spec())

    def fake_http(method, path, query, body):
        calls.append((method, path, query, body))
        return 200, json.dumps({"ok": True, "path": path})

    return MCPServer(toolset, make_http_tool_caller(toolset, fake_http))


def test_mcp_initialize():
    server = _server_with_fake_http([])
    resp = server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "neoscaffold"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_initialized_notification_returns_none():
    server = _server_with_fake_http([])
    assert server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_mcp_tools_list():
    server = _server_with_fake_http([])
    resp = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in resp["result"]["tools"]}
    assert "buildGraph" in names


def test_mcp_tools_call_dispatches_http():
    calls = []
    server = _server_with_fake_http(calls)
    resp = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "buildGraph", "arguments": {"prompt": "log hi"}},
        }
    )
    assert resp["result"]["isError"] is False
    assert calls == [("post", "/v1/agent/build-graph", {}, {"prompt": "log hi"})]
    assert "path" in resp["result"]["content"][0]["text"]


def test_mcp_tools_call_unknown_tool():
    server = _server_with_fake_http([])
    resp = server.handle(
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "nope"}}
    )
    assert "error" in resp


def test_mcp_http_error_marks_is_error():
    toolset = OpenApiToolset(build_openapi_spec())

    def failing_http(method, path, query, body):
        return 422, json.dumps({"error": "bad"})

    server = MCPServer(toolset, make_http_tool_caller(toolset, failing_http))
    resp = server.handle(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "buildGraph", "arguments": {"prompt": "x"}},
        }
    )
    assert resp["result"]["isError"] is True


def test_mcp_unknown_method():
    server = _server_with_fake_http([])
    resp = server.handle({"jsonrpc": "2.0", "id": 6, "method": "does/not/exist"})
    assert resp["error"]["code"] == -32601


def test_mcp_handle_line_roundtrip():
    server = _server_with_fake_http([])
    out = server.handle_line('{"jsonrpc":"2.0","id":7,"method":"ping"}')
    assert json.loads(out)["id"] == 7


def test_mcp_handle_line_parse_error():
    server = _server_with_fake_http([])
    out = server.handle_line("not json")
    assert json.loads(out)["error"]["code"] == -32700


def test_runnable_mcp_server_builds():
    import mcp_server

    server = mcp_server.build_server()
    resp = server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = {t["name"] for t in resp["result"]["tools"]}
    assert "buildGraph" in names
