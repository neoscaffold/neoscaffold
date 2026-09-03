"""Tests for the natural-language graph builder (offline + LLM planners)."""

import json

import pytest

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET
from server.domain.services.graph_builder import (
    GraphBuilder,
    build_graph,
    extract_llm_payload,
    offline_widget_edits,
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


def test_llm_swarm_join_without_solvers_is_rewritten_and_wired():
    from custom_extensions.agent_swarm.extension import EXTENSION_MAPPINGS as SWARM
    from custom_extensions.agents.extension import EXTENSION_MAPPINGS as AGENTS

    known = {**KNOWN, **AGENTS["nodes"], **SWARM["nodes"]}
    # Mirrors the live /v1/agent/events payload: two CerebrasAgents, a
    # SwarmJoin used as a generic combiner, and a log — all unwired literals.
    payload = {
        "thoughts": "I will create two AI agents to generate painting ideas.",
        "plan": [
            "Create first AI agent to generate painting idea.",
            "Create second AI agent to generate painting idea.",
            "Combine the outputs of both agents into one description.",
        ],
        "prompt": {
            "1": {
                "type": "CerebrasAgent",
                "name": "Painting Idea Generator 1",
                "inputs": {"prompt": "describe a painting idea", "api_key": ""},
            },
            "2": {
                "type": "CerebrasAgent",
                "name": "Painting Idea Generator 2",
                "inputs": {
                    "prompt": "describe a different painting idea",
                    "api_key": "",
                },
            },
            "3": {
                "type": "SwarmJoinNode",
                "name": "Combine Painting Ideas",
                "inputs": {"results": []},
            },
            "4": {
                "type": "ConsoleLog",
                "name": "Log Combined Idea",
                "inputs": {"any": "combined description"},
            },
        },
    }
    result = build_graph(
        "make two ai agents describe ideas for paintings and then combine them into one.",
        known_nodes=known,
        llm=lambda p: payload,
    )
    assert result.source == "llm"
    types = _types(result)
    assert "SwarmJoinNode" not in types
    assert "ConcatString" in types
    join = next(n for n in result.prompt.values() if n["type"] == "ConcatString")
    log = next(n for n in result.prompt.values() if n["type"] == "ConsoleLog")
    assert _is_edge(join["inputs"]["a"]) and _is_edge(join["inputs"]["b"])
    assert _is_edge(log["inputs"]["any"])
    paths = [n for n in result.prompt.values() if n["type"] == "ValuePath"]
    assert len(paths) == 2
    path_ids = {nid for nid, n in result.prompt.items() if n["type"] == "ValuePath"}
    assert join["inputs"]["a"]["originId"] in path_ids
    assert join["inputs"]["b"]["originId"] in path_ids
    assert any("SwarmJoinNode" in r and "ConcatString" in r for r in result.repairs)
    assert not any("no wires" in w for w in result.warnings)


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
    paths = [n for n in result.prompt.values() if n["type"] == "ValuePath"]
    assert len(paths) == 2
    assert all(n["inputs"]["value_path"] == "summary" for n in paths)
    assert all(_is_edge(n["inputs"]["object"]) for n in paths)
    # ConcatString is fed by ValuePath nodes, not raw agent dicts.
    path_ids = {nid for nid, n in result.prompt.items() if n["type"] == "ValuePath"}
    assert join["inputs"]["a"]["originId"] in path_ids
    assert join["inputs"]["b"]["originId"] in path_ids


def test_offline_widget_edit_sets_matching_widget():
    canvas = {
        "15": {
            "type": "CerebrasAgent",
            "name": "CerebrasAgent",
            "widgets": {"api_key": "", "prompt": "old"},
        }
    }
    result = build_graph(
        'set the prompt of CerebrasAgent to "describe cubist paintings"',
        known_nodes=KNOWN,
        canvas=canvas,
    )
    assert result.source == "offline"
    assert result.prompt == {}
    assert result.widget_edits
    assert result.widget_edits[0]["node_id"] == "15"
    assert result.widget_edits[0]["widget"] == "prompt"
    assert result.widget_edits[0]["value"] == "describe cubist paintings"
    assert result.thoughts


def test_offline_widget_edit_skips_api_key_unless_named():
    canvas = {
        "1": {
            "type": "CerebrasAgent",
            "widgets": {"api_key": "secret", "prompt": "old"},
        }
    }
    edits = offline_widget_edits('change CerebrasAgent prompt to "new idea"', canvas)
    assert len(edits) == 1
    assert edits[0]["widget"] == "prompt"


def test_llm_widget_edits_only_skips_new_graph():
    payload = {
        "thoughts": "The existing agent prompt should mention cubism.",
        "plan": ["Update CerebrasAgent prompt"],
        "widget_edits": [{"node_id": "15", "widget": "prompt", "value": "cubism"}],
    }
    result = build_graph(
        "change the agent prompt",
        known_nodes=KNOWN,
        llm=lambda p: payload,
        canvas={"15": {"type": "CerebrasAgent", "widgets": {"prompt": "old"}}},
    )
    assert result.source == "llm"
    assert result.prompt == {}
    assert result.widget_edits[0]["value"] == "cubism"
    assert "cubism" in result.thoughts or result.thoughts


def test_extract_llm_payload_separates_envelope_from_graph():
    thoughts, edits, plan, graph = extract_llm_payload(
        {
            "thoughts": "reason",
            "plan": ["a"],
            "widget_edits": [{"node_id": "1", "widget": "text", "value": "x"}],
            "prompt": GOOD_GRAPH,
        }
    )
    assert thoughts == "reason"
    assert edits[0]["widget"] == "text"
    assert plan == ["a"]
    assert graph == GOOD_GRAPH


def test_offline_if_equal_builds_wired_branches():
    result = build_graph(
        'if "red" equals "blue" then "happy" else "sad"',
        known_nodes=KNOWN,
    )
    types = _types(result)
    assert types.count("IfEqual") == 1
    assert "IfEqualTrue" in types and "IfEqualFalse" in types
    assert "EndIfEqual" in types
    iff = next(n for n in result.prompt.values() if n["type"] == "IfEqual")
    assert _is_edge(iff["inputs"]["a"]) and _is_edge(iff["inputs"]["b"])
    end = next(n for n in result.prompt.values() if n["type"] == "EndIfEqual")
    assert _is_edge(end["inputs"]["IfEqual"])


def test_offline_for_loop_builds_wired_loop():
    result = build_graph("loop 3 times and log the index", known_nodes=KNOWN)
    types = _types(result)
    assert "ForLoop" in types and "EndForLoop" in types
    loop = next(n for n in result.prompt.values() if n["type"] == "ForLoop")
    assert loop["inputs"]["start"] == 0
    assert loop["inputs"]["stop"] == 3
    end = next(n for n in result.prompt.values() if n["type"] == "EndForLoop")
    assert _is_edge(end["inputs"]["ForLoop"])
    assert _is_edge(end["inputs"]["node_inputs"])


def test_offline_imports_prompt_graph_json():
    raw = json.dumps(
        {
            "1": {"type": "nsString", "name": "s", "inputs": {"text": "imported"}},
            "2": {"type": "ConsoleLog", "name": "l", "inputs": {"any": {"originId": "1"}}},
        }
    )
    result = build_graph(f"please import this workflow {raw}", known_nodes=KNOWN)
    assert "nsString" in _types(result)
    log = next(n for n in result.prompt.values() if n["type"] == "ConsoleLog")
    assert _is_edge(log["inputs"]["any"])


def test_offline_imports_litegraph_workflow():
    workflow = {
        "nodes": [
            {
                "id": 6,
                "type": "nsString",
                "title": "s",
                "inputs": [
                    {"name": "in_rules", "link": None},
                    {"name": "text", "link": None},
                ],
                "widgets_values": ["hello", None],
            },
            {
                "id": 2,
                "type": "ConsoleLog",
                "title": "l",
                "inputs": [
                    {"name": "in_rules", "link": None},
                    {"name": "any", "link": 4},
                ],
                "widgets_values": [None],
            },
        ],
        "links": [[4, 6, 0, 2, 1, "*"]],
    }
    result = build_graph(json.dumps(workflow), known_nodes=KNOWN)
    assert result.prompt["6"]["inputs"]["text"] == "hello"
    assert result.prompt["2"]["inputs"]["any"] == {"originId": "6"}


def test_offline_export_workflow_does_not_reimport_nodes():
    canvas = {
        "15": {
            "type": "nsString",
            "name": "s",
            "widgets": {"text": "keep"},
        }
    }
    result = build_graph("export this workflow", known_nodes=KNOWN, canvas=canvas)
    assert result.prompt == {}
    assert result.exported_workflow
    assert result.exported_workflow["prompt"]["15"]["inputs"]["text"] == "keep"


def test_llm_poem_loop_if_control_links_are_wired():
    # Mirrors the live /v1/agent/events graph: dangling IfEqual.b, unwired ends.
    payload = {
        "1": {"type": "CerebrasAgent", "name": "Poem Generator 1", "inputs": {"prompt": "poem a"}},
        "2": {"type": "CerebrasAgent", "name": "Poem Generator 2", "inputs": {"prompt": "poem b"}},
        "3": {
            "type": "ConcatString",
            "name": "Combine Poems",
            "inputs": {"a": {"originId": "1"}, "b": {"originId": "2"}},
        },
        "4": {"type": "ForLoop", "name": "Loop 3 Times", "inputs": {"start": 0, "stop": 3}},
        "5": {
            "type": "IfEqual",
            "name": "Evaluate Poem",
            "inputs": {"a": {"originId": "3"}, "b": {"originId": "LLM"}},
        },
        "6": {"type": "CerebrasAgent", "name": "LLM Judge", "inputs": {"prompt": "judge"}},
        "7": {"type": "EndForLoop", "name": "End Loop", "inputs": {}},
        "8": {"type": "EndIfEqual", "name": "End Evaluation", "inputs": {}},
    }
    from custom_extensions.agents.extension import EXTENSION_MAPPINGS as AGENTS

    known = {**KNOWN, **AGENTS["nodes"]}
    result = build_graph("poems and a judge", known_nodes=known, llm=lambda p: payload)
    end_for = next(n for n in result.prompt.values() if n["type"] == "EndForLoop")
    end_if = next(n for n in result.prompt.values() if n["type"] == "EndIfEqual")
    iff = next(n for n in result.prompt.values() if n["type"] == "IfEqual")
    assert _is_edge(end_for["inputs"]["ForLoop"])
    assert _is_edge(end_if["inputs"]["IfEqual"])
    assert not _is_unfilled_local(iff["inputs"].get("a"))
    assert not _is_unfilled_local(iff["inputs"].get("b"))
    assert not any(
        "ForLoop" in w and "not provided" in w for w in result.warnings
    )
    assert not any(
        "IfEqual" in w and "not provided" in w for w in result.warnings
    )


def _is_unfilled_local(value):
    return value in (None, "", [], {})


def test_llm_refines_from_lint_feedback():
    calls = []
    broken = {
        "1": {"type": "nsString", "inputs": {"text": "x"}},
        "2": {"type": "EndForLoop", "inputs": {}},
    }
    fixed = {
        "1": {"type": "nsString", "inputs": {"text": "x"}},
        "3": {"type": "ForLoop", "inputs": {"start": 0, "stop": 3, "step": 1}},
        "2": {
            "type": "EndForLoop",
            "inputs": {"ForLoop": {"originId": "3"}, "node_inputs": {"originId": "1"}},
        },
    }

    def planner(message):
        calls.append(message)
        if len(calls) == 1:
            return {"plan": ["draft"], "prompt": broken}
        return {"plan": ["fixed"], "prompt": fixed}

    result = build_graph("loop and end", known_nodes=KNOWN, llm=planner)
    assert len(calls) >= 2
    assert any("refined" in r for r in result.repairs) or any(
        "refined" in step for step in result.plan
    )
    end = next(n for n in result.prompt.values() if n["type"] == "EndForLoop")
    assert _is_edge(end["inputs"]["ForLoop"])


def test_llm_if_equal_skeleton_is_completed():
    islands = {
        "1": {"type": "nsString", "inputs": {"text": "a"}},
        "2": {"type": "nsString", "inputs": {"text": "a"}},
        "3": {"type": "IfEqual", "inputs": {"a": {"originId": "1"}, "b": {"originId": "2"}}},
    }
    result = build_graph("if they match", known_nodes=KNOWN, llm=lambda p: islands)
    types = _types(result)
    assert "IfEqualTrue" in types
    assert "IfEqualFalse" in types
    assert "EndIfEqual" in types
    assert any("IfEqualTrue" in r for r in result.repairs)


def test_planner_prompt_includes_registration_contracts():
    from server.domain.services.graph_builder import _planner_prompt

    text = _planner_prompt(KNOWN)
    assert "ConcatString:" in text
    assert "in a, b" in text
    assert "originId" in text
    assert "ValuePath" in text
    assert "summary" in text
    assert "widget_edits" in text
    assert "IfEqual" in text
    assert "ForLoop" in text
    assert "EndWhileLoop" in text
    assert "import" in text.lower()


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
