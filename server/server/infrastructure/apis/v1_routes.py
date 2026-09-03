"""Versioned v1 HTTP surface for NeoScaffold 1.0.0.

Additive, backward-compatible routes:

- ``POST /v1/agent/build-graph`` — natural language -> validated prompt-graph.
- ``GET  /v1/metrics``           — Prometheus text exposition (PromQL).
- ``GET  /v1/healthz``           — liveness + loaded node/extension counts.
"""

from aiohttp import web

from ...domain.services.graph_builder import GraphBuilder, make_openai_planner
from ...domain.utilities.authorize_user_and_get_info import authorize_user_and_get_info
from ...domain.utilities.fallback_json_encoder import dumps
from ...harness import observability
from ...harness.agent_events import AGENT_EVENTS
from ...harness.openapi import build_openapi_spec
from ...harness.openapi_mcp import OpenApiToolset
from ...harness.parsing import ParseError

VERSION = "1.0.0"


def _authorized_user(request):
    """Return ``(user_id, None)`` or ``(None, error_response)``."""
    info = authorize_user_and_get_info(request)
    if isinstance(info, web.Response):
        return None, info
    user_id = info.get("user_info", {}).get("user_id")
    if not user_id:
        return None, web.json_response({"error": "No user id"}, status=401)
    return user_id, None


# Node types that are pure sources/leaves; placed on an upper row so the wiring
# into the main pipeline row reads clearly.
_SOURCE_NODE_TYPES = {
    "nsString",
    "nsArray",
    "nsInteger",
    "nsFloat",
    "nsBoolean",
    "CerebrasAgent",
    "CerebrasAgentAsync",
    "PromptNode",
    "SwarmSolverNode",
}


def _layout(prompt):
    """Two-row left-to-right layout so wired edges are easy to see.

    Source/leaf nodes go on the top row, pipeline nodes (append/join/passthrough/
    log/...) on the main row, each advanced left-to-right in creation order.
    """
    layout = {}
    top_x = 120
    main_x = 120
    for node_id, node in prompt.items():
        node_type = (node or {}).get("type", "")
        if node_type in _SOURCE_NODE_TYPES:
            layout[node_id] = [top_x, 70]
            top_x += 220
        else:
            layout[node_id] = [main_x, 300]
            main_x += 260
    return layout


def v1_routes(server):
    routes = server.routes

    @routes.post("/v1/agent/build-graph")
    async def build_graph_route(request):
        user_id, error = _authorized_user(request)
        if error is not None:
            return error

        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid JSON body"}, status=400)

        prompt_text = data.get("prompt") if isinstance(data, dict) else None
        if not isinstance(prompt_text, str) or not prompt_text.strip():
            return web.json_response(
                {"error": "'prompt' must be a non-empty string"}, status=400
            )

        known_nodes = getattr(server, "nodes", {})
        builder = GraphBuilder(
            known_nodes=known_nodes,
            llm=make_openai_planner(known_nodes),
        )
        try:
            result = builder.build(prompt_text)
        except ParseError as exc:
            observability.inc("neoscaffold_graph_build_rejected_total", reason="parse")
            return web.json_response({"error": exc.message, "path": exc.path}, status=422)

        payload = {
            "prompt": result.prompt,
            "layout": _layout(result.prompt),
            "plan": result.plan,
            "warnings": result.warnings,
            "repairs": result.repairs,
            "source": result.source,
        }
        return web.json_response(payload, dumps=dumps)

    @routes.get("/v1/metrics")
    async def metrics_route(request):
        # Unauthenticated by design so a Prometheus scraper can reach it.
        return web.Response(text=observability.render(), content_type="text/plain")

    @routes.get("/v1/healthz")
    async def health_route(request):
        return web.json_response(
            {
                "status": "ok",
                "version": VERSION,
                "extensions": len(getattr(server, "extensions", {})),
                "nodes": len(getattr(server, "nodes", {})),
                "rules": len(getattr(server, "rules", {})),
            }
        )

    @routes.get("/v1/openapi.json")
    async def openapi_route(request):
        # The machine-readable contract other agents (and the MCP bridge) use.
        return web.json_response(build_openapi_spec(server))

    @routes.get("/v1/mcp/tools")
    async def mcp_tools_route(request):
        # MCP tool definitions derived from the OpenAPI spec.
        toolset = OpenApiToolset(build_openapi_spec(server))
        return web.json_response({"tools": toolset.tools()})

    @routes.get("/v1/agent/events")
    async def agent_events_route(request):
        raw_limit = request.rel_url.query.get("limit")
        try:
            limit = int(raw_limit) if raw_limit is not None else 100
        except (TypeError, ValueError):
            limit = 100
        return web.json_response(
            {
                "events": AGENT_EVENTS.recent(limit),
                "streams": AGENT_EVENTS.streams(),
            }
        )

    # Bridge agent/subagent events + streams to the WebSocket so the editor can
    # show them live. Only the most recent server broadcasts (keeps tests clean).
    AGENT_EVENTS.clear_subscribers()

    def _broadcast_agent_payload(payload):
        try:
            channel = "agent_stream" if payload.get("type") == "stream" else "agent_event"
            server.send_sync(channel, payload)
        except Exception:
            pass

    AGENT_EVENTS.subscribe(_broadcast_agent_payload)
