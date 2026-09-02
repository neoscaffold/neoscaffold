"""Integration tests for the v1 HTTP routes using an aiohttp test client."""

import asyncio
from argparse import Namespace

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from server.infrastructure.servers.server import Server


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
            assert body["source"] in ("offline", "offline_fallback")
            # metrics should now report at least one build
            metrics = await (await client.get("/v1/metrics")).text()
            assert "neoscaffold_graph_build_total" in metrics
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
