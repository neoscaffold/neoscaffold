# agent_graph extension

Prompt-driven nodes and agent-generated graph topology for NeoScaffold v1.0.0.
See [`harness.md`](../../../harness.md) and
[`docs/ROADMAP_1.0.0.md`](../../../docs/ROADMAP_1.0.0.md).

## Nodes

### `PromptNode`
A node triggered by a prompt describing its job.

- **Inputs:** `prompt` (required), `input` (optional).
- **Output:** `*`.
- **Behavior:** runs a pluggable *responder*. The default responder is offline
  and deterministic — it substitutes `{input}` in the prompt (or appends the
  input when present) — so graphs using `PromptNode` are unit-testable without an
  API key. To back it with a model, replace `RESPONDER` in `extension.py` with an
  LLM-backed callable (e.g. wrapping the `llm` extension).

```
PromptNode(prompt="Say hello to {input}", input="world") -> "Say hello to world"
```

### `BuildGraphNode`
Turns a natural-language prompt into a validated NeoScaffold sub-graph — the
"agents spinning up agents" pattern.

- **Input:** `prompt` (required).
- **Output:** `object` (a graph spec: `{prompt, plan, warnings, repairs, source}`).
- **Behavior:** delegates to `server.domain.services.graph_builder.build_graph`,
  which always returns a graph that passes the parse boundary
  (`server.harness.parsing`). With `OPENAI_API_KEY` set, the HTTP prompt bar /
  `POST /v1/agent/build-graph` path uses an OpenAI planner (override model with
  `NEOSCAFFOLD_GRAPH_MODEL`; force offline with `NEOSCAFFOLD_GRAPH_OFFLINE=1`).
  Invalid model output is repaired or rejected, then falls back to the offline
  planner. After parse, the harness also repairs **disconnected** graphs: it
  fills empty `prompt` literals from the user request, wires unused outputs
  into unwired required dataflow inputs, and inserts `ValuePath` nodes when a
  dict-producing agent is wired into ConcatString/ConsoleLog (default path
  `summary`). It never invents API keys. When the request includes a `canvas`
  snapshot, the planner can return `widget_edits` to change any existing
  widget instead of (or in addition to) building new nodes. The prompt bar
  keeps a conversation transcript of thoughts and outputs. When a queued run
  fails, it asks how to fix the graph and can arm a patch
  (`POST /v1/agent/suggest-fix`) for Accept.

## Reliability

Both nodes satisfy the harness contract lint
(`python -m server.harness.lint`) and the parse-over-validate boundary. The graph
builder never executes unparsed model output: invalid proposals are repaired or
rejected (harness.md §6).
