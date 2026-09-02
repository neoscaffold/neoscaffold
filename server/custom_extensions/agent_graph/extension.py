"""agent_graph extension: prompt-driven nodes + agent-generated sub-graphs.

Ships the two highest-leverage v1.0.0 primitives as an extension (so the core
executor stays stable):

- ``PromptNode`` — a node triggered by a prompt describing its job. A pluggable
  *responder* produces the output; the default responder is offline and
  deterministic (no API key), so graphs using PromptNode are testable. When an
  LLM key is configured, swap ``RESPONDER`` for an LLM-backed callable.
- ``BuildGraphNode`` — turns a natural-language prompt into a validated
  NeoScaffold sub-graph (agents spinning up agents / Paperclip-style).

See ``harness.md`` and ``docs/ROADMAP_1.0.0.md``.
"""

version = "1.0.0"


def offline_respond(prompt, input_value=None):
    """Deterministic, offline prompt responder.

    Substitutes ``{input}`` in the prompt, or appends the input when present.
    This makes PromptNode fully testable without any external API key.
    """
    text = prompt if isinstance(prompt, str) else ("" if prompt is None else str(prompt))
    if "{input}" in text:
        return text.replace("{input}", "" if input_value is None else str(input_value))
    if input_value not in (None, ""):
        return f"{text}: {input_value}"
    return text


# Pluggable responder seam. Replace with an LLM-backed callable to make
# PromptNode call a model; the offline responder is the default.
RESPONDER = offline_respond


class PromptNode:
    CATEGORY = "agent"
    SUBCATEGORY = "prompt"
    DESCRIPTION = (
        "A prompt-driven node: describe the node's job in natural language and it "
        "produces an output. Offline by default (deterministic templating); can be "
        "backed by an LLM by swapping the responder."
    )

    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "prompt",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        },
        "optional_inputs": {
            "input": {
                "kind": "*",
                "name": "input",
                "widget": {"kind": "string", "name": "input", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        prompt = ""
        input_value = None
        required = node_inputs.get("required_inputs") or {}
        if "prompt" in required:
            prompt = required.get("prompt", {}).get("values", "")
        optional = node_inputs.get("optional_inputs") or {}
        if "input" in optional:
            raw = optional.get("input", {}).get("values")
            input_value = raw if raw not in ("", None) else None
        return RESPONDER(prompt, input_value)


class BuildGraphNode:
    CATEGORY = "agent"
    SUBCATEGORY = "graph"
    DESCRIPTION = (
        "Turns a natural-language prompt into a validated NeoScaffold sub-graph "
        "(agents spinning up agents). Output is a graph spec that can be imported "
        "or executed."
    )

    INPUT = {
        "required_inputs": {
            "prompt": {
                "kind": "prompt",
                "name": "prompt",
                "widget": {"kind": "string", "name": "prompt", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "object",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        # Lazy import to avoid coupling extension load to the server package.
        from server.domain.services.graph_builder import build_graph

        prompt = ""
        required = node_inputs.get("required_inputs") or {}
        if "prompt" in required:
            prompt = required.get("prompt", {}).get("values", "")
        result = build_graph(prompt)
        return result.to_dict()


EXTENSION_MAPPINGS = {
    "name": "AgentGraph",
    "version": version,
    "description": "Prompt-driven nodes and agent-generated graph topology.",
    "javascript_class_name": "AgentGraph",
    "nodes": {
        "PromptNode": {
            "python_class": PromptNode,
            "javascript_class_name": "PromptNode",
            "display_name": "PromptNode",
        },
        "BuildGraphNode": {
            "python_class": BuildGraphNode,
            "javascript_class_name": "BuildGraphNode",
            "display_name": "BuildGraphNode",
        },
    },
    "rules": {},
}
