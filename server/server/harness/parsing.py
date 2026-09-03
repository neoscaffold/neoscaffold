"""Parse, don't validate.

Untrusted graph payloads are parsed once, at the edge, into typed structures
(:class:`GraphSpec` / :class:`NodeSpec`). Downstream code consumes the typed
structure and never re-inspects the raw dict. A successfully parsed graph is
correct-by-construction for the checks performed here: shape, referential
integrity (every ``originId`` points at a declared node), no self-loops, known
node types, and kind assignability across declared edges.

See ``harness.md`` §1–§2.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List, Mapping, Optional, Union

# The top type of the kind lattice: assignable to and from everything.
TOP_KIND = "*"


class ParseError(Exception):
    """Raised when a payload cannot be parsed into a typed structure.

    Carries a machine-readable ``path`` (dotted location of the problem) and a
    human-readable ``message`` so callers can repair, reject, or escalate.
    """

    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"{path or '<root>'}: {message}")


def is_assignable(from_kind: str, to_kind: str) -> bool:
    """Return whether a value of ``from_kind`` may flow into ``to_kind``.

    ``*`` is the top type (gradual typing): assignable to and from anything.
    Concrete kinds are assignable only to themselves or ``*``.
    """
    if from_kind == TOP_KIND or to_kind == TOP_KIND:
        return True
    return from_kind == to_kind


@dataclass(frozen=True)
class InputRef:
    """A node input that is wired to another node's output (an edge)."""

    origin_id: str


@dataclass(frozen=True)
class NodeContract:
    """The typed contract of a node, derived from its ``INPUT``/``OUTPUT``."""

    type: str
    input_kinds: Mapping[str, str]
    required: FrozenSet[str]
    output_kind: str


@dataclass
class NodeSpec:
    """One node in a prompt-graph. ``inputs`` values are literals or ``InputRef``."""

    node_id: str
    type: str
    name: str
    inputs: Dict[str, Union[InputRef, Any]]

    def links(self) -> Dict[str, InputRef]:
        return {k: v for k, v in self.inputs.items() if isinstance(v, InputRef)}


@dataclass
class GraphSpec:
    """A parsed, structurally-valid prompt-graph."""

    nodes: Dict[str, NodeSpec]

    def to_prompt(self) -> Dict[str, Any]:
        """Render back to the executor's ``prompt`` dict format."""
        out: Dict[str, Any] = {}
        for node_id, spec in self.nodes.items():
            inputs: Dict[str, Any] = {}
            for name, value in spec.inputs.items():
                if isinstance(value, InputRef):
                    inputs[name] = {"originId": value.origin_id}
                else:
                    inputs[name] = value
            out[node_id] = {"type": spec.type, "name": spec.name, "inputs": inputs}
        return out


def contract_from_python_class(type_name: str, cls: Any) -> NodeContract:
    """Build a :class:`NodeContract` from a node ``python_class``."""
    inp = getattr(cls, "INPUT", {}) or {}
    required = inp.get("required_inputs", {}) or {}
    optional = inp.get("optional_inputs", {}) or {}
    input_kinds: Dict[str, str] = {}
    for name, spec in {**required, **optional}.items():
        input_kinds[name] = (spec or {}).get("kind", TOP_KIND)
    out = getattr(cls, "OUTPUT", {}) or {}
    return NodeContract(
        type=type_name,
        input_kinds=input_kinds,
        required=frozenset(required.keys()),
        output_kind=out.get("kind", TOP_KIND),
    )


def contracts_from_nodes(nodes: Mapping[str, Any]) -> Dict[str, NodeContract]:
    """Build contracts from a ``server.nodes``-style registration mapping."""
    contracts: Dict[str, NodeContract] = {}
    for name, registration in nodes.items():
        if isinstance(registration, dict):
            cls = registration.get("python_class")
        else:
            cls = registration
        if cls is not None:
            contracts[name] = contract_from_python_class(name, cls)
    return contracts


def _parse_input_value(value: Any) -> Union[InputRef, Any]:
    # A dict carrying ``originId`` is an edge; any other value is a literal
    # (this mirrors the executor's prompt_to_graph semantics).
    if isinstance(value, dict) and "originId" in value:
        origin = value["originId"]
        if not isinstance(origin, str) or not origin:
            raise ValueError("originId must be a non-empty string")
        return InputRef(origin_id=origin)
    return value


