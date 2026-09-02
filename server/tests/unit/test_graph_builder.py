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


def test_offline_join_builds_stringjoin():
    result = build_graph('concatenate "foo" and "bar" then log it', known_nodes=KNOWN)
    assert "StringJoin" in _types(result)
    assert "ConsoleLog" in _types(result)
    join = next(n for n in result.prompt.values() if n["type"] == "StringJoin")
    assert join["inputs"]["array"] == ["foo", "bar"]


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
