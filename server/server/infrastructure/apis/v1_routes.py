"""Versioned v1 HTTP surface for NeoScaffold 1.0.0.

Additive, backward-compatible routes:

- ``POST /v1/agent/build-graph`` — natural language -> validated prompt-graph.
- ``POST /v1/agent/suggest-fix`` — run-error -> accept-ready graph patch.
- ``GET  /v1/metrics``           — Prometheus text exposition (PromQL).
- ``GET  /v1/healthz``           — liveness + loaded node/extension counts.
"""

from aiohttp import web

from ...domain.services.graph_builder import GraphBuilder, make_openai_planner
from ...harness.workflows import export_workflow, import_workflow
from ...domain.utilities.authorize_user_and_get_info import authorize_user_and_get_info
from ...domain.utilities.fallback_json_encoder import dumps
from ...harness import observability
from ...harness.agent_events import AGENT_EVENTS
from ...harness.openapi import build_openapi_spec
from ...harness.openapi_mcp import OpenApiToolset
from ...harness.execution_fix import suggest_execution_fix
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


_LAYOUT_ORIGIN_X = 80
_LAYOUT_ORIGIN_Y = 80
_LAYOUT_COL_W = 280
_LAYOUT_ROW_H = 220
_LAYOUT_WRAP_COLS = 4


def _node_id_sort_key(node_id):
    try:
        return (0, int(node_id))
    except (TypeError, ValueError):
        return (1, str(node_id))


def _incoming_origins(node):
    origins = []
    inputs = (node or {}).get("inputs")
    if not isinstance(inputs, dict):
        return origins
    for value in inputs.values():
        if isinstance(value, dict) and value.get("originId") is not None:
            origins.append(str(value["originId"]))
    return origins


def _execution_ranks(prompt):
    """Longest-path ranks from sources so columns follow execution order."""
    ids = [str(node_id) for node_id in prompt]
    preds = {node_id: [] for node_id in ids}
    succs = {node_id: [] for node_id in ids}
    for node_id, node in prompt.items():
        target = str(node_id)
        for origin in _incoming_origins(node):
            if origin in preds and origin != target:
                preds[target].append(origin)
                succs[origin].append(target)

    indegree = {node_id: len(preds[node_id]) for node_id in ids}
    ranks = {node_id: 0 for node_id in ids}
    queue = [node_id for node_id in ids if indegree[node_id] == 0]
    queue.sort(key=_node_id_sort_key)
    remaining = set(ids)

    while queue:
        node_id = queue.pop(0)
        remaining.discard(node_id)
        for succ in succs[node_id]:
            ranks[succ] = max(ranks[succ], ranks[node_id] + 1)
            indegree[succ] -= 1
            if indegree[succ] == 0:
                queue.append(succ)
                queue.sort(key=_node_id_sort_key)

    if remaining:
        base = max(ranks.values(), default=-1) + 1
        for offset, node_id in enumerate(sorted(remaining, key=_node_id_sort_key)):
            ranks[node_id] = base + offset
    return ranks, preds


