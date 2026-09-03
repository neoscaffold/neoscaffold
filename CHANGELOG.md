# Changelog

## 1.0.0 - 2026-09-02

- Improved the natural-language graph builder to generate real node-to-node wiring: concatenation now builds an `nsString` per literal wired through an `nsArrayAppend` chain into `StringJoin` (edges, not literal arrays), pipe/pass-through phrasing inserts a wired `PassThrough`, and every result is wired into the logger. Added a two-row layout so wiring reads clearly, and the editor now auto fits-to-view after inserting a generated graph.
- Added an OpenAPI 3.1 contract (`GET /v1/openapi.json`, `docs/openapi.json`) as the single source of truth for the API.
- Added an MCP interface derived from the OpenAPI spec so other agents can control NeoScaffold: an OpenAPI→MCP tool converter, `GET /v1/mcp/tools`, and a runnable stdio MCP server (`server/mcp_server.py`) implementing `initialize`/`tools/list`/`tools/call` (see `docs/MCP.md`).
- Added subagent visibility: an agent/subagent event log (`server/server/harness/agent_events.py`), instrumentation of the graph builder (parent build span + per-node child spans) and `PromptNode`/`BuildGraphNode`, `GET /v1/agent/events`, live WebSocket broadcast, and an editor **Agent Activity** panel.
- Added the engineering harness (`harness.md`): typed boundaries, parse-over-validate, system lints, observability, and a sandbox seam.
- Added `server/server/harness/`: `parsing` (typed `GraphSpec`/`NodeSpec` parse boundary + kind lattice), `observability` (dependency-free Prometheus metrics + structured JSON logs), `lint` (architecture lint CLI, `python -m server.harness.lint`), and `sandbox` (`run_guarded` timeout seam).
- Added agent-generated graph topology: `graph_builder` turns natural language into a validated prompt-graph (offline deterministic planner by default; optional LLM planner whose output is parsed, repaired, or rejected).
- Added the `agent_graph` extension with `PromptNode` (prompt-driven node, offline by default) and `BuildGraphNode` (builds sub-graphs — agents spinning up agents).
- Added versioned HTTP surface: `POST /v1/agent/build-graph`, `GET /v1/metrics` (PromQL), `GET /v1/healthz`; instrumented graph execution with metrics.
- Added a natural-language entry point in the editor: `neo-prompt-bar` component + `litegraph` Ember service + `importPromptGraph` canvas insertion.
- Added `docs/ROADMAP_1.0.0.md` answering the vision's open questions and specifying the extension and core frontend/backend changes.
- Added extensive tests: parse/observability/lint/sandbox unit tests, graph-builder unit + execution acceptance tests, and v1 route integration tests.

## 0.2.0 - 2026-05-09

- Added parallel graph execution for async-capable nodes with configurable concurrency.
- Added frontend execution mode controls and per-node runtime status tracking for parallel workflows.
- Added async support for node evaluation, including sync node methods that return awaitables.
- Added soft `GOTO` handling in parallel mode for control-flow graphs, including downstream cache invalidation.
- Updated `IfEqual` and `WhileLoop` control flow to complete through their `End*` nodes in parallel mode while only running the selected branch/body path and deferring `End*` nodes until branch/body work finishes.
- Added acceptance and unit coverage for parallel execution, `IfEqual`, and `WhileLoop` workflows.
