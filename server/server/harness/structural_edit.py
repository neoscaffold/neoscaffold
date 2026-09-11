"""Deterministic structural edits for an existing prompt-graph.

The LLM planner is instructed to emit widget_edits for value tweaks and a
full ``prompt`` only when adding nodes. That leaves rewires, loop/if
control edges, and "make those changes" as thoughts with no graph mutation.
This module applies those edits to the current workflow so the harness
cannot report a plan without writing the edges.
"""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence

from .parsing import _next_node_id
from .workflows import import_workflow

AGENT_TYPES = ("CursorAgent", "CerebrasAgent", "CerebrasAgentAsync")
_ORDINALS = {
    "1st": 1,
    "first": 1,
    "2nd": 2,
    "second": 2,
    "3rd": 3,
    "third": 3,
    "last": -1,
}

_STRUCTURAL_RE = re.compile(
    r"(wire|rewire|connect|unwire|infinite|runaway|endwhileloop|"
    r"end while|make (the |those )?changes|apply (the |those )?changes|"
    r"fix (the )?(workflow|loop|if)|before the endwhile|"
    r"output into endwhile|loop control|if statement|if/loop)",
    re.I,
)
_APPLY_RE = re.compile(
    r"\b(make (the |those )?changes|apply (the |those )?changes|"
    r"do it(?: for me)?|you need to make)\b",
    re.I,
)
_LOOP_FIX_RE = re.compile(
    r"(infinite|runaway|loop control|if statement|fix (the )?(workflow|loop|if)|"
    r"remaining|color_workflow_active|decrement)",
    re.I,
)
_AGENT_WIRE_RE = re.compile(
    r"(cursoragent|cerebrasagent|2nd|second|endwhileloop|end while|"
    r"before the endwhile|output into)",
    re.I,
)
_NODE_INTO_RE = re.compile(
    r"node\s+(\d+)\b.{0,80}?\b(EndWhileLoop|EndIfEqual|WhileLoop|ConsoleLog)\b",
    re.I,
)
_NTH_TYPE_RE = re.compile(
    r"(?:(\d+)(?:st|nd|rd|th)|first|second|third|last)\s+"
    r"([A-Za-z][A-Za-z0-9_]*)",
    re.I,
)


@dataclass
class StructuralEdit:
    prompt: Dict[str, Any]
    patch: Dict[str, Any] = field(
        default_factory=lambda: {"add_nodes": {}, "wire": [], "set": []}
    )
    plan: List[str] = field(default_factory=list)
    thoughts: str = ""
    changed: bool = False


def is_structural_request(
    text: str, history: Optional[Sequence[Any]] = None
) -> bool:
    blob = f"{text or ''} {_history_text(history)}"
    return bool(_STRUCTURAL_RE.search(blob))