def _place_row(node_ids, y, layout, preds=None):
    """Place ``node_ids`` left-to-right on one row, wrapping after 4 columns."""
    ordered = list(node_ids)
    if preds is not None:

        def row_key(node_id):
            upstream = [
                layout[origin][0]
                for origin in preds.get(node_id, [])
                if origin in layout
            ]
            barycenter = sum(upstream) / len(upstream) if upstream else 0
            return (barycenter, _node_id_sort_key(node_id))

        ordered.sort(key=row_key)
    else:
        ordered.sort(key=_node_id_sort_key)

    for index, node_id in enumerate(ordered):
        col = index % _LAYOUT_WRAP_COLS
        row = index // _LAYOUT_WRAP_COLS
        layout[node_id] = [
            _LAYOUT_ORIGIN_X + col * _LAYOUT_COL_W,
            y + row * _LAYOUT_ROW_H,
        ]
    extra_rows = max(0, (len(ordered) - 1) // _LAYOUT_WRAP_COLS)
    return y + (extra_rows + 1) * _LAYOUT_ROW_H


def _layout(prompt):
    """Place nodes left-to-right, then top-to-bottom.

    A linear pipeline stays on one row (left to right). Parallel stages share a
    row (left to right) and later stages move down. A disconnected set wraps
    like a reading-order grid.
    """
    if not prompt:
        return {}

    ranks, preds = _execution_ranks(prompt)
    by_rank = {}
    for node_id, rank in ranks.items():
        by_rank.setdefault(rank, []).append(node_id)

    layout = {}
    rank_sizes = [len(by_rank[rank]) for rank in by_rank]
    max_width = max(rank_sizes) if rank_sizes else 1
    max_rank = max(by_rank) if by_rank else 0

    if max_rank == 0:
        _place_row(by_rank.get(0, []), _LAYOUT_ORIGIN_Y, layout)
        return layout

    if max_width == 1:
        for node_id, rank in ranks.items():
            layout[node_id] = [
                _LAYOUT_ORIGIN_X + rank * _LAYOUT_COL_W,
                _LAYOUT_ORIGIN_Y,
            ]
        return layout

    y = _LAYOUT_ORIGIN_Y
    for rank in sorted(by_rank):
        y = _place_row(by_rank[rank], y, layout, preds=preds)
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

        canvas = data.get("canvas") if isinstance(data.get("canvas"), dict) else None
        history = data.get("history") if isinstance(data.get("history"), list) else None
        workflow = data.get("workflow") if isinstance(data.get("workflow"), dict) else None

        known_nodes = getattr(server, "nodes", {})
        builder = GraphBuilder(
            known_nodes=known_nodes,
            llm=make_openai_planner(known_nodes),
        )
        try:
            result = builder.build(
                prompt_text, canvas=canvas, history=history, workflow=workflow
            )
        except ParseError as exc:
            observability.inc("neoscaffold_graph_build_rejected_total", reason="parse")
            return web.json_response({"error": exc.message, "path": exc.path}, status=422)

        payload = {
            "prompt": result.prompt,
            "layout": _layout(result.prompt) if result.prompt else {},
            "plan": result.plan,
            "warnings": result.warnings,
            "repairs": result.repairs,
            "source": result.source,
            "thoughts": result.thoughts,
            "widget_edits": result.widget_edits,
        }
        if result.exported_workflow is not None:
            payload["exported_workflow"] = result.exported_workflow
        return web.json_response(payload, dumps=dumps)

    @routes.post("/v1/agent/import-workflow")
    async def import_workflow_route(request):
        user_id, error = _authorized_user(request)
        if error is not None:
            return error
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid JSON body"}, status=400)
        raw = data.get("workflow", data) if isinstance(data, dict) else data
        prompt = import_workflow(raw)
        if not prompt:
            return web.json_response({"error": "not a workflow or prompt-graph"}, status=422)
        return web.json_response({"prompt": prompt, "layout": _layout(prompt)}, dumps=dumps)

    @routes.post("/v1/agent/suggest-fix")
    async def suggest_fix_route(request):
        user_id, error = _authorized_user(request)
        if error is not None:
            return error
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid JSON body"}, status=400)
        if not isinstance(data, dict):
            return web.json_response({"error": "invalid JSON body"}, status=400)
        message = data.get("error") or data.get("message") or ""
        if not isinstance(message, str) or not message.strip():
            errors = data.get("node_errors")
            if isinstance(errors, list) and errors:
                first = errors[0] if isinstance(errors[0], dict) else {}
                message = first.get("message") or str(errors[0])
        if not isinstance(message, str) or not message.strip():
            return web.json_response(
                {"error": "'error' or 'node_errors' is required"}, status=400
            )
        node_id = data.get("node_id")
        prompt = data.get("prompt") if isinstance(data.get("prompt"), dict) else {}
        suggestion = suggest_execution_fix(message, prompt=prompt, node_id=node_id)
        return web.json_response(suggestion, dumps=dumps)

    @routes.post("/v1/agent/export-workflow")
    async def export_workflow_route(request):
        user_id, error = _authorized_user(request)
        if error is not None:
            return error
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "invalid JSON body"}, status=400)
        prompt = data.get("prompt") if isinstance(data, dict) else None
        litegraph = data.get("workflow") if isinstance(data, dict) else None
        if not isinstance(prompt, dict):
            prompt = import_workflow(data) or {}
        if not prompt and not litegraph:
            return web.json_response({"error": "prompt or workflow is required"}, status=400)
        return web.json_response(
            export_workflow(
                prompt,
                layout=_layout(prompt) if prompt else {},
                litegraph=litegraph if isinstance(litegraph, dict) else None,
            ),
            dumps=dumps,
        )

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
