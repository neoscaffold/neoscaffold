"""Suggest an accept-ready graph patch when a run fails."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .parsing import _next_node_id

_LOOP_HEADS = {
    "ForLoop": "EndForLoop",
    "WhileLoop": "EndWhileLoop",
    "ForEachLoop": "EndForEachLoop",
}
_LOOP_LINK = {
    "ForLoop": "ForLoop",
    "WhileLoop": "WhileLoop",
    "ForEachLoop": "ForEachLoop",
}
_BODY_PREF = (
    "ConcatString",
    "StringJoin",
    "CerebrasAgent",
    "CerebrasAgentAsync",
    "PromptNode",
    "PassThrough",
    "ConsoleLog",
    "nsString",
)


def _as_prompt_graph(prompt: Any) -> Dict[str, Any]:
    if not isinstance(prompt, dict):
        return {}
    inner = prompt.get("prompt")
    if isinstance(inner, dict) and any(
        isinstance(value, dict) and value.get("type") for value in inner.values()
    ):
        return inner
    return {
        key: value
        for key, value in prompt.items()
        if isinstance(value, dict) and value.get("type")
    }


def _nodes_of_type(prompt: Dict[str, Any], type_name: str) -> List[str]:
    return [
        node_id
        for node_id, node in prompt.items()
        if isinstance(node, dict) and node.get("type") == type_name
    ]


def patch_has_work(patch: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(patch, dict):
        return False
    return bool(patch.get("add_nodes") or patch.get("wire") or patch.get("set"))


def _is_edge(value: Any) -> bool:
    return isinstance(value, dict) and value.get("originId") is not None


def _pick_loop_body(prompt: Dict[str, Any], loop_id: str, end_kind: str) -> Optional[str]:
    skip = {str(loop_id), * _nodes_of_type(prompt, end_kind)}
    for type_name in _BODY_PREF:
        for node_id in _nodes_of_type(prompt, type_name):
            if node_id not in skip:
                return node_id
    for node_id, node in prompt.items():
        if str(node_id) in skip or not isinstance(node, dict):
            continue
        if node.get("type") in _LOOP_HEADS or str(node.get("type", "")).startswith("End"):
            continue
        return str(node_id)
    return None


def _loop_body_patch(prompt: Dict[str, Any], loop_id: str) -> Optional[Dict[str, Any]]:
    loop = prompt.get(str(loop_id)) if isinstance(prompt, dict) else None
    if not isinstance(loop, dict):
        heads = [
            node_id
            for node_id, node in prompt.items()
            if isinstance(node, dict) and node.get("type") in _LOOP_HEADS
        ]
        if not heads:
            return None
        loop_id = heads[0]
        loop = prompt[loop_id]
    loop_type = loop.get("type")
    end_kind = _LOOP_HEADS.get(loop_type)
    if not end_kind:
        return None
    link_name = _LOOP_LINK[loop_type]
    body_id = _pick_loop_body(prompt, loop_id, end_kind)
    if body_id is None:
        return None

    add_nodes: Dict[str, Any] = {}
    wire: List[Dict[str, str]] = []
    gate_id = None
    for node_id in _nodes_of_type(prompt, "PassThrough"):
        inputs = prompt[node_id].get("inputs") or {}
        ignored = inputs.get("ignored_input")
        if not _is_edge(ignored):
            gate_id = node_id
            break
    if gate_id is None:
        gate_id = _next_node_id(prompt)
        add_nodes[gate_id] = {
            "type": "PassThrough",
            "name": "loop body",
            "inputs": {
                "value": {"originId": body_id},
                "ignored_input": {"originId": str(loop_id)},
            },
        }
    else:
        wire.append(
            {
                "target": gate_id,
                "input": "ignored_input",
                "originId": str(loop_id),
            }
        )
        if not _is_edge((prompt.get(gate_id) or {}).get("inputs", {}).get("value")):
            wire.append({"target": gate_id, "input": "value", "originId": body_id})

    end_ids = _nodes_of_type(prompt, end_kind)
    if end_ids:
        end_id = end_ids[0]
        end_inputs = (prompt.get(end_id) or {}).get("inputs") or {}
        if not _is_edge(end_inputs.get(link_name)):
            wire.append(
                {"target": end_id, "input": link_name, "originId": str(loop_id)}
            )
        if not _is_edge(end_inputs.get("node_inputs")):
            wire.append(
                {"target": end_id, "input": "node_inputs", "originId": gate_id}
            )

    ask = (
        f"The {loop_type} has no body — only {end_kind} is connected. "
        f"Accept this patch to make node {body_id} ({prompt[body_id].get('type')}) "
        "a loop successor via PassThrough?"
    )
    return {
        "ask": ask,
        "suggestion": (
            f"Wire PassThrough.ignored_input from {loop_type} '{loop_id}' and "
            f"feed {end_kind}.node_inputs from that PassThrough so the loop "
            "has a body besides the end node."
        ),
        "patch": {"add_nodes": add_nodes, "wire": wire},
    }


def suggest_execution_fix(
    error_message: str,
    prompt: Optional[Dict[str, Any]] = None,
    node_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Return ``{ask, suggestion, patch, armed}`` for a failed run."""
    message = str(error_message or "")
    graph = _as_prompt_graph(prompt)
    failed = str(node_id) if node_id is not None else ""

    if (
        "connected to this loop other than" in message
        or "should be placed at the end of the loop" in message
    ):
        found = _loop_body_patch(graph, failed)
        if found:
            found["armed"] = patch_has_work(found.get("patch"))
            return found

    if "Only one" in message and "should be connected to this loop" in message:
        return {
            "ask": (
                "This loop has the wrong number of end nodes. "
                "Keep exactly one matching End*Loop wired from the loop head?"
            ),
            "suggestion": (
                "Each ForLoop/WhileLoop/ForEachLoop must have exactly one "
                "matching End* node wired from the loop."
            ),
            "patch": {"add_nodes": {}, "wire": []},
            "armed": False,
        }

    if graph and failed and failed in graph:
        node = graph[failed]
        return {
            "ask": (
                f"Node {failed} ({node.get('type')}) failed: {message} "
                "Want me to try a harness rebuild of this workflow?"
            ),
            "suggestion": message,
            "patch": {"add_nodes": {}, "wire": []},
            "armed": False,
        }

    return {
        "ask": (
            f"The run failed: {message} "
            "Tell me how you want it fixed, or ask the harness to rebuild."
        ),
        "suggestion": message,
        "patch": {"add_nodes": {}, "wire": []},
        "armed": False,
    }
