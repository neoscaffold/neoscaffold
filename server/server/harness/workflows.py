"""Import and export NeoScaffold workflows (prompt-graph or LiteGraph JSON)."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

_JSON_OBJECT = re.compile(r"\{.*\}", re.S)
_SKIP_INPUTS = frozenset({"in_rules", "out_rules"})


def extract_json_value(text: str) -> Optional[Any]:
    """Return the first JSON value embedded in ``text``, or None."""
    raw = (text or "").strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    match = _JSON_OBJECT.search(raw)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def is_prompt_graph(value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return False
    if "nodes" in value and isinstance(value.get("nodes"), list):
        return False
    samples = list(value.values())[:8]
    return all(
        isinstance(node, dict) and isinstance(node.get("type"), str) and node.get("type")
        for node in samples
    )


def is_litegraph_workflow(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("nodes"), list)


def litegraph_to_prompt(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a LiteGraph serialize() payload into a prompt-graph."""
    links_by_id: Dict[Any, Any] = {}
    for link in workflow.get("links") or []:
        if isinstance(link, (list, tuple)) and len(link) >= 5:
            links_by_id[link[0]] = link
        elif isinstance(link, dict) and "id" in link:
            links_by_id[link["id"]] = [
                link.get("id"),
                link.get("origin_id"),
                link.get("origin_slot"),
                link.get("target_id"),
                link.get("target_slot"),
            ]

    prompt: Dict[str, Any] = {}
    for node in workflow.get("nodes") or []:
        if not isinstance(node, dict) or node.get("id") is None:
            continue
        node_id = str(node["id"])
        inputs: Dict[str, Any] = {}
        declared = []
        for slot in node.get("inputs") or []:
            if not isinstance(slot, dict):
                continue
            name = slot.get("name")
            if not name or name in _SKIP_INPUTS:
                continue
            declared.append(name)
            link_id = slot.get("link")
            if link_id is None or link_id not in links_by_id:
                continue
            origin = links_by_id[link_id][1]
            if origin is not None:
                inputs[name] = {"originId": str(origin)}
        unfilled = [name for name in declared if name not in inputs]
        widgets = [v for v in (node.get("widgets_values") or []) if v is not None]
        for name, value in zip(unfilled, widgets):
            inputs[name] = value
        prompt[node_id] = {
            "type": node.get("type") or "",
            "name": node.get("title") or node.get("type") or node_id,
            "inputs": inputs,
        }
    return prompt


def canvas_to_prompt(canvas: Dict[str, Any]) -> Dict[str, Any]:
    """Turn a widget snapshot into a prompt-graph (literals only)."""
    prompt: Dict[str, Any] = {}
    for node_id, node in canvas.items():
        if not isinstance(node, dict) or not node.get("type"):
            continue
        widgets = node.get("widgets") if isinstance(node.get("widgets"), dict) else {}
        prompt[str(node_id)] = {
            "type": node["type"],
            "name": node.get("name") or node["type"],
            "inputs": dict(widgets),
        }
    return prompt


def import_workflow(raw: Any) -> Optional[Dict[str, Any]]:
    """Accept a prompt-graph, ``{prompt: ...}`` envelope, or LiteGraph workflow."""
    if isinstance(raw, str):
        raw = extract_json_value(raw)
    if not isinstance(raw, dict):
        return None
    if is_litegraph_workflow(raw):
        prompt = litegraph_to_prompt(raw)
        return prompt or None
    inner = raw.get("prompt") if isinstance(raw.get("prompt"), dict) else None
    if inner is not None and is_prompt_graph(inner):
        return inner
    if is_prompt_graph(raw):
        return raw
    return None


def export_workflow(
    prompt: Optional[Dict[str, Any]] = None,
    *,
    layout: Optional[Dict[str, Any]] = None,
    litegraph: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Portable export: prompt-graph plus optional LiteGraph serialize payload."""
    exported: Dict[str, Any] = {
        "prompt": dict(prompt or {}),
        "layout": dict(layout or {}),
    }
    if isinstance(litegraph, dict) and litegraph:
        exported["workflow"] = litegraph
    return exported
