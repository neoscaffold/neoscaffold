"""Agent-generated graph topology: natural language -> valid prompt-graph.

``build_graph`` turns a plain-language intent into an executable NeoScaffold
prompt-graph. The default planner is **offline and deterministic** (no API key
required), so the natural-language entry point is unit-testable. An optional
LLM planner may be injected; its output is always run through the parse boundary
(``harness.parsing``) and repaired or rejected — never executed unparsed
(harness.md §4, §6).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

from ...harness import observability
from ...harness.agent_events import AGENT_EVENTS
from ...harness.parsing import (
    GraphSpec,
    NodeContract,
    ParseError,
    contracts_from_nodes,
    lint_graph,
    parse_graph,
)

# Node types the offline planner composes from. All are provided by the core /
# network_requests extensions that ship with NeoScaffold.
STRING_NODE = "nsString"
JOIN_NODE = "StringJoin"
LOG_NODE = "ConsoleLog"
PROMPT_NODE = "PromptNode"
ARRAY_NODE = "nsArray"
ARRAY_APPEND_NODE = "nsArrayAppend"
PASS_NODE = "PassThrough"

_QUOTED = re.compile(r"[\"'“”‘’]([^\"'“”‘’]+)[\"'“”‘’]")
_JOIN_WORDS = ("concat", "join", "combine", "append", "merge")
_LOG_WORDS = ("log", "print", "console", "output", "display", "show")
_STRING_WORDS = ("string", "text", "message", "say", "word")
_PIPE_WORDS = ("pipe", "pipeline", "passthrough", "pass through", "chain", "forward", "through")


@dataclass
class BuildResult:
    """A built graph plus the evidence needed to review it."""

    spec: GraphSpec
    prompt: Dict[str, Any]
    plan: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    repairs: List[str] = field(default_factory=list)
    source: str = "offline"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "plan": self.plan,
            "warnings": self.warnings,
            "repairs": self.repairs,
            "source": self.source,
        }


class GraphBuilder:
    """Builds prompt-graphs from natural language.

    ``known_nodes`` is a ``server.nodes``-style mapping; when provided, the
    builder only composes types that are registered and parses the result
    against their contracts. ``llm`` is an optional callable
    ``(prompt: str) -> dict | str`` returning a proposed graph.
    """

    def __init__(
        self,
        known_nodes: Optional[Mapping[str, Any]] = None,
        llm: Optional[Callable[[str], Any]] = None,
    ) -> None:
        self.known_nodes = dict(known_nodes or {})
        self.contracts: Optional[Dict[str, NodeContract]] = (
            contracts_from_nodes(self.known_nodes) if known_nodes else None
        )
        self.llm = llm

    # --- availability helper -------------------------------------------------
    def _has(self, node_type: str) -> bool:
        # With no contracts we cannot verify availability, so assume present.
        return self.contracts is None or node_type in self.contracts

    # --- public API ----------------------------------------------------------
    def build(self, prompt: str) -> BuildResult:
        start = time.perf_counter()
        text = (prompt or "").strip()
        if not text:
            raise ParseError("prompt", "prompt must be a non-empty string")

        # Open a subagent span so users can watch the build happen.
        event_id = AGENT_EVENTS.start(
            "graph_build", text[:80], detail={"prompt": text, "planner": "llm" if self.llm else "offline"}
        )
        try:
            if self.llm is not None:
                result = self._build_with_llm(text)
            else:
                result = self._build_offline(text)
        except Exception as exc:
            AGENT_EVENTS.finish(event_id, status="failed", detail={"error": str(exc)})
            raise

        # Child spans: each generated node is a scoped unit of work.
        for node_id, node_spec in result.spec.nodes.items():
            AGENT_EVENTS.record(
                "node",
                node_spec.type,
                parent_id=event_id,
                detail={"node_id": node_id, "name": node_spec.name},
            )

        AGENT_EVENTS.finish(
            event_id,
            status="succeeded",
            detail={
                "source": result.source,
                "nodes": len(result.spec.nodes),
                "plan": result.plan,
                "warnings": result.warnings,
            },
        )

        observability.inc(
            "neoscaffold_graph_build_total",
            help="Graphs built from natural language",
            source=result.source,
        )
        observability.observe(
            "neoscaffold_graph_build_seconds",
            time.perf_counter() - start,
            help="Time to build a graph from natural language",
            source=result.source,
        )
        observability.log_event(
            "graph_build",
            source=result.source,
            nodes=len(result.spec.nodes),
            warnings=len(result.warnings),
            repairs=len(result.repairs),
        )
        return result

    # --- offline deterministic planner --------------------------------------
    def _build_offline(self, text: str) -> BuildResult:
        lowered = text.lower()
        literals = [m.strip() for m in _QUOTED.findall(text) if m.strip()]
        wants_join = any(word in lowered for word in _JOIN_WORDS)
        wants_log = any(word in lowered for word in _LOG_WORDS)
        wants_pipe = any(word in lowered for word in _PIPE_WORDS)
        mentions_string = any(word in lowered for word in _STRING_WORDS)

        plan: List[str] = []
        payload: Dict[str, Any] = {}
        counter = [0]

        def add(node_type: str, name: str, inputs: Dict[str, Any]) -> str:
            counter[0] += 1
            node_id = str(counter[0])
            payload[node_id] = {"type": node_type, "name": name, "inputs": inputs}
            return node_id

        def edge(node_id: str) -> Dict[str, str]:
            return {"originId": node_id}

        # Whether we can build a fully-wired concatenation (string nodes -> array
        # append chain -> join) instead of a single literal-fed node.
        can_wire_join = all(
            self._has(node_type)
            for node_type in (STRING_NODE, ARRAY_NODE, ARRAY_APPEND_NODE, JOIN_NODE)
        )

        def wire_join(items: List[str]) -> str:
            # Collect one nsString per literal into an array via a wired
            # nsArrayAppend chain, then StringJoin the array. Real node-to-node
            # edges throughout (this is the "understands wiring" path).
            array_id = add(ARRAY_NODE, "array", {})
            plan.append("Create an empty array (nsArray) as the collector.")
            current = array_id
            for index, literal in enumerate(items):
                string_id = add(STRING_NODE, f"string {index + 1}", {"text": literal})
                current = add(
                    ARRAY_APPEND_NODE,
                    f"append {index + 1}",
                    {"array": edge(current), "element": edge(string_id)},
                )
                plan.append(f"Create string {literal!r} and wire it into the array.")
            join_id = add(JOIN_NODE, "join", {"array": edge(current), "delimiter": " "})
            plan.append("Join the collected strings into one (StringJoin), wired from the array.")
            return join_id

        source_id: Optional[str] = None

        if literals and can_wire_join and (wants_join or len(literals) > 1):
            source_id = wire_join(literals)
        elif literals and self._has(STRING_NODE):
            source_id = add(STRING_NODE, "string", {"text": literals[0]})
            plan.append(f"Create a string = {literals[0]!r}.")
        elif (mentions_string or wants_log) and self._has(STRING_NODE):
            source_id = add(STRING_NODE, "string", {"text": text})
            plan.append("Create a string from the prompt text.")

        # Fallback: a prompt-driven node if available, else echo the prompt.
        if source_id is None:
            if self._has(PROMPT_NODE):
                source_id = add(PROMPT_NODE, "prompt", {"prompt": text})
                plan.append(f"Create a {PROMPT_NODE} carrying the prompt.")
            elif self._has(STRING_NODE):
                source_id = add(STRING_NODE, "string", {"text": text})
                plan.append("Create a string from the prompt text (fallback).")

        # Optional PassThrough link when the user asks to pipe/chain/pass through.
        if source_id is not None and wants_pipe and self._has(PASS_NODE):
            source_id = add(PASS_NODE, "passthrough", {"value": edge(source_id)})
            plan.append("Route the value through a PassThrough link.")

        # Always wire the result into a logger so the graph has an output sink.
        if source_id is not None and self._has(LOG_NODE):
            add(LOG_NODE, "log", {"any": edge(source_id)})
            plan.append(f"Wire the result into {LOG_NODE}.")

        spec = parse_graph(payload, contracts=self.contracts)
        warnings = lint_graph(spec, self.contracts) if self.contracts else []
        return BuildResult(
            spec=spec, prompt=spec.to_prompt(), plan=plan, warnings=warnings, source="offline"
        )

    # --- optional LLM planner ------------------------------------------------
    def _build_with_llm(self, text: str) -> BuildResult:
        raw = self.llm(text)  # type: ignore[misc]
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError as exc:
                observability.inc(
                    "neoscaffold_graph_build_rejected_total", reason="llm_json"
                )
                # Model produced non-JSON; fall back to the deterministic planner.
                fallback = self._build_offline(text)
                fallback.repairs.append(f"LLM output was not JSON ({exc}); used offline planner")
                fallback.source = "offline_fallback"
                return fallback

        # A model may wrap the graph under a "prompt" key; accept either shape.
        if isinstance(raw, dict) and "prompt" in raw and isinstance(raw["prompt"], dict):
            raw = raw["prompt"]

        repairs: List[str] = []
        try:
            spec = parse_graph(raw, contracts=self.contracts)
        except ParseError as first_error:
            repaired, repairs = repair_graph(raw, contracts=self.contracts)
            try:
                spec = parse_graph(repaired, contracts=self.contracts)
                repairs.append(f"repaired after: {first_error}")
            except ParseError:
                observability.inc(
                    "neoscaffold_graph_build_rejected_total", reason="llm_invalid"
                )
                fallback = self._build_offline(text)
                fallback.repairs.append(f"LLM graph invalid ({first_error}); used offline planner")
                fallback.source = "offline_fallback"
                return fallback

        if not spec.nodes:
            observability.inc("neoscaffold_graph_build_rejected_total", reason="llm_empty")
            fallback = self._build_offline(text)
            fallback.repairs = repairs + ["LLM graph was empty after repair; used offline planner"]
            fallback.source = "offline_fallback"
            return fallback

        warnings = lint_graph(spec, self.contracts) if self.contracts else []
        return BuildResult(
            spec=spec,
            prompt=spec.to_prompt(),
            plan=["Graph proposed by LLM, parsed and accepted."],
            warnings=warnings,
            repairs=repairs,
            source="llm",
        )


def repair_graph(
    payload: Any,
    *,
    contracts: Optional[Mapping[str, NodeContract]] = None,
) -> tuple:
    """Deterministically repair a graph payload (harness.md §6).

    Bounded repairs only: drop nodes of unknown type (when contracts are known)
    and drop edges whose ``originId`` is missing or self-referential. Never
    invents nodes. Returns ``(repaired_payload, repairs)``.
    """
    repairs: List[str] = []
    if not isinstance(payload, dict):
        return {}, ["payload was not an object; replaced with empty graph"]

    kept: Dict[str, Any] = {}
    for node_id, node in payload.items():
        if not isinstance(node, dict) or not node.get("type"):
            repairs.append(f"dropped malformed node '{node_id}'")
            continue
        if contracts is not None and node["type"] not in contracts:
            repairs.append(f"dropped node '{node_id}' of unknown type '{node['type']}'")
            continue
        kept[node_id] = node

    for node_id, node in kept.items():
        inputs = node.get("inputs") or {}
        if not isinstance(inputs, dict):
            node["inputs"] = {}
            repairs.append(f"reset non-object inputs on node '{node_id}'")
            continue
        cleaned: Dict[str, Any] = {}
        for name, value in inputs.items():
            if isinstance(value, dict) and "originId" in value:
                origin = value.get("originId")
                if origin == node_id or origin not in kept:
                    repairs.append(f"dropped dangling edge '{node_id}.{name}' -> '{origin}'")
                    continue
            cleaned[name] = value
        node["inputs"] = cleaned

    return kept, repairs


def build_graph(
    prompt: str,
    *,
    known_nodes: Optional[Mapping[str, Any]] = None,
    llm: Optional[Callable[[str], Any]] = None,
) -> BuildResult:
    """Convenience wrapper around :class:`GraphBuilder`."""
    return GraphBuilder(known_nodes=known_nodes, llm=llm).build(prompt)
