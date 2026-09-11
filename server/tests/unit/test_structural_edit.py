"""Deterministic wiring repairs for existing WhileLoop / IfEqual graphs."""

from server.domain.services.graph_builder import build_graph
from server.harness.structural_edit import (
    apply_structural_edits,
    current_prompt,
    is_structural_request,
)

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET

KNOWN = {**CORE["nodes"], **NET["nodes"]}


def _edge(prompt, node_id, name):
    value = prompt[node_id]["inputs"].get(name)
    assert isinstance(value, dict) and "originId" in value, (node_id, name, value)
    return value["originId"]


def loop_workflow():
    """Core-only WhileLoop / IfEqual graph with a dangling end-loop body."""
    return {
        "1": {"type": "PromptNode", "name": "first prompt", "inputs": {"prompt": "pick"}},
        "2": {
            "type": "nsString",
            "name": "prefix",
            "inputs": {"text": "Describe this value: "},
        },
        "3": {
            "type": "ConcatString",
            "name": "concat",
            "inputs": {"a": {"originId": "2"}, "b": {"originId": "1"}},
        },
        "4": {
            "type": "PromptNode",
            "name": "second prompt",
            "inputs": {"prompt": {"originId": "3"}},
        },
        "5": {
            "type": "ConsoleLog",
            "name": "log",
            "inputs": {"any": {"originId": "4"}},
        },
        "6": {"type": "nsInteger", "name": "remaining init", "inputs": {"value": 3}},
        "7": {
            "type": "nsString",
            "name": "remaining key",
            "inputs": {"text": "color_workflow_remaining"},
        },
        "8": {
            "type": "MemoryWrite",
            "name": "write remaining",
            "inputs": {"key": {"originId": "7"}, "value": {"originId": "6"}},
        },
        "9": {"type": "nsBoolean", "name": "active init", "inputs": {"value": False}},
        "10": {
            "type": "nsString",
            "name": "active key",
            "inputs": {"text": "color_workflow_active"},
        },
        "12": {
            "type": "MemoryWrite",
            "name": "write active false",
            "inputs": {"key": {"originId": "10"}, "value": {"originId": "9"}},
        },
        "13": {
            "type": "WhileLoop",
            "name": "while",
            "inputs": {
                "condition_key": "color_workflow_active",
                "node_inputs": {"originId": "12"},
            },
        },
        "15": {
            "type": "PassThrough",
            "name": "loop body",
            "inputs": {
                "value": {"originId": "7"},
                "ignored_input": {"originId": "13"},
            },
        },
        "16": {
            "type": "MemoryRead",
            "name": "read remaining",
            "inputs": {"key": {"originId": "7"}},
        },
        "17": {
            "type": "PassThrough",
            "name": "read in loop",
            "inputs": {
                "value": {"originId": "16"},
                "ignored_input": {"originId": "15"},
            },
        },
        "18": {"type": "nsInteger", "name": "one", "inputs": {"value": 1}},
        "19": {
            "type": "Subtract",
            "name": "decrement",
            "inputs": {"a": {"originId": "17"}, "b": {"originId": "18"}},
        },
        "20": {
            "type": "MemoryWrite",
            "name": "store remaining",
            "inputs": {"key": {"originId": "7"}, "value": {"originId": "19"}},
        },
        "21": {"type": "nsInteger", "name": "zero", "inputs": {"value": 0}},
        "22": {
            "type": "IfEqual",
            "name": "if remaining 0",
            "inputs": {"a": {"originId": "19"}, "b": {"originId": "21"}},
        },
        "23": {
            "type": "IfEqualTrue",
            "name": "true",
            "inputs": {"IfEqual": {"originId": "22"}},
        },
        "24": {"type": "nsBoolean", "name": "false", "inputs": {"value": False}},
        "25": {
            "type": "PassThrough",
            "name": "true gate",
            "inputs": {
                "value": {"originId": "24"},
                "ignored_input": {"originId": "23"},
            },
        },
        "26": {
            "type": "MemoryWrite",
            "name": "stop flag",
            "inputs": {"key": {"originId": "10"}, "value": {"originId": "25"}},
        },
        "27": {
            "type": "IfEqualFalse",
            "name": "false",
            "inputs": {"IfEqual": {"originId": "22"}},
        },
        "31": {
            "type": "EndIfEqual",
            "name": "end if",
            "inputs": {
                "IfEqual": {"originId": "22"},
                "node_inputs": {"originId": "26"},
            },
        },
        "32": {
            "type": "EndWhileLoop",
            "name": "end while",
            "inputs": {
                "WhileLoop": {"originId": "13"},
                "node_inputs": {"originId": "31"},
            },
        },
    }


