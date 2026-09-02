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
  (`server.harness.parsing`).

## Reliability

Both nodes satisfy the harness contract lint
(`python -m server.harness.lint`) and the parse-over-validate boundary. The graph
builder never executes unparsed model output: invalid proposals are repaired or
rejected (harness.md §6).
