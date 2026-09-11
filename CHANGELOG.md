# Changelog

## 1.0.2 - 2026-09-11

- Applied structural harness edits to the current workflow instead of describing them: loop/if termination now keeps the remaining decrement in the `EndWhileLoop` / `EndIfEqual` chain, and a requested body node (for example the second agent) is gated through `EndIfEqual` into `EndWhileLoop.node_inputs`. Returned as an in-place `graph_patch` (`apply_mode: reconcile`) so the canvas is not replaced with a PromptNode+ConsoleLog fallback.
- Stopped toolbar **Stop** from no-oping on a checksum mismatch: `all_stop` is now client-wide, sequential runs yield and re-check between nodes (including loop-back), parallel runs poll and cancel in-flight tasks, and the editor marks remaining nodes cancelled on `stopped` / `stop-point`.
- Accepted the removed httpx/OpenAI `proxies=` argument so agent nodes can construct an HTTP client on current httpx/OpenAI versions.
- Bumped the advertised API version to `1.0.2` (`GET /v1/healthz`, OpenAPI, MCP server info).

## 1.0.1 - 2026-09-10

- Added a conversational workflow harness (`server/server/harness/workflow_agent.py`, `WorkflowHarness`): a request is turned into a workflow, executed, verified against the user's intent, and refined on failure or unmet intent until it both runs and satisfies the request (or the attempt budget is exhausted). Exposed at `POST /v1/agent/run` (`{request, workflow?, max_iterations?, verify?, suggest_code?}` → `{passed, intent_met, intent_reason, iterations[], change_summary, code_suggestions, final_prompt, final_outputs, layout, reply}`).
- Added intent verification: an optional LLM judge (`make_llm_verifier`) decides whether the executed workflow's outputs satisfy the request; an unmet verdict becomes feedback that drives another iteration, so a runnable-but-wrong workflow can recover.
- Added per-iteration graph-change communication: `diff_graphs`/`summarize_diff` report added/removed nodes, retyped nodes, added/removed edges, and widget-value changes (e.g. `Added ConsoleLog (node 2); Wired node 2.any ← node 1`), surfaced in the response, the editor transcript, and the live Agent Activity stream.
- Added node code-update suggestions: when a request can't be satisfied by editing the graph, `make_code_suggester` identifies the implicated node (from node types + runtime error) and proposes a minimal revision of that node's Python class plus a rationale. Rendered in the transcript as a labeled, collapsible block — for review, never auto-applied.
- Added an editor **Iterate** toggle in the conversation prompt bar (portable `neoscaffold_litegraph_extensions.js`) that routes the request to `/v1/agent/run`, loads the final workflow onto the canvas, and renders the per-iteration change lines and code suggestions; the transcript summary shows the terminal (`ConsoleLog`) result rather than arbitrary intermediate node values.
- Documented the harness in the OpenAPI contract: `/v1/agent/run` is now part of `GET /v1/openapi.json` (with `HarnessRun`/`HarnessIteration`/`CodeSuggestion` schemas), so the MCP surface (`GET /v1/mcp/tools`) automatically exposes a `runHarness` tool for other agents. Regenerated `docs/openapi.json`, which also re-syncs the previously stale static copy (adds `import-workflow`, `export-workflow`, `suggest-fix`).
- Fixed the natural-language planner to tolerate models that only allow the default sampling temperature (e.g. `gpt-5.6-terra`), retrying without `temperature` on the corresponding `BadRequestError`.
- Fixed `/v1/agent/run` to accept a raw LiteGraph `serialize()` workflow as context (normalized via `import_workflow`, and `diff_graphs` made defensive), resolving a 500 when iterating from the editor.
- Fixed the editor's auto fit-to-view to reserve the bottom toolbar / prompt-bar (and side-panel) margins so a freshly generated graph is centered within the visible region and is no longer clipped at the bottom edge.
- Folded the standalone control-loop experiment into the workflow harness and removed the separate coding-agent `agent_control` package; the project's focus is the visual programming language, and the iteration machinery now lives in the harness.
- Added `server/tests/test_workflow_agent.py`: graph-diff/summary, per-iteration change communication, `get_node_source`, code-suggestion on failure (and none on success), LiteGraph-context tolerance, and intent verification — all offline/deterministic (no API key required).

## 1.0.0 - 2026-09-02

- Added the `agent_swarm` extension: a fork-join swarm of coding agents. Prompt mode ("spawn a swarm of agents to solve the codeforces problems") builds a graph that fans out to one `SwarmSolverNode` per problem, collects results via a wired `nsArrayAppend` chain, and fork-joins them with `SwarmJoinNode`. Each agent writes a Python solution, streams its work to the UI scoped to its node, and verifies the solution in a subprocess sandbox against sample I/O. Offline/deterministic by default (reference solutions); live agents use OpenAI (default `gpt-5.6-terra`) with token streaming. Verified end-to-end: 10 concurrent live agents solved and verified 10/10 problems.
- Added a subprocess code sandbox (`sandbox.run_python_code`) and a per-node live stream channel on the agent event log (`stream`/`streams`), exposed via `GET /v1/agent/events` (`streams`) and broadcast over the WebSocket (`agent_stream`); the editor's Agent Activity panel now shows each agent's live output scoped to its node.
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
