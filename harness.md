# NeoScaffold Engineering Harness

> A map, not a thousand-page manual. This document defines the constraints the
> harness enforces, the utilities it provides, and the guardrails that let
> agent-generated graphs converge to quality over time.

The harness is the reliability substrate for NeoScaffold v1.0.0. It exists so that
a **swarm of agents** can build, test, verify, and wire graph nodes without a human
babysitting every step, while a supervising engineer defends a small, carefully
chosen set of constraints.

Guiding principles (from the harness-engineering methodology):

1. **Converge to quality over time.** Give agents a map (typed boundaries, a few
   enforced lints, observable feedback), not an exhaustive rulebook.
2. **Strict typing on boundaries.** The node-connection surface and the HTTP/WS
   API are the boundaries. Everything crossing them is parsed into a typed value
   or rejected with a precise error.
3. **Parse, don't validate.** Convert untrusted input into a typed structure once,
   at the edge, and pass the typed structure inward. Never re-check the same shape
   deep in the call stack. See <https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/>.
4. **Enforce a few constraints; warn on the rest.** Hard-fail only on the
   constraints a supervising engineer is willing to defend. Everything else is a
   warning surfaced into the agent's context so it can decide whether to act.
5. **Observability is a first-class product.** Logs, metrics, and traces are
   stored on the system itself and queryable with LogQL/PromQL so both humans and
   agents can measure effectiveness and efficiency.
6. **Hoist utilities into the repo.** Prefer small, predictable, in-repo utilities
   over new third-party dependencies to avoid dependency hell.

---

## 1. Typed boundaries and contracts

NeoScaffold already has structural node contracts (`INPUT` / `OUTPUT` / `PARAMETERS`
dicts on each node/rule class). The harness formalizes them into a **two-layer**
type model:

| Layer | When | Mechanism | Failure mode |
| --- | --- | --- | --- |
| **Compile-time (author-time)** | Extension load / CI / pre-commit | `harness.lint` verifies every node/rule class declares a complete, well-formed contract | Block (CI red) |
| **Runtime (edge)** | Every `/prompt` and every node boundary | `harness.parsing` parses payloads and node inputs/outputs into typed dataclasses | Reject with structured `ParseError`, or repair, or escalate (§6) |

"Typed semantic language at the node-connection level" therefore means **both**:
a static contract that lints at author-time, and a runtime parse of the values
flowing across each edge. An edge is valid only when the upstream `OUTPUT.kind`
is assignable to the downstream input `kind` (with `*` as the top type).

### Kind lattice

```
              *                 (top / any)
        ______|______
       |      |      |
    string  number  array  boolean  object  rule_group  ...
```

`*` is assignable to and from everything (gradual typing). Concrete kinds are
assignable only to themselves or `*`. The assignability check lives in
`harness.parsing.is_assignable(from_kind, to_kind)` and is the single source of
truth used by the graph builder, the editor, and CI.

---

## 2. Parse, don't validate

All untrusted input is parsed at the edge into typed structures defined in
`server/server/harness/parsing.py`:

- `NodeSpec` — one node in a prompt-graph (`type`, `name`, `inputs`).
- `GraphSpec` — a whole prompt-graph (`{node_id: NodeSpec}`), with referential
  integrity checks (every `originId` points at a declared node; no self-loops).
- `parse_graph(payload, *, known_types)` → `GraphSpec` **or** raises `ParseError`
  carrying a machine-readable `path` and `message`.

Downstream code (executor, builder, endpoints) consumes the typed `GraphSpec` and
never re-inspects raw dicts. This is the concrete realization of "parse, don't
validate": one parse at the boundary, typed values everywhere inside.

A parsed graph is **correct by construction** for the checks the parser performs,
so the graph builder (§4) can only ever emit graphs that already parse.

---

## 3. System-level lints

The harness ships architecture lints, not just style lints. `harness.lint`
enforces the constraints a supervising engineer defends:

- Every registered node class declares `CATEGORY`, `SUBCATEGORY`, `DESCRIPTION`,
  an `INPUT` with `required_inputs`, an `OUTPUT` with `kind`/`name`, and a callable
  `evaluate`.
- Every registered rule class declares `PARAMETERS` and a callable `evaluate`.
- Input/parameter entries declare a `kind` and `name`; `kind` is a known kind.
- `EXTENSION_MAPPINGS` is well-formed (name, version, nodes/rules maps).

Run it as `python -m server.harness.lint` (exits non-zero on violations). It is
wired into pre-commit and CI. Warnings (e.g. missing `SUBCATEGORY` description)
are printed but do not fail; violations do. This is the "lint rules for system and
architecture design" primitive: the set is intentionally small and enforced.

