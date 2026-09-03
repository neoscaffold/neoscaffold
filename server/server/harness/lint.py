"""Architecture lints over loaded extensions (harness.md §3).

Enforces the small, defended set of contract constraints on every registered
node and rule class. Run as ``python -m server.harness.lint`` (exits non-zero on
any error-level violation). Warnings are printed but do not fail the build.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Mapping

# Kinds the harness recognizes today. Unknown kinds warn (not fail) so archetypes
# can introduce new kinds without an immediate CI break.
KNOWN_KINDS = {
    "*",
    "string",
    "number",
    "integer",
    "float",
    "boolean",
    "array",
    "object",
    "rule_group",
    "prompt",
    "control_flow",
    "function",
    "complex",
    "RESPONSE",
}

ERROR = "error"
WARNING = "warning"


@dataclass
class Violation:
    level: str
    target: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.target}: {self.message}"


def _check_input_entries(target: str, input_block: Mapping[str, Any]) -> List[Violation]:
    violations: List[Violation] = []
    for group in ("required_inputs", "optional_inputs"):
        entries = input_block.get(group) or {}
        if not isinstance(entries, dict):
            violations.append(Violation(ERROR, target, f"INPUT.{group} must be an object"))
            continue
        for name, spec in entries.items():
            spec = spec or {}
            if "kind" not in spec:
                violations.append(
                    Violation(ERROR, f"{target}.{group}.{name}", "input is missing 'kind'")
                )
            elif spec["kind"] not in KNOWN_KINDS:
                violations.append(
                    Violation(
                        WARNING,
                        f"{target}.{group}.{name}",
                        f"unknown kind '{spec['kind']}'",
                    )
                )
            if "name" not in spec:
                violations.append(
                    Violation(WARNING, f"{target}.{group}.{name}", "input is missing 'name'")
                )
    return violations


def lint_node(type_name: str, cls: Any) -> List[Violation]:
    """Lint a single node ``python_class`` against the contract."""
    target = f"node:{type_name}"
    violations: List[Violation] = []

    for attr in ("CATEGORY", "SUBCATEGORY", "DESCRIPTION"):
        value = getattr(cls, attr, None)
        if not isinstance(value, str) or not value:
            violations.append(Violation(ERROR, target, f"missing non-empty {attr}"))

    inp = getattr(cls, "INPUT", None)
    if not isinstance(inp, dict):
        violations.append(Violation(ERROR, target, "missing INPUT object"))
    else:
        # An empty INPUT is valid for constant/source nodes (e.g. nsNull).
        violations.extend(_check_input_entries(target, inp))

    out = getattr(cls, "OUTPUT", None)
    if not isinstance(out, dict):
        violations.append(Violation(ERROR, target, "missing OUTPUT object"))
    else:
        if "kind" not in out:
            violations.append(Violation(ERROR, target, "OUTPUT is missing 'kind'"))
        elif out["kind"] not in KNOWN_KINDS:
            violations.append(Violation(WARNING, target, f"OUTPUT unknown kind '{out['kind']}'"))
        if "name" not in out:
            violations.append(Violation(WARNING, target, "OUTPUT is missing 'name'"))

    if not callable(getattr(cls, "evaluate", None)):
        violations.append(Violation(ERROR, target, "missing callable evaluate()"))

    return violations


def lint_rule(rule_name: str, cls: Any) -> List[Violation]:
    """Lint a single rule ``python_class`` against the contract."""
    target = f"rule:{rule_name}"
    violations: List[Violation] = []

    for attr in ("CATEGORY", "SUBCATEGORY", "DESCRIPTION"):
        value = getattr(cls, attr, None)
        if not isinstance(value, str) or not value:
            violations.append(Violation(ERROR, target, f"missing non-empty {attr}"))

    params = getattr(cls, "PARAMETERS", None)
    if not isinstance(params, dict):
        violations.append(Violation(ERROR, target, "missing PARAMETERS object"))

    if not callable(getattr(cls, "evaluate", None)):
        violations.append(Violation(ERROR, target, "missing callable evaluate()"))

    return violations


def _extract_class(registration: Any) -> Any:
    if isinstance(registration, dict):
        return registration.get("python_class")
    return registration


def lint_registry(
    nodes: Mapping[str, Any],
    rules: Mapping[str, Any] | None = None,
) -> List[Violation]:
    """Lint every registered node and rule. Returns all violations."""
    violations: List[Violation] = []
    for type_name, registration in (nodes or {}).items():
        cls = _extract_class(registration)
        if cls is None:
            violations.append(Violation(ERROR, f"node:{type_name}", "no python_class"))
            continue
        violations.extend(lint_node(type_name, cls))
    for rule_name, registration in (rules or {}).items():
        cls = _extract_class(registration)
        if cls is None:
            violations.append(Violation(ERROR, f"rule:{rule_name}", "no python_class"))
            continue
        violations.extend(lint_rule(rule_name, cls))
    return violations


def has_errors(violations: List[Violation]) -> bool:
    return any(v.level == ERROR for v in violations)


def _load_registry():
    """Load all extensions via the real Server loader (used by the CLI)."""
    import asyncio
    from argparse import Namespace

    from server.infrastructure.servers.server import Server

    args = Namespace(
        enable_cors_header="*",
        enable_smart_cache=False,
        inspection_delay=0,
        enable_parallel_execution=False,
        max_parallel_nodes=8,
        max_upload_size=100,
    )
    loop = asyncio.new_event_loop()
    try:
        server = Server(loop=loop, args=args)
        server.load_extensions()
        return dict(server.nodes), dict(server.rules)
    finally:
        loop.close()


def main(argv=None) -> int:
    nodes, rules = _load_registry()
    violations = lint_registry(nodes, rules)
    errors = [v for v in violations if v.level == ERROR]
    warnings = [v for v in violations if v.level == WARNING]

    for violation in violations:
        print(violation)

    print(
        f"\nharness lint: {len(nodes)} nodes, {len(rules)} rules checked; "
        f"{len(errors)} error(s), {len(warnings)} warning(s)."
    )
    return 1 if errors else 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
