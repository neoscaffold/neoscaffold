"""Tests for the agent_swarm extension (offline/deterministic)."""

import os

# Force the deterministic offline coder even though OPENAI_API_KEY may be set
# in this environment, so these tests never hit the network.
os.environ["NEOSCAFFOLD_SWARM_OFFLINE"] = "1"

from custom_extensions.agent_swarm.extension import (  # noqa: E402
    EXTENSION_MAPPINGS,
    SwarmJoinNode,
    SwarmSolverNode,
    offline_coder,
    solve,
)
from custom_extensions.agent_swarm.problems import PROBLEM_IDS, get_problem  # noqa: E402
from server.domain.services.graph_builder import DEFAULT_CODEFORCES_IDS  # noqa: E402
from server.harness.agent_events import AGENT_EVENTS  # noqa: E402
from server.harness.lint import has_errors, lint_registry  # noqa: E402


class FakeNode:
    def __init__(self, node_id):
        self.node_id = node_id


def _resolved(required=None, optional=None):
    def wrap(d):
        return {k: {"values": v} for k, v in (d or {}).items()}

    return {"required_inputs": wrap(required), "optional_inputs": wrap(optional)}


def test_all_reference_solutions_verify_offline():
    for problem_id in PROBLEM_IDS:
        result = solve(get_problem(problem_id), node_id=f"n-{problem_id}", coder=offline_coder)
        assert result["verified"], (problem_id, result["sample_results"])
        assert result["samples_passed"] == result["samples_total"] > 0
        assert result["model"] == "offline"


def test_solve_streams_to_node():
    AGENT_EVENTS.clear()
    solve(get_problem("codeforces/409/F"), node_id="stream-node", coder=offline_coder)
    streams = AGENT_EVENTS.streams()
    assert "stream-node" in streams
    assert "verified=True" in streams["stream-node"]["text"]


def test_solver_node_evaluate_offline():
    node = SwarmSolverNode()
    node._node = FakeNode("solver-1")
    result = node.evaluate(_resolved({"problem_id": "codeforces/171/B"}))
    assert result["verified"] is True
    assert result["problem_id"] == "codeforces/171/B"
    assert result["node_id"] == "solver-1"


def test_solver_node_unknown_problem():
    node = SwarmSolverNode()
    node._node = FakeNode("solver-x")
    result = node.evaluate(_resolved({"problem_id": "codeforces/999/Z"}))
    assert result["verified"] is False
    assert result["error"] == "unknown problem"


def test_join_node_aggregates_results():
    node = SwarmJoinNode()
    results = [
        {"problem_id": "a", "verified": True, "samples_passed": 2, "samples_total": 2},
        {"problem_id": "b", "verified": False, "samples_passed": 1, "samples_total": 2},
        {"problem_id": "c", "verified": True, "samples_passed": 1, "samples_total": 1},
    ]
    report = node.evaluate(_resolved({"results": results}))
    assert report["total"] == 3
    assert report["solved"] == 2
    assert {p["problem_id"] for p in report["problems"]} == {"a", "b", "c"}


def test_extension_nodes_pass_contract_lint():
    violations = lint_registry(EXTENSION_MAPPINGS["nodes"], EXTENSION_MAPPINGS.get("rules"))
    assert not has_errors(violations), [str(v) for v in violations]


def test_default_ids_match_problem_set():
    # Guard against drift between the builder's default workload and the problems.
    assert set(DEFAULT_CODEFORCES_IDS) == set(PROBLEM_IDS)
