"""NeoScaffold engineering harness.

Reliability substrate for v1.0.0: typed boundaries (``parsing``), architecture
lints (``lint``), observability (``observability``), and a sandbox seam
(``sandbox``). See ``harness.md`` at the repository root for the specification.

These utilities are intentionally dependency-free and hoisted into the repo to
avoid dependency hell.
"""

from .parsing import (
    TOP_KIND,
    GraphSpec,
    InputRef,
    NodeContract,
    NodeSpec,
    ParseError,
    contract_from_python_class,
    contracts_from_nodes,
    edge_count,
    is_assignable,
    lint_graph,
    parse_graph,
    repair_connectivity,
)

__all__ = [
    "TOP_KIND",
    "GraphSpec",
    "InputRef",
    "NodeContract",
    "NodeSpec",
    "ParseError",
    "contract_from_python_class",
    "contracts_from_nodes",
    "edge_count",
    "is_assignable",
    "lint_graph",
    "parse_graph",
    "repair_connectivity",
]
