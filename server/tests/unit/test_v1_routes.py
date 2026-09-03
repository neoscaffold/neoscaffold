"""Integration tests for the v1 HTTP routes using an aiohttp test client."""

import asyncio
import os
from argparse import Namespace

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from server.infrastructure.apis.v1_routes import _layout
from server.infrastructure.servers.server import Server

# Keep build-graph deterministic in CI even if OPENAI_API_KEY is present.
os.environ["NEOSCAFFOLD_GRAPH_OFFLINE"] = "1"


def _assert_layout_follows_execution(prompt, layout):
    for node_id, node in prompt.items():
        target_pos = layout[str(node_id)]
        for value in (node.get("inputs") or {}).values():
            if not (isinstance(value, dict) and value.get("originId")):
                continue
            origin = str(value["originId"])
            if origin not in layout:
                continue
            origin_pos = layout[origin]
            is_left = origin_pos[0] < target_pos[0]
            is_above = origin_pos[1] < target_pos[1]
            assert is_left or is_above, (
                f"{origin} should sit left of or above {node_id}"
            )


def _make_server_app():
    args = Namespace(
        enable_cors_header="*",
        enable_smart_cache=False,
        inspection_delay=0,
        enable_parallel_execution=False,
        max_parallel_nodes=8,
        max_upload_size=100,
    )
    loop = asyncio.get_event_loop()
    server = Server(loop=loop, args=args)
    server.load_extensions()
    server.add_routes()
    return server


@pytest.fixture
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


def _run(loop, coro):
    return loop.run_until_complete(coro)


async def _client(server):
    client = TestClient(TestServer(server.app))
    await client.start_server()
    return client