Platform-specific reliability lints (e.g. "a node that performs network I/O must
declare `optional_inputs.timeout`") are added here as the platform hardens. Each
new hard constraint must have a named owner who defends it.

---

## 4. Agent-generated graph topology

The natural-language entry point turns intent into a **valid** prompt-graph:

```
NL prompt ──▶ Planner ──▶ GraphSpec (typed) ──▶ parse_graph ──▶ executable prompt
                 │                                    │
        offline deterministic                 reject / repair / escalate
        or LLM-backed (optional)
```

- `server/server/domain/services/graph_builder.py` exposes
  `build_graph(prompt, *, known_types, llm=None) -> BuildResult`.
- **Offline, deterministic planner** (default): a small intent grammar composes
  known core nodes (`nsString`, `StringJoin`, `PassThrough`, `ConsoleLog`, …).
  Deterministic output means it is unit-testable **without any API key**.
- **LLM planner** (optional): when a key is present, the LLM proposes a graph as
  JSON which is then run through `parse_graph`. The harness trusts the *parser*,
  never the model: an invalid proposal is repaired or rejected (§6), never
  executed blindly. A proposal that parses but is **disconnected** (no
  `originId` wires) is still repaired: unused producers are wired into unwired
  required dataflow inputs, and empty `prompt` literals are filled from the
  user's request. When a dict-producing node (e.g. `CerebrasAgent`) is wired
  into a string consumer (`ConcatString`, `ConsoleLog`), the harness inserts a
  `ValuePath` adapter (default field `summary`) rather than concatenating the
  raw dict. Credential fields (`api_key`, …) are never invented.

Every builder result is parsed before it leaves the service, so the endpoint and
the editor only ever receive graphs that already satisfy §1–§2.

### Per-node swarms (orchestration)

Prompt-driven nodes (the `PromptNode` primitive) carry a `prompt` describing the
node's job. The v1.0.0 orchestration pattern is **agents spinning up agents**
(Paperclip-style): a parent scoping agent decomposes intent into node prompts, and
per-node agents scope → implement → test → verify. This maps onto the existing
Python async backend as follows:

- The graph is the plan; nodes are units of work.
- `run_parallel` already schedules ready nodes concurrently under a semaphore
  (`MAX_PARALLEL_NODES`); per-node agents run *inside* a node's `evaluate` (or a
  sandboxed worker) and report progress over the same WebSocket channel.
- No new event loop is required: node agents are `async` tasks or `to_thread`
  offloads, consistent with today's executor.

---

## 5. Observability

Logs, metrics, and traces are produced by the system and stored on the system,
queryable with the same languages an operator would use in Grafana/Prometheus.

- **Metrics** — `server/server/harness/observability.py` implements a tiny,
  dependency-free registry (counters + histograms) exposed at `GET /v1/metrics`
  in Prometheus text-exposition format (**PromQL**-compatible). No
  `prometheus_client` dependency is added (utilities hoisted into the repo).
  Instrumented today: graph runs, nodes executed, node failures, node duration,
  graph-build requests.
- **Logs** — structured JSON log lines (one object per line) so a log shipper can
  index fields and operators can query with **LogQL**. `harness.observability.log_event`
  emits `{"ts", "level", "event", ...fields}`.
- **Traces** — each prompt run carries a `prompt_id`; each node emits span-like
  start/finish events keyed by `prompt_id` + `node_id`. This is the seam where an
  OpenTelemetry exporter is added without touching call sites.
- **Health** — `GET /v1/healthz` returns liveness + loaded-extension/node counts.

### Agent-performance monitoring

