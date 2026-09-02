"""Versioned v1 HTTP surface for NeoScaffold 1.0.0.

Additive, backward-compatible routes:

- ``POST /v1/agent/build-graph`` — natural language -> validated prompt-graph.
- ``GET  /v1/metrics``           — Prometheus text exposition (PromQL).
- ``GET  /v1/healthz``           — liveness + loaded node/extension counts.
"""

from aiohttp import web

from ...domain.services.graph_builder import GraphBuilder
from ...domain.utilities.authorize_user_and_get_info import authorize_user_and_get_info
from ...domain.utilities.fallback_json_encoder import dumps
from ...harness import observability
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


def _layout(prompt):
    """Assign a simple left-to-right layout so the editor can place nodes."""
    layout = {}
    for index, node_id in enumerate(prompt):
        layout[node_id] = [120 + index * 260, 200]
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

        builder = GraphBuilder(known_nodes=getattr(server, "nodes", {}))
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
