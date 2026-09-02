"""Tests for the parse-don't-validate boundary (server.harness.parsing)."""

import pytest

from server.harness.parsing import (
    TOP_KIND,
    GraphSpec,
    InputRef,
    NodeContract,
    ParseError,
    contract_from_python_class,
    contracts_from_nodes,
    is_assignable,
    lint_graph,
    parse_graph,
)


# --- fake node classes mirroring the real extension contract shape ---
class FakeString:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "string"
    INPUT = {"required_inputs": {"text": {"kind": "*", "name": "text"}}}
    OUTPUT = {"kind": "string", "name": "*", "cacheable": True}

    def evaluate(self, node_inputs):
        return ""


class FakeConsoleLog:
    CATEGORY = "utilities"
    SUBCATEGORY = "logging"
    DESCRIPTION = "log"
    INPUT = {"required_inputs": {"any": {"kind": "*", "name": "any"}}}
    OUTPUT = {"kind": "*", "name": "any", "cacheable": True}

    def evaluate(self, node_inputs):
        return ""


class FakeNumberSink:
    CATEGORY = "core"
    SUBCATEGORY = "math"
    DESCRIPTION = "needs a number"
    INPUT = {"required_inputs": {"value": {"kind": "number", "name": "value"}}}
    OUTPUT = {"kind": "number", "name": "*", "cacheable": True}

    def evaluate(self, node_inputs):
        return 0


NODES = {
    "nsString": {"python_class": FakeString},
    "ConsoleLog": {"python_class": FakeConsoleLog},
    "NumberSink": {"python_class": FakeNumberSink},
}


def simple_prompt():
    return {
        "1": {"type": "nsString", "name": "s", "inputs": {"text": "hi"}},
        "2": {"type": "ConsoleLog", "name": "log", "inputs": {"any": {"originId": "1"}}},
    }


# --- is_assignable ---
def test_is_assignable_top_type():
    assert is_assignable("*", "string")
    assert is_assignable("string", "*")
    assert is_assignable("*", "*")


def test_is_assignable_concrete():
    assert is_assignable("string", "string")
    assert not is_assignable("string", "number")


# --- parse_graph structure ---
def test_parse_graph_roundtrip_to_prompt():
    spec = parse_graph(simple_prompt())
    assert isinstance(spec, GraphSpec)
    assert set(spec.nodes) == {"1", "2"}
    assert spec.nodes["2"].inputs["any"] == InputRef(origin_id="1")
    # to_prompt reproduces the executor-facing shape
    prompt = spec.to_prompt()
    assert prompt["2"]["inputs"]["any"] == {"originId": "1"}
    assert prompt["1"]["inputs"]["text"] == "hi"


def test_parse_graph_defaults_name_to_type():
    spec = parse_graph({"1": {"type": "nsString", "inputs": {}}})
    assert spec.nodes["1"].name == "nsString"


def test_parse_graph_rejects_non_object():
    with pytest.raises(ParseError):
        parse_graph([1, 2, 3])


def test_parse_graph_rejects_missing_type():
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"name": "x", "inputs": {}}})
    assert exc.value.path == "1.type"


def test_parse_graph_rejects_bad_inputs_type():
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"type": "nsString", "inputs": "nope"}})
    assert exc.value.path == "1.inputs"


def test_parse_graph_rejects_dangling_edge():
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"type": "ConsoleLog", "inputs": {"any": {"originId": "99"}}}})
    assert exc.value.path == "1.inputs.any"
    assert "does not reference" in exc.value.message


def test_parse_graph_rejects_self_loop():
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"type": "ConsoleLog", "inputs": {"any": {"originId": "1"}}}})
    assert "self-loop" in exc.value.message


def test_parse_graph_rejects_empty_origin_id():
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"type": "ConsoleLog", "inputs": {"any": {"originId": ""}}}})
    assert exc.value.path == "1.inputs.any"


# --- parse_graph with contracts ---
def test_parse_graph_rejects_unknown_type_with_contracts():
    contracts = contracts_from_nodes(NODES)
    with pytest.raises(ParseError) as exc:
        parse_graph({"1": {"type": "Nope", "inputs": {}}}, contracts=contracts)
    assert exc.value.path == "1.type"


def test_parse_graph_accepts_known_types_with_contracts():
    contracts = contracts_from_nodes(NODES)
    spec = parse_graph(simple_prompt(), contracts=contracts)
    assert set(spec.nodes) == {"1", "2"}


def test_parse_graph_rejects_kind_mismatch():
    contracts = contracts_from_nodes(NODES)
    # nsString outputs 'string' but NumberSink.value expects 'number'
    payload = {
        "1": {"type": "nsString", "inputs": {"text": "x"}},
        "2": {"type": "NumberSink", "inputs": {"value": {"originId": "1"}}},
    }
    with pytest.raises(ParseError) as exc:
        parse_graph(payload, contracts=contracts)
    assert exc.value.path == "2.inputs.value"
    assert "assignable" in exc.value.message


def test_parse_graph_allows_star_into_concrete_via_edge():
    contracts = contracts_from_nodes(NODES)
    # ConsoleLog outputs '*', which is assignable into NumberSink.value ('number')
    payload = {
        "1": {"type": "ConsoleLog", "inputs": {"any": "x"}},
        "2": {"type": "NumberSink", "inputs": {"value": {"originId": "1"}}},
    }
    spec = parse_graph(payload, contracts=contracts)
    assert spec.nodes["2"].links()["value"].origin_id == "1"


# --- contracts ---
def test_contract_from_python_class():
    contract = contract_from_python_class("nsString", FakeString)
    assert contract.output_kind == "string"
    assert contract.input_kinds["text"] == TOP_KIND
    assert "text" in contract.required


# --- lint_graph (soft warnings) ---
def test_lint_graph_warns_unknown_input():
    contracts = contracts_from_nodes(NODES)
    spec = parse_graph({"1": {"type": "nsString", "inputs": {"bogus": "x"}}}, contracts=contracts)
    warnings = lint_graph(spec, contracts)
    assert any("bogus" in w and "not a declared input" in w for w in warnings)


def test_lint_graph_warns_missing_required():
    contracts = contracts_from_nodes(NODES)
    spec = parse_graph({"1": {"type": "nsString", "inputs": {}}}, contracts=contracts)
    warnings = lint_graph(spec, contracts)
    assert any("text" in w and "required" in w for w in warnings)


def test_lint_graph_clean_when_valid():
    contracts = contracts_from_nodes(NODES)
    spec = parse_graph(simple_prompt(), contracts=contracts)
    assert lint_graph(spec, contracts) == []
