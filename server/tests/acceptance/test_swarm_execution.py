"""End-to-end: prompt -> swarm graph -> concurrent solve/verify -> fork-join.

Runs the whole fan-out/fan-in swarm through the real GraphExecutor with the
deterministic offline coder (no network), proving the wiring and the fork-join
report execute correctly.
"""

import asyncio
import os

os.environ["NEOSCAFFOLD_SWARM_OFFLINE"] = "1"

from custom_extensions.agent_swarm.extension import EXTENSION_MAPPINGS as SWARM  # noqa: E402
from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE  # noqa: E402
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET  # noqa: E402
from server.domain.services.graph_builder import build_graph  # noqa: E402
from server.domain.services.graph_executor import GraphExecutor  # noqa: E402
from server.harness.agent_events import AGENT_EVENTS  # noqa: E402

KNOWN = {**CORE["nodes"], **NET["nodes"], **SWARM["nodes"]}


class AcceptanceServer:
    def __init__(self):
        self.ENABLE_SMART_CACHE = True
        self.INSPECTION_DELAY = 0
        self.MAX_PARALLEL_NODES = 8
        self.client_id = "acc"
        self.current_workflow_id = "wf"
        self.sessions = {}
        self.rules = {}
        self.sent_messages = []
        self.nodes = KNOWN

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


def _run(prompt_dict, runtime="parallel"):
    server = AcceptanceServer()
    executor = GraphExecutor(server)
    graph = executor.prompt_to_graph(prompt_dict)
    response = {"prompt_id": "p", "number": 1, "client_id": "acc", "workflow_id": "wf"}
    if runtime == "parallel":
        return asyncio.run(executor.run_parallel(graph, response)), server
    return asyncio.run(executor.run_sequential(graph, response)), server


def test_swarm_graph_executes_and_fork_joins():
    AGENT_EVENTS.clear()
    result = build_graph(
        "spawn a swarm of agents to solve "
        "codeforces/409/F codeforces/784/A codeforces/290/A codeforces/171/B",
        known_nodes=KNOWN,
    )
    graph_results, server = _run(result.prompt, "parallel")

    join_ids = [nid for nid, n in result.prompt.items() if n["type"] == "SwarmJoinNode"]
    assert join_ids
    report = graph_results[join_ids[0]].values
    assert report["total"] == 4
    assert report["solved"] == 4  # offline reference solutions all verify
    solved_ids = {p["problem_id"] for p in report["problems"] if p["verified"]}
    assert solved_ids == {
        "codeforces/409/F",
        "codeforces/784/A",
        "codeforces/290/A",
        "codeforces/171/B",
    }

    # Each solver node produced a verified solution.
    solver_ids = [nid for nid, n in result.prompt.items() if n["type"] == "SwarmSolverNode"]
    assert len(solver_ids) == 4
    for nid in solver_ids:
        assert graph_results[nid].values["verified"] is True

    # Streams were emitted scoped to each solver node.
    streams = AGENT_EVENTS.streams()
    assert len([nid for nid in solver_ids if nid in streams]) == 4
