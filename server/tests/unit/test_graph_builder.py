"""Tests for the natural-language graph builder (offline + LLM planners)."""

import pytest

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET
from server.domain.services.graph_builder import (
    GraphBuilder,
    build_graph,
    repair_graph,
)
from server.harness.parsing import ParseError, contracts_from_nodes

KNOWN = {**CORE["nodes"], **NET["nodes"]}


def _types(result):
    return [node["type"] for node in result.prompt.values()]


# --- offline deterministic planner ---
def test_offline_log_string_builds_valid_graph():
    result = build_graph('please log "hello world"', known_nodes=KNOWN)
    assert result.source == "offline"
    assert "nsString" in _types(result)
    assert "ConsoleLog" in _types(result)
    assert result.plan  # human-readable plan present
    # the string literal is carried into the graph
    assert any(
        node["type"] == "nsString" and node["inputs"].get("text") == "hello world"
        for node in result.prompt.values()
    )


def _is_edge(value):
    return isinstance(value, dict) and "originId" in value


def test_offline_join_builds_wired_graph():
    result = build_graph('concatenate "foo" and "bar" then log it', known_nodes=KNOWN)
    types = _types(result)
    # Real wiring: string nodes -> array -> append chain -> join -> log
    assert types.count("nsString") == 2
    assert "nsArray" in types
    assert types.count("nsArrayAppend") == 2
    assert "StringJoin" in types
    assert "ConsoleLog" in types

    prompt = result.prompt
    # The join's array input is wired from a node, not a literal.
    join = next(n for n in prompt.values() if n["type"] == "StringJoin")
    assert _is_edge(join["inputs"]["array"])
    # The logger's input is wired from the join.
    log = next(n for n in prompt.values() if n["type"] == "ConsoleLog")
    assert _is_edge(log["inputs"]["any"])
    # Each append wires both an array and an element edge.
    for node in prompt.values():
        if node["type"] == "nsArrayAppend":
            assert _is_edge(node["inputs"]["array"])
            assert _is_edge(node["inputs"]["element"])


def test_offline_multiple_literals_wire_even_without_join_word():
    result = build_graph('log "a" and "b" and "c"', known_nodes=KNOWN)
    types = _types(result)
    assert types.count("nsString") == 3
    assert types.count("nsArrayAppend") == 3
    assert "StringJoin" in types


def test_offline_swarm_builds_fanout_and_join():
    from custom_extensions.agent_swarm.extension import EXTENSION_MAPPINGS as SWARM

    known = {**KNOWN, **SWARM["nodes"]}
    result = build_graph(
        "spawn a swarm of agents to solve codeforces/409/F codeforces/784/A codeforces/290/A",
        known_nodes=known,
    )
    types = _types(result)
    assert types.count("SwarmSolverNode") == 3
    assert types.count("SwarmJoinNode") == 1
    assert "nsArray" in types and types.count("nsArrayAppend") == 3
    # join is wired from the collected array; a logger is wired from the join
    join = next(n for n in result.prompt.values() if n["type"] == "SwarmJoinNode")
    assert isinstance(join["inputs"]["results"], dict) and "originId" in join["inputs"]["results"]
    # each solver carries its problem id
    solver_ids = {
        n["inputs"]["problem_id"]
        for n in result.prompt.values()
        if n["type"] == "SwarmSolverNode"
    }
    assert solver_ids == {"codeforces/409/F", "codeforces/784/A", "codeforces/290/A"}


def test_offline_swarm_defaults_to_full_problem_set():
    from custom_extensions.agent_swarm.extension import EXTENSION_MAPPINGS as SWARM

    known = {**KNOWN, **SWARM["nodes"]}
    result = build_graph("run the codeforces swarm", known_nodes=known)
    types = _types(result)
    assert types.count("SwarmSolverNode") == 10


def test_offline_pipe_inserts_wired_passthrough():
    result = build_graph('log "x" through a passthrough', known_nodes=KNOWN)
    types = _types(result)
    assert "PassThrough" in types
    pt = next(n for n in result.prompt.values() if n["type"] == "PassThrough")
    assert _is_edge(pt["inputs"]["value"])
    log = next(n for n in result.prompt.values() if n["type"] == "ConsoleLog")
    assert _is_edge(log["inputs"]["any"])


def test_offline_defaults_to_log_of_prompt_text():
    result = build_graph("greet the user warmly", known_nodes=KNOWN)
    # no literal/keyword: falls back to a string from the prompt text + a log
    assert "nsString" in _types(result)
    assert "ConsoleLog" in _types(result)


def test_offline_result_is_parseable_against_contracts():
    # build() already parses internally; assert the emitted prompt re-parses.
    from server.harness.parsing import parse_graph

    result = build_graph('log "roundtrip"', known_nodes=KNOWN)
    reparsed = parse_graph(result.prompt, contracts=contracts_from_nodes(KNOWN))
    assert set(reparsed.nodes) == set(result.prompt)


def test_empty_prompt_raises():
    with pytest.raises(ParseError):
        build_graph("   ", known_nodes=KNOWN)


def test_no_known_nodes_still_builds():
    result = build_graph('log "x"')  # contracts=None
    assert result.prompt  # non-empty, structurally valid


