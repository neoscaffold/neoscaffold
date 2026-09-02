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


def lint_graph(
    spec: GraphSpec,
    contracts: Optional[Mapping[str, NodeContract]] = None,
) -> List[str]:
    """Return soft warnings for a parsed graph (never raises).

    Warnings: a declared required input is neither wired nor given a literal, and
    an input name is not declared by the node's contract. These are surfaced into
    agent context rather than hard-failed (harness.md §4).
    """
    warnings: List[str] = []
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
    return warnings