def test_healthz(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.get("/v1/healthz")
            assert resp.status == 200
            body = await resp.json()
            assert body["status"] == "ok"
            assert body["version"] == "1.0.0"
            assert body["nodes"] > 0
        finally:
            await client.close()

    _run(loop, go())


def test_metrics_exposition(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.get("/v1/metrics")
            assert resp.status == 200
            assert resp.content_type == "text/plain"
        finally:
            await client.close()

    _run(loop, go())


def test_build_graph_endpoint_returns_valid_prompt(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.post(
                "/v1/agent/build-graph", json={"prompt": 'log "endpoint works"'}
            )
            assert resp.status == 200
            body = await resp.json()
            assert "prompt" in body and body["prompt"]
            types = [n["type"] for n in body["prompt"].values()]
            assert "ConsoleLog" in types
            assert "layout" in body
            assert set(body["layout"]) == set(body["prompt"])
            _assert_layout_follows_execution(body["prompt"], body["layout"])
            assert body["source"] in ("offline", "offline_fallback")
            # metrics should now report at least one build
            metrics = await (await client.get("/v1/metrics")).text()
            assert "neoscaffold_graph_build_total" in metrics
        finally:
            await client.close()

    _run(loop, go())


def test_build_graph_endpoint_returns_widget_edits(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.post(
                "/v1/agent/build-graph",
                json={
                    "prompt": 'set the prompt of CerebrasAgent to "paint a mural"',
                    "canvas": {
                        "15": {
                            "type": "CerebrasAgent",
                            "name": "CerebrasAgent",
                            "widgets": {"api_key": "", "prompt": "old"},
                        }
                    },
                },
            )
            assert resp.status == 200
            body = await resp.json()
            assert body["widget_edits"]
            assert body["widget_edits"][0]["widget"] == "prompt"
            assert body["widget_edits"][0]["value"] == "paint a mural"
            assert "thoughts" in body
        finally:
            await client.close()

    _run(loop, go())


def test_build_graph_rejects_empty_prompt(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.post("/v1/agent/build-graph", json={"prompt": "  "})
            assert resp.status == 400
        finally:
            await client.close()

    _run(loop, go())


def test_openapi_endpoint(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.get("/v1/openapi.json")
            assert resp.status == 200
            spec = await resp.json()
            assert spec["openapi"].startswith("3.")
            assert "/v1/agent/build-graph" in spec["paths"]
            assert "/v1/agent/suggest-fix" in spec["paths"]
        finally:
            await client.close()

    _run(loop, go())


def test_mcp_tools_endpoint(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            resp = await client.get("/v1/mcp/tools")
            assert resp.status == 200
            body = await resp.json()
            names = {t["name"] for t in body["tools"]}
            assert "buildGraph" in names
            assert "runPrompt" in names
            assert "importWorkflow" in names
            assert "exportWorkflow" in names
            assert "suggestFix" in names
        finally:
            await client.close()

    _run(loop, go())


def test_agent_events_endpoint_reflects_builds(loop):
    server = _make_server_app()

    async def go():
        client = await _client(server)
        try:
            # trigger a build so at least one agent event exists
            await client.post("/v1/agent/build-graph", json={"prompt": 'log "events"'})
            resp = await client.get("/v1/agent/events?limit=50")
            assert resp.status == 200
            body = await resp.json()
            kinds = [e["kind"] for e in body["events"]]
            assert "graph_build" in kinds
        finally:
            await client.close()

    _run(loop, go())


def test_suggest_fix_endpoint_arms_loop_body_patch(loop):
    server = _make_server_app()
    prompt = {
        "3": {
            "type": "ConcatString",
            "name": "Combine Poems",
            "inputs": {"a": "hello", "b": "world"},
        },
        "4": {"type": "ForLoop", "name": "Loop 3 Times", "inputs": {"start": 0, "stop": 3}},
        "7": {"type": "EndForLoop", "name": "End Loop", "inputs": {"ForLoop": {"originId": "4"}}},
    }

    async def go():
        client = await _client(server)
        try:
            resp = await client.post(
                "/v1/agent/suggest-fix",
                json={
                    "error": (
                        "Exception: At least one node should be connected to "
                        "this loop other than EndForLoop"
                    ),
                    "node_id": "4",
                    "prompt": prompt,
                },
            )
            assert resp.status == 200
            body = await resp.json()
            assert body["armed"] is True
            assert "PassThrough" in body["ask"]
            patch = body["patch"]
            added = list(patch["add_nodes"].values())
            assert added and added[0]["type"] == "PassThrough"
            assert added[0]["inputs"]["ignored_input"] == {"originId": "4"}
            assert added[0]["inputs"]["value"] == {"originId": "3"}
            assert any(
                edge["target"] == "7" and edge["input"] == "node_inputs"
                for edge in patch["wire"]
            )
        finally:
            await client.close()

    _run(loop, go())


def test_layout_places_pipeline_left_to_right_in_execution_order():
    prompt = {
        "1": {"type": "nsString", "inputs": {"text": "hello"}},
        "2": {"type": "ConsoleLog", "inputs": {"any": {"originId": "1"}}},
    }
    layout = _layout(prompt)
    assert layout["1"][0] < layout["2"][0]
    assert layout["1"][1] == layout["2"][1]


def test_layout_places_parallel_branches_left_to_right_then_down():
    prompt = {
        "1": {"type": "CerebrasAgent", "inputs": {"prompt": "a"}},
        "2": {"type": "CerebrasAgent", "inputs": {"prompt": "b"}},
        "5": {"type": "ValuePath", "inputs": {"object": {"originId": "1"}}},
        "6": {"type": "ValuePath", "inputs": {"object": {"originId": "2"}}},
        "3": {
            "type": "ConcatString",
            "inputs": {"a": {"originId": "5"}, "b": {"originId": "6"}},
        },
        "4": {"type": "ConsoleLog", "inputs": {"any": {"originId": "3"}}},
    }
    layout = _layout(prompt)
    _assert_layout_follows_execution(prompt, layout)
    # Sources share the top row, left to right.
    assert layout["1"][1] == layout["2"][1]
    assert layout["1"][0] < layout["2"][0]
    # Later stages move down; aligned under their upstream branch.
    assert layout["5"][1] > layout["1"][1]
    assert layout["6"][1] == layout["5"][1]
    assert layout["5"][0] == layout["1"][0]
    assert layout["6"][0] == layout["2"][0]
    assert layout["3"][1] > layout["5"][1]
    assert layout["4"][1] > layout["3"][1]


def test_layout_wraps_disconnected_nodes_left_to_right():
    prompt = {
        "1": {"type": "nsString", "inputs": {"text": "a"}},
        "2": {"type": "nsString", "inputs": {"text": "b"}},
        "3": {"type": "nsString", "inputs": {"text": "c"}},
        "4": {"type": "nsString", "inputs": {"text": "d"}},
    }
    layout = _layout(prompt)
    assert layout["1"][1] == layout["2"][1] == layout["3"][1] == layout["4"][1]
    assert layout["1"][0] < layout["2"][0] < layout["3"][0] < layout["4"][0]