# --- optional LLM planner ---
GOOD_GRAPH = {
    "1": {"type": "nsString", "name": "s", "inputs": {"text": "x"}},
    "2": {"type": "ConsoleLog", "name": "l", "inputs": {"any": {"originId": "1"}}},
}


def test_llm_valid_graph_accepted():
    result = build_graph("anything", known_nodes=KNOWN, llm=lambda p: GOOD_GRAPH)
    assert result.source == "llm"
    assert set(result.prompt) == {"1", "2"}


def test_llm_graph_wrapped_under_prompt_key():
    result = build_graph("anything", known_nodes=KNOWN, llm=lambda p: {"prompt": GOOD_GRAPH})
    assert result.source == "llm"


def test_llm_dangling_edge_is_repaired():
    bad = {"1": {"type": "ConsoleLog", "name": "l", "inputs": {"any": {"originId": "999"}}}}
    result = build_graph("x", known_nodes=KNOWN, llm=lambda p: bad)
    assert result.source == "llm"
    assert result.repairs  # the dangling edge was dropped


def test_llm_unknown_type_falls_back_to_offline():
    bad = {"1": {"type": "TotallyMadeUp", "name": "x", "inputs": {}}}
    result = build_graph('log "hi"', known_nodes=KNOWN, llm=lambda p: bad)
    # repair drops the unknown node -> empty -> offline fallback
    assert result.source == "offline_fallback"
    assert "ConsoleLog" in _types(result)


def test_llm_non_json_string_falls_back_to_offline():
    result = build_graph('log "hi"', known_nodes=KNOWN, llm=lambda p: "not json at all")
    assert result.source == "offline_fallback"


def test_llm_disconnected_graph_is_wired_by_harness():
    islands = {
        "1": {"type": "nsString", "name": "a", "inputs": {"text": "hello"}},
        "2": {"type": "nsString", "name": "b", "inputs": {"text": "world"}},
        "3": {"type": "ConcatString", "name": "join", "inputs": {}},
        "4": {"type": "ConsoleLog", "name": "log", "inputs": {}},
    }
    result = build_graph("combine two strings", known_nodes=KNOWN, llm=lambda p: islands)
    assert result.source == "llm"
    join = next(n for n in result.prompt.values() if n["type"] == "ConcatString")
    log = next(n for n in result.prompt.values() if n["type"] == "ConsoleLog")
    assert _is_edge(join["inputs"]["a"])
    assert _is_edge(join["inputs"]["b"])
    assert _is_edge(log["inputs"]["any"])
    assert any("wired" in r for r in result.repairs)


def test_llm_empty_agent_prompts_are_filled():
    from custom_extensions.agents.extension import EXTENSION_MAPPINGS as AGENTS

    known = {**KNOWN, **AGENTS["nodes"]}
    islands = {
        "1": {"type": "CerebrasAgent", "name": "a", "inputs": {}},
        "2": {"type": "CerebrasAgent", "name": "b", "inputs": {}},
        "3": {"type": "ConcatString", "name": "join", "inputs": {}},
        "4": {"type": "ConsoleLog", "name": "log", "inputs": {}},
    }
    intent = "make two ai agents describe ideas for paintings and then combine them into one."
    result = build_graph(intent, known_nodes=known, llm=lambda p: islands)
    assert result.source == "llm"
    agents = [n for n in result.prompt.values() if n["type"] == "CerebrasAgent"]
    assert len(agents) == 2
    assert all(n["inputs"].get("prompt") for n in agents)
    join = next(n for n in result.prompt.values() if n["type"] == "ConcatString")
    assert _is_edge(join["inputs"]["a"]) and _is_edge(join["inputs"]["b"])


def test_planner_prompt_includes_registration_contracts():
    from server.domain.services.graph_builder import _planner_prompt

    text = _planner_prompt(KNOWN)
    assert "ConcatString:" in text
    assert "in a, b" in text
    assert "originId" in text


def test_make_openai_planner_none_without_key(monkeypatch):
    from server.domain.services.graph_builder import make_openai_planner

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("NEOSCAFFOLD_GRAPH_OFFLINE", raising=False)
    assert make_openai_planner(KNOWN) is None


def test_make_openai_planner_none_when_forced_offline(monkeypatch):
    from server.domain.services.graph_builder import make_openai_planner

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("NEOSCAFFOLD_GRAPH_OFFLINE", "1")
    assert make_openai_planner(KNOWN) is None


def test_make_openai_planner_returns_callable(monkeypatch):
    from server.domain.services.graph_builder import make_openai_planner

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("NEOSCAFFOLD_GRAPH_OFFLINE", raising=False)
    planner = make_openai_planner(KNOWN)
    assert callable(planner)


# --- repair_graph directly ---
def test_repair_drops_unknown_and_dangling():
    contracts = contracts_from_nodes(KNOWN)
    payload = {
        "1": {"type": "Bogus", "inputs": {}},
        "2": {"type": "ConsoleLog", "inputs": {"any": {"originId": "missing"}}},
    }
    repaired, repairs = repair_graph(payload, contracts=contracts)
    assert "1" not in repaired  # unknown type dropped
    assert repaired["2"]["inputs"] == {}  # dangling edge dropped
    assert len(repairs) >= 2
