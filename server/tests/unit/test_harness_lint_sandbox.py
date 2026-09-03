"""Tests for server.harness.lint and server.harness.sandbox."""

import time

from server.harness.lint import (
    ERROR,
    WARNING,
    has_errors,
    lint_node,
    lint_registry,
    lint_rule,
)
from server.harness.sandbox import run_guarded


class GoodNode:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "a good node"
    INPUT = {"required_inputs": {"text": {"kind": "*", "name": "text"}}}
    OUTPUT = {"kind": "string", "name": "*", "cacheable": True}

    def evaluate(self, node_inputs):
        return ""


class BadNodeMissingFields:
    # no CATEGORY/SUBCATEGORY/DESCRIPTION, no INPUT/OUTPUT, no evaluate
    pass


class NodeUnknownKind:
    CATEGORY = "core"
    SUBCATEGORY = "x"
    DESCRIPTION = "d"
    INPUT = {"required_inputs": {"a": {"kind": "mystery", "name": "a"}}}
    OUTPUT = {"kind": "string", "name": "*"}

    def evaluate(self, node_inputs):
        return None


class GoodRule:
    CATEGORY = "text"
    SUBCATEGORY = "metrics"
    DESCRIPTION = "rule"
    PARAMETERS = {"required_parameters": {}}

    def evaluate(self, source_input, parameters):
        return {"passed": True}


def test_lint_node_clean():
    assert lint_node("GoodNode", GoodNode) == []


def test_lint_node_reports_missing_fields():
    violations = lint_node("BadNode", BadNodeMissingFields)
    assert has_errors(violations)
    messages = " ".join(v.message for v in violations)
    assert "CATEGORY" in messages
    assert "INPUT" in messages
    assert "OUTPUT" in messages
    assert "evaluate" in messages


def test_lint_node_unknown_kind_is_warning_not_error():
    violations = lint_node("NodeUnknownKind", NodeUnknownKind)
    assert not has_errors(violations)
    assert any(v.level == WARNING and "unknown kind" in v.message for v in violations)


def test_lint_rule_clean():
    assert lint_rule("GoodRule", GoodRule) == []


def test_lint_registry_mixed():
    nodes = {"GoodNode": {"python_class": GoodNode}, "BadNode": {"python_class": BadNodeMissingFields}}
    rules = {"GoodRule": {"python_class": GoodRule}}
    violations = lint_registry(nodes, rules)
    assert has_errors(violations)
    # good node/rule contribute no errors; bad node contributes several
    targets = {v.target for v in violations if v.level == ERROR}
    assert "node:BadNode" in targets
    assert "node:GoodNode" not in targets


def test_lint_registry_missing_python_class():
    violations = lint_registry({"X": {"display_name": "X"}}, {})
    assert any(v.target == "node:X" and "no python_class" in v.message for v in violations)


# --- sandbox ---
def test_run_guarded_success():
    result = run_guarded(lambda a, b: a + b, 2, 3)
    assert result.ok
    assert result.value == 5
    assert not result.timed_out


def test_run_guarded_captures_error():
    def boom():
        raise ValueError("nope")

    result = run_guarded(boom)
    assert not result.ok
    assert isinstance(result.error, ValueError)


def test_run_guarded_timeout():
    result = run_guarded(lambda: time.sleep(2.0), timeout=0.1)
    assert not result.ok
    assert result.timed_out
