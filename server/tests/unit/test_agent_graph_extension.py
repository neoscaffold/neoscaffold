"""Tests for the agent_graph extension (PromptNode, BuildGraphNode)."""

from custom_extensions.agent_graph.extension import (
    EXTENSION_MAPPINGS,
    BuildGraphNode,
    PromptNode,
    offline_respond,
)
from server.harness.lint import has_errors, lint_registry


def _resolved(required=None, optional=None):
    def wrap(d):
        return {k: {"values": v} for k, v in (d or {}).items()}

    return {"required_inputs": wrap(required), "optional_inputs": wrap(optional)}


# --- offline responder ---
def test_offline_respond_substitutes_input():
    assert offline_respond("Say hello to {input}", "world") == "Say hello to world"


def test_offline_respond_appends_input_when_no_placeholder():
    assert offline_respond("Greeting", "hi") == "Greeting: hi"


def test_offline_respond_plain_when_no_input():
    assert offline_respond("just this") == "just this"


# --- PromptNode ---
def test_prompt_node_evaluates_with_input():
    node = PromptNode()
    out = node.evaluate(_resolved({"prompt": "hi {input}"}, {"input": "there"}))
    assert out == "hi there"


def test_prompt_node_evaluates_without_input():
    node = PromptNode()
    out = node.evaluate(_resolved({"prompt": "standalone"}, {"input": ""}))
    assert out == "standalone"


# --- BuildGraphNode ---
def test_build_graph_node_returns_subgraph():
    node = BuildGraphNode()
    out = node.evaluate(_resolved({"prompt": 'log "nested"'}))
    assert isinstance(out, dict)
    assert "prompt" in out and isinstance(out["prompt"], dict)
    types = [n["type"] for n in out["prompt"].values()]
    assert "ConsoleLog" in types


# --- contract lint ---
def test_extension_nodes_pass_contract_lint():
    violations = lint_registry(EXTENSION_MAPPINGS["nodes"], EXTENSION_MAPPINGS.get("rules"))
    assert not has_errors(violations), [str(v) for v in violations]


def test_extension_mappings_shape():
    assert EXTENSION_MAPPINGS["name"] == "AgentGraph"
    assert set(EXTENSION_MAPPINGS["nodes"]) == {"PromptNode", "BuildGraphNode"}