def test_structural_request_detects_rewire_and_apply():
    assert is_structural_request("fix the infinite sequence in the if statement")
    assert is_structural_request("Make the 2nd PromptNode call before EndWhileLoop")
    assert is_structural_request("You need to make those changes for me")
    assert not is_structural_request('set the text of nsString to "hi"')


def test_loop_workflow_wires_decrement_and_second_body():
    edited = apply_structural_edits(
        loop_workflow(),
        "Wire node 4 into EndWhileLoop. "
        "Fix the infinite sequence in the if statement.",
    )
    assert edited.changed
    prompt = edited.prompt

    assert prompt["13"]["inputs"]["condition_key"] == "color_workflow_remaining"
    if_a = _edge(prompt, "22", "a")
    assert prompt[if_a]["type"] == "PassThrough"
    assert _edge(prompt, if_a, "value") == "19"
    assert _edge(prompt, if_a, "ignored_input") == "20"
    assert _edge(prompt, "31", "node_inputs") == if_a

    assert _edge(prompt, "32", "node_inputs") == "4"
    assert _edge(prompt, "32", "WhileLoop") == "13"
    body_prompt = _edge(prompt, "4", "prompt")
    assert prompt[body_prompt]["type"] == "PassThrough"
    assert _edge(prompt, body_prompt, "ignored_input") == "31"

    assert edited.patch["wire"]
    assert any(
        edge["target"] == "32" and edge["originId"] == "4"
        for edge in edited.patch["wire"]
    )


def test_make_those_changes_uses_history():
    edited = apply_structural_edits(
        loop_workflow(),
        "Make those changes",
        history=[
            {
                "role": "assistant",
                "thoughts": "Wire node 4 into EndWhileLoop.",
                "plan": ["Connect node 4 output to EndWhileLoop.node_inputs."],
            }
        ],
    )
    assert edited.changed
    assert _edge(edited.prompt, "32", "node_inputs") == "4"


def test_build_graph_applies_structural_edits_instead_of_tiny_fallback():
    result = build_graph(
        "Please fix the workflow you made an infinite sequence in the if statement. "
        "Wire node 4 into EndWhileLoop.",
        known_nodes=KNOWN,
        workflow=loop_workflow(),
        llm=lambda _prompt: {
            "thoughts": "Wire EndWhileLoop to node 4.",
            "plan": ["Wire EndWhileLoop.node_inputs to node 4."],
            "widget_edits": [
                {"node_id": "9", "widget": "value", "value": False},
            ],
        },
    )
    assert result.source == "structural"
    assert result.apply_mode == "reconcile"
    assert result.prompt["32"]["inputs"]["node_inputs"]["originId"] == "4"
    assert result.graph_patch["wire"]
    types = [node["type"] for node in result.prompt.values()]
    assert types.count("ConsoleLog") == 1
    assert "WhileLoop" in types


def test_llm_tiny_fallback_is_not_applied_over_existing_loop():
    result = build_graph(
        "fix the infinite loop in the if statement",
        known_nodes=KNOWN,
        workflow=loop_workflow(),
        llm=lambda _prompt: {
            "thoughts": "Create a string and log it.",
            "plan": ["Wire the result into ConsoleLog."],
            "prompt": {
                "1": {"type": "nsString", "name": "text", "inputs": {"text": "fix"}},
                "2": {
                    "type": "ConsoleLog",
                    "name": "log",
                    "inputs": {"any": {"originId": "1"}},
                },
            },
        },
    )
    assert result.source == "structural"
    assert "WhileLoop" in [node["type"] for node in result.prompt.values()]
    assert result.prompt["13"]["type"] == "WhileLoop"


def test_current_prompt_reads_graphToPrompt_envelope():
    inner = loop_workflow()
    assert current_prompt({"prompt": inner, "checksum": "x"})["13"]["type"] == "WhileLoop"