def parse_node(node_id: str, raw: Any) -> NodeSpec:
    """Parse a single node dict into a :class:`NodeSpec` (structure only)."""
    if not isinstance(node_id, str) or not node_id:
        raise ParseError("", "node id must be a non-empty string")
    if not isinstance(raw, dict):
        raise ParseError(node_id, "node must be an object")

    node_type = raw.get("type")
    if not isinstance(node_type, str) or not node_type:
        raise ParseError(f"{node_id}.type", "type must be a non-empty string")

    name = raw.get("name", node_type)
    if not isinstance(name, str) or not name:
        name = node_type

    raw_inputs = raw.get("inputs", {})
    if raw_inputs is None:
        raw_inputs = {}
    if not isinstance(raw_inputs, dict):
        raise ParseError(f"{node_id}.inputs", "inputs must be an object")

    inputs: Dict[str, Union[InputRef, Any]] = {}
    for input_name, value in raw_inputs.items():
        try:
            inputs[input_name] = _parse_input_value(value)
        except ValueError as exc:
            raise ParseError(f"{node_id}.inputs.{input_name}", str(exc))

    return NodeSpec(node_id=node_id, type=node_type, name=name, inputs=inputs)


def parse_graph(
    payload: Any,
    *,
    contracts: Optional[Mapping[str, NodeContract]] = None,
) -> GraphSpec:
    """Parse an untrusted prompt-graph payload into a typed :class:`GraphSpec`.

    Hard errors (raise :class:`ParseError`): payload not an object, node not an
    object, missing/empty ``type``, bad ``inputs`` type, malformed ``originId``,
    dangling edge (``originId`` not a declared node), self-loop, unknown node
    ``type`` (only when ``contracts`` is supplied), and kind mismatch across a
    declared edge (only when ``contracts`` is supplied).
    """
    if not isinstance(payload, dict):
        raise ParseError("", "graph must be an object of node_id -> node")

    nodes: Dict[str, NodeSpec] = {}
    for node_id, raw in payload.items():
        nodes[node_id] = parse_node(node_id, raw)

    for node_id, spec in nodes.items():
        # Referential integrity + no self-loops.
        for input_name, ref in spec.links().items():
            if ref.origin_id == node_id:
                raise ParseError(
                    f"{node_id}.inputs.{input_name}",
                    "input references its own node (self-loop)",
                )
            if ref.origin_id not in nodes:
                raise ParseError(
                    f"{node_id}.inputs.{input_name}",
                    f"originId '{ref.origin_id}' does not reference a declared node",
                )

        if contracts is not None:
            if spec.type not in contracts:
                raise ParseError(f"{node_id}.type", f"unknown node type '{spec.type}'")

    if contracts is not None:
        for node_id, spec in nodes.items():
            target = contracts[spec.type]
            for input_name, ref in spec.links().items():
                # Only type-check inputs the contract declares; extra inputs are
                # tolerated by the executor and handled as warnings by lint_graph.
                if input_name not in target.input_kinds:
                    continue
                origin = contracts[nodes[ref.origin_id].type]
                if not is_assignable(origin.output_kind, target.input_kinds[input_name]):
                    raise ParseError(
                        f"{node_id}.inputs.{input_name}",
                        (
                            f"kind '{origin.output_kind}' from '{ref.origin_id}' is not "
                            f"assignable to '{target.input_kinds[input_name]}'"
                        ),
                    )

    return GraphSpec(nodes=nodes)


# Inputs that are credentials/config, never auto-wired by connectivity repair.
CREDENTIAL_INPUTS = frozenset(
    {"api_key", "key", "token", "password", "secret", "authorization", "timeout", "model"}
)
# Required string fields the planner should fill from the user's intent.
PROMPT_INPUTS = frozenset({"prompt", "text", "message", "instruction"})


def _is_edge_value(value: Any) -> bool:
    return isinstance(value, dict) and "originId" in value


def _is_unfilled(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, InputRef):
        return False
    if _is_edge_value(value):
        return False
    return value == ""


def edge_count(spec: GraphSpec) -> int:
    return sum(len(node.links()) for node in spec.nodes.values())


def _sorted_node_ids(ids: List[str]) -> List[str]:
    def key(node_id: str):
        try:
            return (0, int(node_id))
        except (TypeError, ValueError):
            return (1, node_id)

    return sorted(ids, key=key)


