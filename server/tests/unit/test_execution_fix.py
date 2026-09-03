"""Tests for accept-ready patches suggested after a failed graph run."""

from server.harness.execution_fix import suggest_execution_fix


LOOP_BODY_ERROR = (
    "Exception: At least one node should be connected to this loop "
    "other than EndForLoop"
)


def _poem_loop_prompt():
    return {
        "1": {"type": "CerebrasAgent", "name": "Poem Generator 1", "inputs": {"prompt": "poem a"}},
        "2": {"type": "CerebrasAgent", "name": "Poem Generator 2", "inputs": {"prompt": "poem b"}},
        "3": {
            "type": "ConcatString",
            "name": "Combine Poems",
            "inputs": {"a": {"originId": "1"}, "b": {"originId": "2"}},
        },
        "4": {"type": "ForLoop", "name": "Loop 3 Times", "inputs": {"start": 0, "stop": 3}},
        "7": {
            "type": "EndForLoop",
            "name": "End Loop",
            "inputs": {"ForLoop": {"originId": "4"}},
        },
    }


def test_loop_body_error_arms_passthrough_patch():
    result = suggest_execution_fix(LOOP_BODY_ERROR, prompt=_poem_loop_prompt(), node_id="4")
    assert result["armed"] is True
    assert "ForLoop" in result["ask"]
    assert "ConcatString" in result["ask"]
    add_nodes = result["patch"]["add_nodes"]
    assert len(add_nodes) == 1
    gate = next(iter(add_nodes.values()))
    assert gate["type"] == "PassThrough"
    assert gate["inputs"]["ignored_input"] == {"originId": "4"}
    assert gate["inputs"]["value"] == {"originId": "3"}
    gate_id = next(iter(add_nodes))
    assert any(
        edge["target"] == "7"
        and edge["input"] == "node_inputs"
        and edge["originId"] == gate_id
        for edge in result["patch"]["wire"]
    )


def test_loop_body_error_unwraps_graph_to_prompt_envelope():
    envelope = {"prompt": _poem_loop_prompt(), "workflow": {}, "checksum": "x"}
    result = suggest_execution_fix(LOOP_BODY_ERROR, prompt=envelope, node_id="4")
    assert result["armed"] is True
    gate = next(iter(result["patch"]["add_nodes"].values()))
    assert gate["inputs"]["ignored_input"] == {"originId": "4"}


def test_end_at_end_of_loop_uses_same_body_patch():
    result = suggest_execution_fix(
        "Exception: EndForLoop should be placed at the end of the loop.",
        prompt=_poem_loop_prompt(),
        node_id="4",
    )
    assert result["armed"] is True
    assert result["patch"]["add_nodes"]


def test_reuses_unwired_passthrough_instead_of_inserting():
    prompt = _poem_loop_prompt()
    prompt["8"] = {"type": "PassThrough", "name": "gate", "inputs": {"value": {"originId": "3"}}}
    result = suggest_execution_fix(LOOP_BODY_ERROR, prompt=prompt, node_id="4")
    assert result["armed"] is True
    assert result["patch"]["add_nodes"] == {}
    wires = result["patch"]["wire"]
    assert any(
        edge["target"] == "8"
        and edge["input"] == "ignored_input"
        and edge["originId"] == "4"
        for edge in wires
    )


def test_generic_error_asks_without_arming_empty_patch():
    result = suggest_execution_fix(
        "Exception: something else exploded",
        prompt=_poem_loop_prompt(),
        node_id="3",
    )
    assert result["armed"] is False
    assert "3" in result["ask"]
    assert result["patch"]["add_nodes"] == {}
    assert result["patch"]["wire"] == []
