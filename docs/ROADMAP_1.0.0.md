# NeoScaffold v1.0.0 Roadmap

This document turns the [Vision](../README.md) into concrete decisions: what ships
as a **NeoScaffold extension**, what changes in the **backend** and **frontend**,
and how the [engineering harness](../harness.md) is introduced. It also answers the
vision's open questions.

The organizing insight from harness engineering: **give agents a map, not a
manual.** v1.0.0 lays down that map — typed boundaries, a small set of enforced
lints, a natural-language entry point, and an observability stack — so later
releases can layer richer swarms on a substrate that already converges to quality.

---

## 1. Gap clusters → workstreams

| Cluster | Gap today | v1.0.0 workstream |
| --- | --- | --- |
| Agent-generated topology | Graphs are wired by hand; no NL entry point | **NL → graph builder** extension + `/v1/agent/build-graph` + editor prompt bar |
| Reliability harness | Typed dicts exist; no parse layer, lints, metrics, sandbox | **Harness** package: parsing, lint, observability, sandbox |
| Combination | Nothing verifies swarm-built graphs | Builder emits only graphs that pass the parse layer; failures reject/repair/escalate |

---

## 2. What ships as an extension

**New extension: `custom_extensions/agent_graph/`.**

Rationale: the two highest-leverage vision primitives — *prompt-driven nodes* and
*agent-generated topology* — are node/graph concepts, so they belong in the
extension surface where every other node lives, not baked into the core. This keeps
the core executor stable and lets the agent capabilities evolve as an extension
(and ship as open source alongside the others).

Nodes provided:

- **`PromptNode`** — the prompt-driven node primitive. It carries a `prompt`
  describing its job and an optional `input`. It runs a pluggable *responder*:
  - default **offline responder** performs deterministic prompt templating
    (`{input}` substitution + simple directives), so graphs using `PromptNode` are
    testable without any API key;
  - when an LLM key is configured, the responder can call the existing `llm`
    extension instead. Degradation is explicit: no key → offline responder.
- **`BuildGraphNode`** — wraps the graph builder so a running graph can generate a
  sub-graph from natural language (agents spinning up agents). Returns a typed
  `GraphSpec` payload.

The extension follows the standard layout (`extension.py`, `web.js`,
`requirements.txt`, `README.md`) and registers via `EXTENSION_MAPPINGS`.

---

## 3. Core backend changes

New package `server/server/harness/` (utilities hoisted into the repo, no new deps):

- `parsing.py` — `NodeSpec`, `GraphSpec`, `parse_graph`, `is_assignable`,
  `ParseError`. The parse-don't-validate boundary.
- `observability.py` — dependency-free metrics registry (counter/histogram),
  Prometheus text exposition, structured JSON logging, timers.
- `lint.py` — architecture lint over loaded extensions; CLI `python -m
  server.harness.lint`.
- `sandbox.py` — `run_guarded(fn, timeout)` first-step sandbox seam.

New service:

- `server/server/domain/services/graph_builder.py` — `build_graph(prompt, ...)`
  with an offline deterministic planner and an optional LLM planner; always returns
  a parsed `GraphSpec`.

New HTTP surface (`server/server/infrastructure/apis/v1_routes.py`, registered from
`Server.add_routes`), additive and versioned:

- `POST /v1/agent/build-graph` — `{prompt}` → `{prompt, layout, plan, warnings}`
  ready to import into the editor.
- `GET /v1/metrics` — Prometheus exposition (PromQL).
- `GET /v1/healthz` — liveness + loaded node/extension counts.
- `GET /v1/openapi.json` — the machine-readable API contract.
- `GET /v1/mcp/tools` — MCP tool definitions derived from the OpenAPI spec.
- `GET /v1/agent/events` — recent subagent activity for the visibility panel.

Control + visibility (so other agents can drive NeoScaffold and users can watch):

- `server/server/harness/openapi.py` — OpenAPI 3.1 spec (single source of truth).
- `server/server/harness/openapi_mcp.py` + `mcp.py` + `server/mcp_server.py` — an
  MCP tools server derived from the spec (see `docs/MCP.md`).