def lint_graph(
    spec: GraphSpec,
    contracts: Optional[Mapping[str, NodeContract]] = None,
) -> List[str]:
    """Return soft warnings for a parsed graph (never raises).

    Warnings: a declared required input is neither wired nor given a literal, an
    input name is not declared by the node's contract, a required literal is
    empty, or a multi-node graph has no wires. These are surfaced into agent
    context rather than hard-failed (harness.md §4, §6).
    """
    warnings: List[str] = []
    n_nodes = len(spec.nodes)
    n_edges = edge_count(spec)
    if n_nodes >= 2 and n_edges == 0:
        warnings.append(
            f"graph has {n_nodes} nodes but no wires; the workflow is disconnected"
        )

    if contracts is None:
        return warnings
    for node_id, node_spec in spec.nodes.items():
        contract = contracts.get(node_spec.type)
        if contract is None:
            continue
        for input_name in node_spec.inputs:
            if input_name not in contract.input_kinds:
                warnings.append(
                    f"{node_id}.inputs.{input_name}: not a declared input of "
                    f"'{node_spec.type}'"
                )
        for required in contract.required:
            if required not in node_spec.inputs:
                warnings.append(
                    f"{node_id}.inputs.{required}: required input is not provided"
                )
            elif _is_unfilled(node_spec.inputs[required]):
                warnings.append(
                    f"{node_id}.inputs.{required}: required input is empty"
                )
    return warnings


def repair_connectivity(
    payload: Any,
    *,
    contracts: Optional[Mapping[str, NodeContract]] = None,
    user_prompt: Optional[str] = None,
) -> tuple:
    """Bounded connectivity repair (harness.md §6). Never invents nodes.

    1. Fill empty ``prompt``/``text`` literals from ``user_prompt``.
    2. Wire unused producers into unwired required dataflow inputs, in node-id
       order, only when kinds are assignable. Credential fields are skipped.

    Returns ``(payload, repairs)``.
    """
    repairs: List[str] = []
    if not isinstance(payload, dict) or not payload:
        return payload if isinstance(payload, dict) else {}, repairs

    intent = (user_prompt or "").strip()
    prompt_targets = [
        node_id
        for node_id, node in payload.items()
        if isinstance(node, dict) and node.get("type")
    ]
    n_promptable = 0
    if contracts is not None:
        for node_id in prompt_targets:
            node_type = payload[node_id].get("type")
            contract = contracts.get(node_type)
            if contract is None:
                continue
            if any(name in contract.input_kinds for name in PROMPT_INPUTS):
                n_promptable += 1

    agent_index = 0
    for node_id in _sorted_node_ids(list(payload)):
        node = payload.get(node_id)
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            inputs = {}
            node["inputs"] = inputs
        node_type = node.get("type")
        contract = contracts.get(node_type) if contracts is not None else None
        fill_names = list(PROMPT_INPUTS)
        if contract is not None:
            fill_names = [n for n in fill_names if n in contract.input_kinds]
        filled_this_node = False
        for name in fill_names:
            if name in CREDENTIAL_INPUTS:
                continue
            if not _is_unfilled(inputs.get(name)):
                continue
            if not intent:
                continue
            if n_promptable > 1:
                agent_index += 1
                inputs[name] = f"{intent} (agent {agent_index})"
            else:
                inputs[name] = intent
            repairs.append(f"filled '{node_id}.{name}' from the user prompt")
            filled_this_node = True
            if filled_this_node:
                break

    if contracts is None:
        return payload, repairs

    used_origins = set()
    for node in payload.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs") or {}
        if not isinstance(inputs, dict):
            continue
        for value in inputs.values():
            if _is_edge_value(value):
                origin = value.get("originId")
                if origin:
                    used_origins.add(origin)

    for target_id in _sorted_node_ids(list(payload)):
        node = payload.get(target_id)
        if not isinstance(node, dict):
            continue
        contract = contracts.get(node.get("type"))
        if contract is None:
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            inputs = {}
            node["inputs"] = inputs
        for required in contract.required:
            if required in CREDENTIAL_INPUTS or required in PROMPT_INPUTS:
                continue
            if not _is_unfilled(inputs.get(required)):
                continue
            target_kind = contract.input_kinds.get(required, TOP_KIND)
            origin_id = _next_unused_producer(
                payload,
                contracts,
                used_origins,
                target_id,
                target_kind,
            )
            if origin_id is None:
                continue
            inputs[required] = {"originId": origin_id}
            used_origins.add(origin_id)
            repairs.append(
                f"wired '{origin_id}' -> '{target_id}.{required}'"
            )

    return payload, repairs


