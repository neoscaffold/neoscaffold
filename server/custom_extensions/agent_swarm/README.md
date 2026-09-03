# agent_swarm extension

A fork-join swarm of coding agents — the v1.0.0 integration workload. See
[`harness.md`](../../../harness.md).

## Nodes

### `SwarmSolverNode`
One independent coding agent.

- **Input:** `problem_id` (a key from `problems.py`), optional `model`.
- **Output:** `object` — `{problem_id, title, code, verified, samples_passed, samples_total, model, ...}`.
- **Behavior:** generates a Python solution, streams its work to the UI scoped
  to its node (`AGENT_EVENTS.stream(node_id, ...)`), and verifies the solution by
  running it in the sandbox against the problem's sample I/O.
- **Offline vs live:** offline (default, no key) uses the problem's known-correct
  reference solution so tests are deterministic; when `OPENAI_API_KEY` is set it
  streams a real solution from a model (default `gpt-5.6-terra`, override with
  `NEOSCAFFOLD_SWARM_MODEL`). Force offline with `NEOSCAFFOLD_SWARM_OFFLINE=1`.

### `SwarmJoinNode`
Fork-join aggregator.

- **Input:** `results` (an array of solver outputs, wired via an `nsArrayAppend`
  chain).
- **Output:** `object` — `{total, solved, problems: [...]}`.

## Prompt mode

Ask prompt mode to "spawn a swarm of agents to solve the codeforces problems"
and the graph builder fans out one `SwarmSolverNode` per problem, collects their
outputs into an array, and wires them into a `SwarmJoinNode` (then a
`ConsoleLog`). Running the graph executes the agents concurrently; the Agent
Activity panel shows each agent's live stream scoped to its node.