def current_prompt(workflow: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Normalize a LiteGraph / prompt-graph / {prompt:...} payload."""
    if not isinstance(workflow, Mapping) or not workflow:
        return {}
    imported = import_workflow(dict(workflow))
    if imported:
        return imported
    return {
        str(key): value
        for key, value in workflow.items()
        if isinstance(value, dict) and value.get("type")
    }


def apply_structural_edits(
    prompt: Mapping[str, Any],
    text: str,
    history: Optional[Sequence[Any]] = None,
) -> StructuralEdit:
    """Rewrite loop/if/agent edges on ``prompt``. Never invents a new workflow."""
    graph = copy.deepcopy(dict(prompt or {}))
    result = StructuralEdit(prompt=graph)
    if not graph:
        return result

    lowered = f"{text or ''} {_history_text(history)}"
    wants_loop = bool(_LOOP_FIX_RE.search(lowered))
    wants_agent = bool(_AGENT_WIRE_RE.search(lowered))
    wants_apply = bool(_APPLY_RE.search(lowered))
    has_while = bool(_nodes_of_type(graph, "WhileLoop"))

    if has_while and (wants_loop or wants_apply or wants_agent):
        if _repair_while_termination(graph, result.patch, result.plan):
            result.changed = True
        if _wire_agent_into_end_while(graph, result.patch, result.plan, lowered):
            result.changed = True

    if _apply_explicit_wire(graph, result.patch, result.plan, text or ""):
        result.changed = True

    result.prompt = graph
    if result.changed:
        result.thoughts = (
            "Applied structural wiring on the current workflow: loop "
            "termination and/or the agent → EndWhileLoop chain."
        )
    return result


def patch_has_work(patch: Optional[Mapping[str, Any]]) -> bool:
    if not isinstance(patch, dict):
        return False
    return bool(patch.get("add_nodes") or patch.get("wire") or patch.get("set"))


def _history_text(history: Optional[Sequence[Any]]) -> str:
    if not history:
        return ""
    parts: List[str] = []
    for item in history:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, Mapping):
            for key in ("content", "thoughts", "output"):
                value = item.get(key)
                if isinstance(value, str):
                    parts.append(value)
            plan = item.get("plan")
            if isinstance(plan, list):
                parts.extend(str(step) for step in plan)
    return "\n".join(parts)


def _nodes_of_type(prompt: Mapping[str, Any], *types: str) -> List[str]:
    wanted = set(types)
    return [
        str(node_id)
        for node_id, node in prompt.items()
        if isinstance(node, dict) and node.get("type") in wanted
    ]


def _inputs(node: Dict[str, Any]) -> Dict[str, Any]:
    inputs = node.get("inputs")
    if not isinstance(inputs, dict):
        inputs = {}
        node["inputs"] = inputs
    return inputs


def _is_edge(value: Any) -> bool:
    return isinstance(value, dict) and value.get("originId") is not None


def _origin(value: Any) -> Optional[str]:
    if _is_edge(value):
        return str(value.get("originId"))
    return None


def _literal(value: Any) -> Any:
    if _is_edge(value):
        return None
    return value


def _set_edge(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    target: str,
    input_name: str,
    origin: str,
    plan: List[str],
) -> bool:
    if target not in prompt or origin not in prompt:
        return False
    inputs = _inputs(prompt[target])
    if _origin(inputs.get(input_name)) == str(origin):
        return False
    inputs[input_name] = {"originId": str(origin)}
    patch.setdefault("wire", []).append(
        {"target": str(target), "input": input_name, "originId": str(origin)}
    )
    origin_type = prompt[origin].get("type")
    target_type = prompt[target].get("type")
    plan.append(
        f"Wire {origin_type} {origin} → {target_type} {target}.{input_name}."
    )
    return True


def _set_literal(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    target: str,
    input_name: str,
    value: Any,
    plan: List[str],
) -> bool:
    if target not in prompt:
        return False
    inputs = _inputs(prompt[target])
    if inputs.get(input_name) == value:
        return False
    inputs[input_name] = value
    patch.setdefault("set", []).append(
        {"node_id": str(target), "input": input_name, "value": value}
    )
    plan.append(
        f"Set {prompt[target].get('type')} {target}.{input_name} = {value!r}."
    )
    return True


def _add_node(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    node_type: str,
    name: str,
    inputs: Dict[str, Any],
) -> str:
    node_id = _next_node_id(prompt)
    spec = {"type": node_type, "name": name, "inputs": dict(inputs)}
    prompt[node_id] = spec
    patch.setdefault("add_nodes", {})[node_id] = spec
    return node_id


def _memory_key(prompt: Dict[str, Any], node_id: str) -> Optional[str]:
    node = prompt.get(node_id)
    if not isinstance(node, dict):
        return None
    key = _literal(_inputs(node).get("key"))
    if isinstance(key, str) and key:
        return key
    origin = _origin(_inputs(node).get("key"))
    if origin and origin in prompt:
        text = _literal(_inputs(prompt[origin]).get("text"))
        if isinstance(text, str) and text:
            return text
    return None


def _string_literal(prompt: Dict[str, Any], node_id: str) -> Optional[str]:
    node = prompt.get(node_id)
    if not isinstance(node, dict):
        return None
    text = _literal(_inputs(node).get("text"))
    return text if isinstance(text, str) and text else None


def _find_remaining_key(prompt: Dict[str, Any]) -> Optional[str]:
    for node_id in _nodes_of_type(prompt, "nsString"):
        text = _string_literal(prompt, node_id)
        if text and "remaining" in text.lower():
            return text
    for node_id in _nodes_of_type(prompt, "MemoryWrite", "MemoryRead"):
        key = _memory_key(prompt, node_id)
        if key and "remaining" in key.lower():
            return key
    return None


def _writes_of_key(prompt: Dict[str, Any], key: str) -> List[str]:
    return [
        node_id
        for node_id in _nodes_of_type(prompt, "MemoryWrite")
        if _memory_key(prompt, node_id) == key
    ]


def _subtract_nodes(prompt: Dict[str, Any]) -> List[str]:
    return _nodes_of_type(prompt, "Subtract")


def _repair_while_termination(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    plan: List[str],
) -> bool:
    """Make a WhileLoop finite via remaining decrement in the end-loop chain.

    The color-workflow failure mode is: Subtract runs, but the MemoryWrite of
    ``remaining`` is not an ancestor of EndIfEqual/EndWhileLoop, so lazy
    evaluation never stores the decrement. The IfEqual true-branch flag write
    is also skipped on the common (not-yet-zero) path, so EndIfEqual hangs or
    the loop never sees a false condition.
    """
    loops = _nodes_of_type(prompt, "WhileLoop")
    ends = _nodes_of_type(prompt, "EndWhileLoop")
    if not loops or not ends:
        return False

    loop_id = loops[0]
    end_id = ends[0]
    remaining_key = _find_remaining_key(prompt)
    changed = False

    if remaining_key:
        condition = _literal(_inputs(prompt[loop_id]).get("condition_key"))
        if condition != remaining_key:
            changed |= _set_literal(
                prompt,
                patch,
                loop_id,
                "condition_key",
                remaining_key,
                plan,
            )

        subtracts = _subtract_nodes(prompt)
        writes = _writes_of_key(prompt, remaining_key)
        # Prefer a write whose value is the Subtract (in-loop decrement).
        decrement_write = None
        subtract_id = subtracts[0] if subtracts else None
        if subtract_id:
            for write_id in writes:
                if _origin(_inputs(prompt[write_id]).get("value")) == subtract_id:
                    decrement_write = write_id
                    break
        if decrement_write is None and writes:
            # Skip the init write (value is a literal integer node).
            for write_id in writes:
                origin = _origin(_inputs(prompt[write_id]).get("value"))
                if origin and prompt.get(origin, {}).get("type") != "nsInteger":
                    decrement_write = write_id
                    break

        ifs = _nodes_of_type(prompt, "IfEqual")
        if subtract_id and decrement_write and ifs:
            if_id = ifs[0]
            sync_id = _existing_sync(prompt, subtract_id, decrement_write)
            if sync_id is None:
                sync_id = _add_node(
                    prompt,
                    patch,
                    "PassThrough",
                    "remaining decrement",
                    {
                        "value": {"originId": subtract_id},
                        "ignored_input": {"originId": decrement_write},
                    },
                )
                plan.append(
                    f"Synchronize Subtract {subtract_id} with MemoryWrite "
                    f"{decrement_write} so remaining is stored each iteration."
                )
                changed = True
            changed |= _set_edge(
                prompt, patch, if_id, "a", sync_id, plan
            )
            zero_id = _origin(_inputs(prompt[if_id]).get("b"))
            if zero_id is None or _literal(_inputs(prompt.get(zero_id, {})).get("value")) not in (0, 0.0):
                for node_id in _nodes_of_type(prompt, "nsInteger"):
                    if _literal(_inputs(prompt[node_id]).get("value")) in (0, 0.0):
                        changed |= _set_edge(
                            prompt, patch, if_id, "b", node_id, plan
                        )
                        break

            endifs = _nodes_of_type(prompt, "EndIfEqual")
            if endifs:
                # EndIfEqual must not wait only on the true-branch flag write;
                # that node is skipped on the common remaining != 0 path.
                changed |= _set_edge(
                    prompt, patch, endifs[0], "node_inputs", sync_id, plan
                )

    changed |= _set_edge(prompt, patch, end_id, "WhileLoop", loop_id, plan)
    return changed


def _existing_sync(
    prompt: Dict[str, Any], value_id: str, ignored_id: str
) -> Optional[str]:
    for node_id in _nodes_of_type(prompt, "PassThrough"):
        inputs = _inputs(prompt[node_id])
        if (
            _origin(inputs.get("value")) == value_id
            and _origin(inputs.get("ignored_input")) == ignored_id
        ):
            return node_id
    return None


def _pick_agent(prompt: Dict[str, Any], text: str) -> Optional[str]:
    node_match = re.search(r"\bnode\s+(\d+)\b", text, re.I)
    if node_match and node_match.group(1) in prompt:
        return node_match.group(1)

    nth = _NTH_TYPE_RE.search(text)
    typed: List[str] = []
    if nth:
        type_name = nth.group(2)
        if type_name.lower() == "agent":
            typed = _nodes_of_type(prompt, *AGENT_TYPES)
        else:
            typed = [
                node_id
                for node_id, node in prompt.items()
                if isinstance(node, dict)
                and str(node.get("type", "")).lower() == type_name.lower()
            ]
        token = (nth.group(1) or nth.group(0).split()[0]).lower()
        index = _ORDINALS.get(token)
        if index is None and token.isdigit():
            index = int(token)
        if typed and index == -1:
            return typed[-1]
        if typed and index is not None and 1 <= index <= len(typed):
            return typed[index - 1]

    agents = typed or _nodes_of_type(prompt, *AGENT_TYPES)
    if len(agents) >= 2 and re.search(r"\b(2nd|second)\b", text, re.I):
        return agents[1]
    if len(agents) >= 2:
        return agents[1]
    return agents[-1] if agents else None


def _wire_agent_into_end_while(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    plan: List[str],
    text: str,
) -> bool:
    """Put the requested agent in the EndWhileLoop dependency chain."""
    ends = _nodes_of_type(prompt, "EndWhileLoop")
    agent_id = _pick_agent(prompt, text)
    if not ends or not agent_id:
        return False

    end_id = ends[0]
    loops = _nodes_of_type(prompt, "WhileLoop")
    changed = False
    if loops:
        changed |= _set_edge(prompt, patch, end_id, "WhileLoop", loops[0], plan)

    endifs = _nodes_of_type(prompt, "EndIfEqual")
    endif_id = None
    current_end_in = _origin(_inputs(prompt[end_id]).get("node_inputs"))
    if current_end_in and prompt.get(current_end_in, {}).get("type") == "EndIfEqual":
        endif_id = current_end_in
    elif endifs:
        endif_id = endifs[0]

    agent_inputs = _inputs(prompt[agent_id])
    prompt_origin = _origin(agent_inputs.get("prompt"))
    if endif_id and prompt_origin != endif_id:
        already_gated = False
        if prompt_origin and prompt.get(prompt_origin, {}).get("type") == "PassThrough":
            if _origin(_inputs(prompt[prompt_origin]).get("ignored_input")) == endif_id:
                already_gated = True
        if not already_gated:
            gate_value = {"originId": prompt_origin} if prompt_origin else ""
            gate_id = _add_node(
                prompt,
                patch,
                "PassThrough",
                "agent after if",
                {
                    "value": gate_value,
                    "ignored_input": {"originId": endif_id},
                },
            )
            plan.append(
                f"Gate {prompt[agent_id].get('type')} {agent_id} on "
                f"EndIfEqual {endif_id} so it runs in the loop body."
            )
            _set_edge(prompt, patch, agent_id, "prompt", gate_id, plan)
            changed = True

    if _origin(_inputs(prompt[end_id]).get("node_inputs")) != agent_id:
        changed |= _set_edge(
            prompt, patch, end_id, "node_inputs", agent_id, plan
        )
    return changed


def _apply_explicit_wire(
    prompt: Dict[str, Any],
    patch: Dict[str, Any],
    plan: List[str],
    text: str,
) -> bool:
    match = _NODE_INTO_RE.search(text)
    if not match:
        return False
    origin = match.group(1)
    target_type = match.group(2)
    if origin not in prompt:
        return False
    targets = _nodes_of_type(prompt, target_type)
    if not targets:
        return False
    input_name = "node_inputs"
    if target_type in ("EndWhileLoop", "EndForLoop", "EndForEachLoop"):
        input_name = "node_inputs"
    elif target_type == "ConsoleLog":
        input_name = "any"
    elif target_type.endswith("Loop") and not target_type.startswith("End"):
        input_name = "node_inputs"
    return _set_edge(prompt, patch, targets[0], input_name, origin, plan)