- `server/server/harness/agent_events.py` — the subagent event log, broadcast over
  WebSocket and exposed at `/v1/agent/events`.

Executor instrumentation: `run_sequential` / `run_parallel` emit metrics
(graph runs, nodes executed, failures, duration) and structured logs via the
observability module. No behavioral change to execution.

Tooling: a `[tool.ruff]` config and pinned dev tools (`pytest`, `ruff`, `mypy`) so
lint/type/test are reproducible.

---

## 4. Core frontend changes

- **`app/services/litegraph.js`** — a real Ember service wrapping the global
  `NeoScaffold` object (today referenced by a test but missing). It exposes
  `buildGraphFromPrompt(text)` which calls `/v1/agent/build-graph` and imports the
  returned graph onto the canvas. This gives the monolithic JS a testable seam.
- **`app/components/neo-prompt-bar/`** — the natural-language entry point: a text
  box above the editor canvas that sends intent to the service and inserts the
  generated graph. Mounted in `templates/workflow.hbs`.
- **`app/components/neo-agent-activity/`** — the subagent visibility panel; polls
  `/v1/agent/events` and renders build spans with their per-node child spans so a
  user can watch the swarm work.
- Tests: a unit test for the service and integration tests for the components
  (backend mocked), plus manual GUI verification.

---

## 5. Answers to the open questions

**Q: What does "typed semantic language" mean at the node-connection level —
compile-time, runtime, or both?**
Both. Author-time: `harness.lint` statically checks each node/rule contract in CI
and pre-commit. Runtime: `harness.parsing` parses every graph and every edge, using
a single `is_assignable` kind-lattice check (`*` is the top type). The editor uses
the same assignability rule to allow/deny connections, so the UI, the builder, and
the server agree.

**Q: What reliability bar is required for swarm-generated graphs?**
For v1.0.0: every generated graph MUST pass `parse_graph` (referential integrity +
kind assignability) before it can execute, and building/execution MUST be
observable (metrics + structured logs). LLM output is never executed unparsed.
This is the minimum bar that makes higher-autonomy stages feasible without a human
in every loop.

**Q: Which Track A primitives carry into Track B, and which are archetype-specific?**
Carry-through (archetype-independent): the parse layer, the kind lattice, the
observability stack, the sandbox seam, and `PromptNode`. Archetype-specific: the
planner's intent grammar and the concrete node palette a given archetype composes
(these live in `graph_builder.py` / the extension and are meant to grow per
archetype).

**Q: How does Paperclip-style orchestration interact with the Python async
backend?**
It maps directly. The graph is the plan; `run_parallel` already schedules ready
nodes concurrently under a semaphore. Per-node agents run as `async` tasks (or
`to_thread` offloads) inside a node's `evaluate`/sandbox worker and report over the
existing WebSocket channel. No second event loop or process model is introduced in
v1.0.0.

**Q: Correct failure mode for an invalid/unsafe graph — reject, escalate, or
repair?**
All three, by a fixed policy ([harness §6](../harness.md#6-failure-modes-reject-repair-or-escalate)):
cheaply-fixable structural problems are **repaired** deterministically and
re-parsed; non-fixable structural problems are **rejected** with a precise path;
graphs that parse but violate a defended constraint are **escalated** to a human;
warning-only issues **proceed** with the warning attached to context. Every
outcome is recorded as a metric.

---

## 6. Sequencing (converge to quality over time)

1. **Substrate (this release):** parse layer, lint, metrics/health, sandbox seam,
   builder (offline), `agent_graph` extension, NL entry point in the editor.
2. **Autonomy:** LLM planner behind the same parse boundary; per-node swarms that
   scope/implement/test/verify; runtime assertions (heap/DOM/GC) as PromQL
   warnings.
3. **Scale:** Dockerized per-node sandbox, OpenTelemetry export, richer
   architecture lints owned by supervising engineers.

Each stage builds on the previous one's typed boundaries and observability, so the
system keeps converging to quality instead of accumulating unverifiable behavior.