def _next_unused_producer(
    payload: Mapping[str, Any],
    contracts: Mapping[str, NodeContract],
    used_origins: set,
    target_id: str,
    target_kind: str,
) -> Optional[str]:
    """Pick the earliest unused producer whose output is assignable to ``target_kind``.

    Only origins that appear *before* ``target_id`` in id-order are considered, so
    the repair cannot introduce cycles.
    """
    ordered = _sorted_node_ids(list(payload))
    try:
        limit = ordered.index(target_id)
    except ValueError:
        limit = len(ordered)
    for origin_id in ordered[:limit]:
        if origin_id in used_origins or origin_id == target_id:
            continue
        origin = payload.get(origin_id)
        if not isinstance(origin, dict):
            continue
        origin_contract = contracts.get(origin.get("type"))
        if origin_contract is None:
            continue
        if is_assignable(origin_contract.output_kind, target_kind):
            return origin_id
    return None


VALUE_PATH_NODE = "ValuePath"

# Default field to extract when a node returns a dict that a string consumer
# should not swallow whole.
DICT_OUTPUT_PATHS = {
    "CerebrasAgent": "summary",
    "CerebrasAgentAsync": "summary",
    "SwarmSolverNode": "code",
}

# Inputs that expect a scalar/text after a dict has been deconstructed.
STRINGISH_CONSUMER_INPUTS = {
    "ConcatString": frozenset({"a", "b"}),
    "StringJoin": frozenset({"delimiter"}),
    "ConsoleLog": frozenset({"any"}),
    "PromptNode": frozenset({"input"}),
}


def _next_node_id(payload: Mapping[str, Any]) -> str:
    highest = 0
    for node_id in payload:
        try:
            highest = max(highest, int(node_id))
        except (TypeError, ValueError):
            continue
    return str(highest + 1)


def _default_value_path(origin_type: str) -> str:
    return DICT_OUTPUT_PATHS.get(origin_type, "summary")


def insert_value_path_adapters(
    payload: Any,
    *,
    contracts: Optional[Mapping[str, NodeContract]] = None,
) -> tuple:
    """Insert ``ValuePath`` nodes between dict producers and string consumers.

    Bounded repair (harness.md §6): only inserts ``ValuePath``, only when the
    origin type is a known dict-output node (or already a ValuePath with an
    empty path). Never invents other node types or credentials.
    """
    repairs: List[str] = []
    if not isinstance(payload, dict) or not payload:
        return payload if isinstance(payload, dict) else {}, repairs
    if contracts is not None and VALUE_PATH_NODE not in contracts:
        return payload, repairs

    # Fill empty value_path literals from the wired origin's default field.
    for node_id, node in list(payload.items()):
        if not isinstance(node, dict) or node.get("type") != VALUE_PATH_NODE:
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        if not _is_unfilled(inputs.get("value_path")):
            continue
        object_ref = inputs.get("object")
        origin_type = ""
        if _is_edge_value(object_ref):
            origin = payload.get(object_ref.get("originId"))
            if isinstance(origin, dict):
                origin_type = origin.get("type") or ""
        inputs["value_path"] = _default_value_path(origin_type)
        repairs.append(
            f"filled '{node_id}.value_path' with '{inputs['value_path']}'"
        )

    splices: List[tuple] = []
    for target_id, node in payload.items():
        if not isinstance(node, dict):
            continue
        target_type = node.get("type")
        if target_type == VALUE_PATH_NODE:
            continue
        consumer_inputs = STRINGISH_CONSUMER_INPUTS.get(target_type)
        if not consumer_inputs:
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for input_name, value in inputs.items():
            if input_name not in consumer_inputs or not _is_edge_value(value):
                continue
            origin_id = value.get("originId")
            origin = payload.get(origin_id)
            if not isinstance(origin, dict):
                continue
            origin_type = origin.get("type")
            if origin_type == VALUE_PATH_NODE:
                continue
            if origin_type not in DICT_OUTPUT_PATHS:
                continue
            splices.append((target_id, input_name, origin_id, origin_type))

    for target_id, input_name, origin_id, origin_type in splices:
        path = _default_value_path(origin_type)
        adapter_id = _next_node_id(payload)
        payload[adapter_id] = {
            "type": VALUE_PATH_NODE,
            "name": f"path {path}",
            "inputs": {
                "object": {"originId": origin_id},
                "value_path": path,
            },
        }
        payload[target_id]["inputs"][input_name] = {"originId": adapter_id}
        repairs.append(
            f"inserted ValuePath '{adapter_id}' ({path}) between "
            f"'{origin_id}' and '{target_id}.{input_name}'"
        )

    return payload, repairs