Because metrics live on the system, the harness can answer "how effective and
efficient are the agents?": graph-build success rate, nodes-per-graph,
build-to-valid latency, node failure rate, and execution duration histograms are
all exported. Anomaly constraints (e.g. "warn if GC count during UI navigation
rises >20%") are expressed as PromQL alerts over these series and surfaced into
the agent's context as warnings rather than hard failures (§6).

---

## 6. Failure modes: reject, repair, or escalate

When a swarm produces an invalid or unsafe graph the harness follows a fixed
policy:

| Situation | Action |
| --- | --- |
| Structurally invalid (fails `parse_graph`) and cheaply fixable | **Repair** (drop dangling edges, coerce assignable kinds) then re-parse |
| Multi-node graph with no wires, or empty `prompt`/`text` literals | **Repair** (wire unused producers into unwired required dataflow inputs in id order; fill empty prompt literals from the user request). Never invents credentials. |
| Dict producer wired into a string consumer | **Repair** by inserting a `ValuePath` adapter (bounded: only that node type; default path `summary` / `code`) |
| Structurally invalid and not cheaply fixable | **Reject** with a `ParseError` describing the exact `path` |
| Parses but violates a defended constraint (unsafe node, missing sandbox) | **Escalate** to a human with the failing constraint attached |
| Parses and only trips a *warning* | **Proceed**, attach the warning to context |

Repair is bounded and deterministic. It does not invent arbitrary nodes; the
one allowed insertion is a ``ValuePath`` adapter that deconstructs a known dict
output. Rejections and escalations are logged as metrics so their frequency is
observable.

---

## 7. Sandboxed execution

Agent-authored node code runs under a sandbox. v1.0.0 ships a minimal, in-process
first step and specifies the target:

- **Now:** `server/server/harness/sandbox.py::run_guarded` runs a callable with a
  wall-clock timeout and captures result/exception, so a runaway node cannot hang
  the executor. Timeouts are recorded as metrics.
- **Target:** per-node execution in Docker (or Cloudflare sandboxes for speed)
  with CPU/memory/network limits and a read-only workspace mount. The `run_guarded`
  seam is where the container runner is swapped in without changing node code.

Runtime assertions (heap/DOM/browser-cache/GC inspection, memory-leak detection)
are driven from the frontend test harness and reported as metrics; anomalous
deltas become PromQL warnings per §5.

---

## 8. Branching, PRs, and the agent workflow

Agents drive features end to end on their own branches:

1. Validate the current state of the codebase (lints + tests green).
2. Reproduce a reported bug; record a video of the failure.
3. Implement a fix.
4. Validate by driving the application; record a second video of the resolution.
5. Open a pull request; respond to agent + human review.
6. Detect and remediate build failures.
7. Escalate to a human only when judgment is required (§6).
8. Merge.

The harness makes steps 1, 3, 4, and 6 measurable: lints and the parse layer gate
authoring, metrics gate runtime behavior, and the observability stack gives both
the agent and the reviewer the evidence to decide.

---

## 9. Naming conventions

- **Node/rule classes:** `PascalCase`; core primitives prefixed `ns` (`nsString`).
- **Kinds:** lowercase snake or single symbol (`string`, `rule_group`, `*`).
- **Extensions:** snake_case directory under `custom_extensions/` containing
  `extension.py` (Python), optional `web.js` (LiteGraph UI), `requirements.txt`,
  and `README.md`.
- **HTTP:** versioned under `/v1/...`; new endpoints are additive and backward
  compatible with the unversioned routes during the 1.0 transition.
- **Metrics:** `neoscaffold_<subject>_<unit>` (`neoscaffold_nodes_executed_total`,
  `neoscaffold_node_duration_seconds`).

---

## 10. Control surface: OpenAPI + MCP

NeoScaffold is meant to be driven by other agents, not just humans. The control
surface is defined once as an **OpenAPI 3.1 spec** (`server/server/harness/openapi.py`,
served at `GET /v1/openapi.json`, static copy in `docs/openapi.json`) and exposed
to agents through the **Model Context Protocol**:

- `server/server/harness/openapi_mcp.py` converts each OpenAPI operation (with an
  `operationId`) into an MCP tool (`name`, `description`, JSON-Schema `inputSchema`)
  and resolves a tool call back into a concrete HTTP request.
- `server/server/harness/mcp.py` implements the MCP JSON-RPC subset a tools server
  needs (`initialize`, `tools/list`, `tools/call`, `ping`), dependency-free.
- `server/mcp_server.py` is the runnable stdio server that proxies tool calls to
  the HTTP API. `GET /v1/mcp/tools` exposes the derived tool list for introspection.

Because tools are derived from the spec, **adding an operation to the OpenAPI
document makes it agent-callable automatically** — the spec is the one boundary
to defend. See `docs/MCP.md`.

## 11. Subagent visibility

Users and agents can see inside the swarm. `server/server/harness/agent_events.py`
records span-like events (`id`, `parent_id`, `kind`, `name`, `status`, timings,
`detail`) in a bounded, thread-safe log with live subscribers:

- The graph builder opens a `graph_build` span and records a child `node` span per
  generated node (parent → child shows agents spinning up agents). `PromptNode`
  and `BuildGraphNode` record their own events.
- `GET /v1/agent/events?limit=` returns recent events; new events are also
  broadcast over the existing WebSocket (`agent_event`) for live UI updates.
- The editor's **Agent Activity** panel renders these spans so a user watches the
  subagents work in real time.

This complements the metrics/logs/traces in §5: metrics answer "how much / how
fast", the event log answers "what is each subagent doing right now".

## 12. Integration workload: the coding-agent swarm

The `agent_swarm` extension is the end-to-end exercise of the whole harness. From
a single prompt, prompt mode builds a fan-out/fan-in graph: one `SwarmSolverNode`
per problem (each an independent agent), a wired `nsArrayAppend` chain collecting
their outputs, and a `SwarmJoinNode` that fork-joins the results.

Each solver agent:
- writes a Python solution (offline reference solution in tests; a live OpenAI
  model such as `gpt-5.6-terra` in production, streamed token-by-token);
- streams its work to the UI scoped to its node (`AGENT_EVENTS.stream(node_id, …)`,
  surfaced in the Agent Activity panel and over the `agent_stream` WebSocket);
- verifies its solution by running it in the subprocess sandbox
  (`sandbox.run_python_code`) against sample I/O.

This ties together §1–§11: parse-validated graph topology, per-node observability
and streaming, sandboxed execution, and the agents-spinning-up-agents
orchestration. It is the canonical "does our setup work well?" test — 10 agents
running concurrently, each solving and verifying independently, then fork-joined
into one report.

## 13. What the harness deliberately does not do

- It does not re-validate typed structures after the edge parse.
- It does not hard-fail on style or on soft constraints; those are warnings.
- It does not trust LLM output; it trusts the parser.
- It does not add heavyweight dependencies when a small in-repo utility suffices.
