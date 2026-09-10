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
import os
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
    complete_control_flow,
    contracts_from_nodes,
    edge_count,
    fill_unwired_if_literals,
    insert_value_path_adapters,
    lint_graph,
    lint_needs_refine,
    parse_graph,
    repair_connectivity,
    rewrite_misused_combiners,
)
from ...harness.workflows import (
    canvas_to_prompt,
    export_workflow,
    import_workflow,
    is_prompt_graph,
)

DEFAULT_GRAPH_MODEL = os.environ.get("NEOSCAFFOLD_GRAPH_MODEL", "gpt-4o-mini")

# Node types the offline planner composes from. All are provided by the core /
# network_requests extensions that ship with NeoScaffold.
STRING_NODE = "nsString"
JOIN_NODE = "StringJoin"
LOG_NODE = "ConsoleLog"
PROMPT_NODE = "PromptNode"
ARRAY_NODE = "nsArray"
ARRAY_APPEND_NODE = "nsArrayAppend"
PASS_NODE = "PassThrough"
SWARM_SOLVER_NODE = "SwarmSolverNode"
SWARM_JOIN_NODE = "SwarmJoinNode"
IF_EQUAL_NODE = "IfEqual"
IF_TRUE_NODE = "IfEqualTrue"
IF_FALSE_NODE = "IfEqualFalse"
IF_END_NODE = "EndIfEqual"
FOR_LOOP_NODE = "ForLoop"
FOR_END_NODE = "EndForLoop"
WHILE_LOOP_NODE = "WhileLoop"
WHILE_END_NODE = "EndWhileLoop"
FOREACH_LOOP_NODE = "ForEachLoop"
FOREACH_END_NODE = "EndForEachLoop"
BOOL_NODE = "nsBoolean"
INT_NODE = "nsInteger"
MEMORY_READ_NODE = "MemoryRead"

_QUOTED = re.compile(r"[\"'“”‘’]([^\"'“”‘’]+)[\"'“”‘’]")
_JOIN_WORDS = ("concat", "join", "combine", "append", "merge")
_LOG_WORDS = ("log", "print", "console", "output", "display", "show")
_STRING_WORDS = ("string", "text", "message", "say", "word")
_PIPE_WORDS = ("pipe", "pipeline", "passthrough", "pass through", "chain", "forward", "through")
_SWARM_WORDS = ("swarm", "codeforces", "agents")
_IF_WORDS = ("if ", "if equal", "equals", "otherwise", " else ")
_LOOP_WORDS = ("loop", "repeat", "iterate", "for each", "while ")
_IMPORT_WORDS = ("import workflow", "import this workflow", "load workflow")
_EXPORT_WORDS = ("export workflow", "export this workflow", "save workflow")
_CF_ID_RE = re.compile(r"\b(?:codeforces/)?\d+/[A-Za-z0-9]+\b")
_IF_RE = re.compile(
    r"if\s+[\"']([^\"']+)[\"']\s+equals?\s+[\"']([^\"']+)[\"']"
    r"(?:\s+then\s+[\"']([^\"']+)[\"'])?"
    r"(?:\s+else\s+[\"']([^\"']+)[\"'])?",
    re.I,
)
_LOOP_COUNT_RE = re.compile(
    r"(?:loop|repeat|iterate)\s+(?:for\s+)?(\d+)\s*(?:times?)?",
    re.I,
)
_FOR_RANGE_RE = re.compile(
    r"for\s+(?:from\s+)?(-?\d+)\s+(?:to|through|until)\s+(-?\d+)",
    re.I,
)

# Default swarm workload (must stay in sync with agent_swarm/problems.py).
DEFAULT_CODEFORCES_IDS = [
    "codeforces/409/F",
    "codeforces/784/A",
    "codeforces/952/A",
    "codeforces/656/A",
    "codeforces/1145/B",
    "codeforces/656/D",
    "codeforces/290/B",
    "codeforces/784/D",
    "codeforces/290/A",
    "codeforces/171/B",
]


def _normalize_cf_id(raw: str) -> str:
    return raw if raw.startswith("codeforces/") else f"codeforces/{raw}"


@dataclass
class BuildResult:
    """A built graph plus the evidence needed to review it."""

    spec: GraphSpec
    prompt: Dict[str, Any]
    plan: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    repairs: List[str] = field(default_factory=list)
    source: str = "offline"
    thoughts: str = ""
    widget_edits: List[Dict[str, Any]] = field(default_factory=list)
    exported_workflow: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "prompt": self.prompt,
            "plan": self.plan,
            "warnings": self.warnings,
            "repairs": self.repairs,
            "source": self.source,
            "thoughts": self.thoughts,
            "widget_edits": self.widget_edits,
        }
        if self.exported_workflow is not None:
            payload["exported_workflow"] = self.exported_workflow
        return payload


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
        self._canvas: Optional[Dict[str, Any]] = None
        self._history: Optional[List[Any]] = None
        self._workflow: Optional[Dict[str, Any]] = None

    # --- availability helper -------------------------------------------------
    def _has(self, node_type: str) -> bool:
        # With no contracts we cannot verify availability, so assume present.
        return self.contracts is None or node_type in self.contracts

    # --- public API ----------------------------------------------------------
    def build(
        self,
        prompt: str,
        *,
        canvas: Optional[Mapping[str, Any]] = None,
        history: Optional[List[Any]] = None,
        workflow: Optional[Mapping[str, Any]] = None,
    ) -> BuildResult:
        start = time.perf_counter()
        text = (prompt or "").strip()
        if not text:
            raise ParseError("prompt", "prompt must be a non-empty string")
        self._canvas = dict(canvas) if isinstance(canvas, Mapping) else None
        self._history = list(history) if isinstance(history, list) else None
        self._workflow = dict(workflow) if isinstance(workflow, Mapping) else None

        # Open a subagent span so users can watch the build happen.
        event_id = AGENT_EVENTS.start(
            "graph_build", text[:80], detail={"prompt": text, "planner": "llm" if self.llm else "offline"}
        )
        try:
            portable = self._import_or_export(text)
            if portable is not None:
                result = portable
            elif self.llm is not None:
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
                "edges": edge_count(result.spec),
                "types": [node.type for node in result.spec.nodes.values()],
                "plan": result.plan,
                "warnings": result.warnings,
                "repairs": result.repairs,
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
            edges=edge_count(result.spec),
            types=[node.type for node in result.spec.nodes.values()],
            warnings=result.warnings,
            repairs=result.repairs,
        )
        return result

    # --- offline deterministic planner --------------------------------------
    def _empty_spec(self) -> GraphSpec:
        return parse_graph({}, contracts=self.contracts)

    def _import_or_export(self, text: str) -> Optional[BuildResult]:
        imported = import_workflow(text)
        if imported is None and self._workflow and any(
            word in text.lower() for word in _IMPORT_WORDS
        ):
            imported = import_workflow(self._workflow)
        if imported:
            spec = parse_graph(imported, contracts=self.contracts)
            return BuildResult(
                spec=spec,
                prompt=spec.to_prompt(),
                plan=["Imported the workflow JSON into a prompt-graph."],
                thoughts="Loading the provided workflow.",
                warnings=lint_graph(spec, self.contracts) if self.contracts else [],
                source="offline",
            )

        if any(word in text.lower() for word in _EXPORT_WORDS):
            current = None
            if self._workflow:
                current = import_workflow(self._workflow)
            if current is None and self._canvas:
                current = canvas_to_prompt(self._canvas)
            if current:
                spec = parse_graph(current, contracts=self.contracts)
                return BuildResult(
                    spec=self._empty_spec(),
                    prompt={},
                    plan=["Exported the current workflow as JSON."],
                    thoughts="Use the downloaded JSON or Menu → Import to reload it.",
                    source="offline",
                    exported_workflow=export_workflow(
                        spec.to_prompt(),
                        litegraph=self._workflow if self._workflow else None,
                    ),
                )
        return None

    def _widget_edit_result(
        self,
        edits: List[Dict[str, Any]],
        *,
        thoughts: str = "",
        plan: Optional[List[str]] = None,
        source: str = "offline",
        repairs: Optional[List[str]] = None,
    ) -> BuildResult:
        return BuildResult(
            spec=self._empty_spec(),
            prompt={},
            plan=plan
            or [f"Set {edit.get('widget')} on node {edit.get('node_id')}." for edit in edits],
            thoughts=thoughts or "Updating existing widgets on the canvas.",
            widget_edits=edits,
            source=source,
            repairs=list(repairs or []),
        )

    def _build_offline(self, text: str) -> BuildResult:
        imported = import_workflow(text)
        if imported is None and self._workflow and any(
            word in text.lower() for word in _IMPORT_WORDS
        ):
            imported = import_workflow(self._workflow)
        if imported:
            spec = parse_graph(imported, contracts=self.contracts)
            return BuildResult(
                spec=spec,
                prompt=spec.to_prompt(),
                plan=["Imported the workflow JSON into a prompt-graph."],
                thoughts="Loading the provided workflow.",
                warnings=lint_graph(spec, self.contracts) if self.contracts else [],
                source="offline",
            )

        if any(word in text.lower() for word in _EXPORT_WORDS):
            current = None
            if self._workflow:
                current = import_workflow(self._workflow)
            if current is None and self._canvas:
                current = canvas_to_prompt(self._canvas)
            if current:
                spec = parse_graph(current, contracts=self.contracts)
                exported = export_workflow(
                    spec.to_prompt(),
                    litegraph=self._workflow if self._workflow else None,
                )
                return BuildResult(
                    spec=self._empty_spec(),
                    prompt={},
                    plan=["Exported the current workflow as JSON."],
                    thoughts="Use the downloaded JSON or Menu → Import to reload it.",
                    source="offline",
                    exported_workflow=exported,
                )

        if self._canvas:
            edits = offline_widget_edits(text, self._canvas)
            if edits:
                return self._widget_edit_result(edits)
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

        wants_swarm = any(word in lowered for word in _SWARM_WORDS)
        can_swarm = all(
            self._has(node_type)
            for node_type in (SWARM_SOLVER_NODE, SWARM_JOIN_NODE, ARRAY_NODE, ARRAY_APPEND_NODE)
        )

        def wire_swarm(problem_ids: List[str]) -> str:
            # Fan out: one SwarmSolverNode (independent agent) per problem.
            solver_ids = []
            for problem_id in problem_ids:
                solver_ids.append(
                    add(SWARM_SOLVER_NODE, f"solve {problem_id}", {"problem_id": problem_id})
                )
            plan.append(f"Spawn {len(solver_ids)} agents (SwarmSolverNode), one per problem.")
            # Collect their outputs into an array via a wired append chain.
            array_id = add(ARRAY_NODE, "results", {})
            current = array_id
            for solver_id in solver_ids:
                current = add(
                    ARRAY_APPEND_NODE,
                    "collect",
                    {"array": edge(current), "element": edge(solver_id)},
                )
            plan.append("Collect each agent's result into an array (wired).")
            # Fork-join into a single report.
            join_id = add(SWARM_JOIN_NODE, "fork-join", {"results": edge(current)})
            plan.append("Fork-join the agents' solutions into a report (SwarmJoinNode).")
            return join_id

        source_id: Optional[str] = None

        def wire_if_equal(left: str, right: str, then_text: str, else_text: str) -> Optional[str]:
            needed = (
                STRING_NODE,
                IF_EQUAL_NODE,
                IF_TRUE_NODE,
                IF_FALSE_NODE,
                IF_END_NODE,
                PASS_NODE,
                LOG_NODE,
            )
            if not all(self._has(node_type) for node_type in needed):
                return None
            left_id = add(STRING_NODE, "if left", {"text": left})
            right_id = add(STRING_NODE, "if right", {"text": right})
            if_id = add(IF_EQUAL_NODE, "if", {"a": edge(left_id), "b": edge(right_id)})
            then_id = add(STRING_NODE, "then", {"text": then_text})
            else_id = add(STRING_NODE, "else", {"text": else_text})
            true_id = add(IF_TRUE_NODE, "if true", {"IfEqual": edge(if_id)})
            false_id = add(IF_FALSE_NODE, "if false", {"IfEqual": edge(if_id)})
            then_pass = add(
                PASS_NODE, "then branch", {"value": edge(then_id), "ignored_input": edge(true_id)}
            )
            else_pass = add(
                PASS_NODE, "else branch", {"value": edge(else_id), "ignored_input": edge(false_id)}
            )
            then_log = add(LOG_NODE, "log then", {"any": edge(then_pass)})
            add(LOG_NODE, "log else", {"any": edge(else_pass)})
            add(
                IF_END_NODE,
                "end if",
                {"IfEqual": edge(if_id), "node_inputs": edge(then_log)},
            )
            plan.append(f"Compare {left!r} and {right!r} (IfEqual) with then/else branches.")
            return then_log

        def wire_for_loop(start: int, stop: int) -> Optional[str]:
            needed = (STRING_NODE, FOR_LOOP_NODE, FOR_END_NODE, PASS_NODE, MEMORY_READ_NODE, LOG_NODE)
            if not all(self._has(node_type) for node_type in needed):
                return None
            key_id = add(STRING_NODE, "index key", {"text": "index"})
            loop_id = add(
                FOR_LOOP_NODE,
                "for",
                {
                    "start": start,
                    "stop": stop,
                    "step": 1,
                    "index_key": edge(key_id),
                    "node_inputs": "",
                },
            )
            gate_id = add(
                PASS_NODE,
                "loop body",
                {"value": edge(key_id), "ignored_input": edge(loop_id)},
            )
            read_id = add(MEMORY_READ_NODE, "read index", {"key": edge(gate_id)})
            log_id = add(LOG_NODE, "log index", {"any": edge(read_id)})
            add(
                FOR_END_NODE,
                "end for",
                {"ForLoop": edge(loop_id), "node_inputs": edge(log_id)},
            )
            plan.append(f"Repeat from {start} to {stop} (ForLoop) and log the index.")
            return log_id

        if_match = _IF_RE.search(text)
        loop_count = _LOOP_COUNT_RE.search(text)
        for_range = _FOR_RANGE_RE.search(text)
        wants_if = if_match is not None or any(word in lowered for word in _IF_WORDS)
        wants_loop = any(word in lowered for word in _LOOP_WORDS)

        if if_match:
            source_id = wire_if_equal(
                if_match.group(1),
                if_match.group(2),
                if_match.group(3) or "true",
                if_match.group(4) or "false",
            )
        elif wants_loop and (loop_count or for_range):
            if for_range:
                start, stop = int(for_range.group(1)), int(for_range.group(2))
            else:
                start, stop = 0, int(loop_count.group(1))
            source_id = wire_for_loop(start, stop)

        if source_id is not None:
            pass
        elif wants_swarm and can_swarm:
            found = [_normalize_cf_id(m) for m in _CF_ID_RE.findall(text)]
            problem_ids = found or list(DEFAULT_CODEFORCES_IDS)
            source_id = wire_swarm(problem_ids)
        elif literals and can_wire_join and (wants_join or len(literals) > 1):
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
    def _compose_llm_message(self, text: str) -> str:
        parts = [text]
        if self._history:
            parts.append(
                "\nConversation so far:\n"
                + json.dumps(self._history[-12:], ensure_ascii=False)[:4000]
            )
        if self._canvas:
            parts.append(
                "\nCurrent canvas widgets (node_id -> type/name/widgets). "
                "To change an existing widget, emit widget_edits using these node_ids; "
                "do not rebuild the graph unless the user asked for new nodes.\n"
                + json.dumps(self._canvas, ensure_ascii=False)[:8000]
            )
        return "\n".join(parts)

    def _repair_llm_graph(self, graph_raw: Any, text: str) -> tuple:
        repairs: List[str] = []
        kinds = {"combiner": 0, "control": 0, "connectivity": 0, "value_path": 0}
        first_error: Optional[ParseError] = None
        try:
            parse_graph(graph_raw, contracts=self.contracts)
        except ParseError as exc:
            first_error = exc
            observability.inc(
                "neoscaffold_graph_build_rejected_total", reason="llm_parse"
            )

        candidate, drop_repairs = repair_graph(graph_raw, contracts=self.contracts)
        repairs.extend(drop_repairs)
        candidate, combiner_repairs = rewrite_misused_combiners(
            candidate, contracts=self.contracts
        )
        repairs.extend(combiner_repairs)
        kinds["combiner"] = len(combiner_repairs)
        candidate, control_repairs = complete_control_flow(
            candidate, contracts=self.contracts
        )
        repairs.extend(control_repairs)
        kinds["control"] = len(control_repairs)
        candidate, conn_repairs = repair_connectivity(
            candidate, contracts=self.contracts, user_prompt=text
        )
        repairs.extend(conn_repairs)
        kinds["connectivity"] = len(conn_repairs)
        candidate, path_repairs = insert_value_path_adapters(
            candidate, contracts=self.contracts
        )
        repairs.extend(path_repairs)
        kinds["value_path"] = len(path_repairs)
        if first_error is not None and drop_repairs:
            repairs.append(f"repaired after: {first_error}")
        return candidate, repairs, first_error, kinds

    def _refine_graph_from_feedback(
        self, text: str, current: Dict[str, Any], warnings: List[str]
    ) -> Optional[Dict[str, Any]]:
        if self.llm is None:
            return None
        payload = {
            "task": (
                "The graph below is missing wires. Return ONLY a JSON envelope "
                "with a complete 'prompt' graph that fixes every problem. "
                "Keep existing nodes when possible. Wire every required "
                "dataflow and control input (IfEqual.a/b, EndIfEqual.IfEqual, "
                "EndForLoop.ForLoop, IfEqualTrue/False.IfEqual, loop body "
                "via PassThrough.ignored_input). Do not invent api_key values."
            ),
            "user_request": text,
            "problems": warnings,
            "current_graph": current,
        }
        raw = self.llm(json.dumps(payload, ensure_ascii=False))
        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except json.JSONDecodeError:
                return None
        _thoughts, _edits, _plan, graph_raw = extract_llm_payload(raw)
        if graph_raw is None and isinstance(raw, dict) and is_prompt_graph(raw):
            graph_raw = raw
        return graph_raw if isinstance(graph_raw, dict) else None

    def _build_with_llm(self, text: str) -> BuildResult:
        raw = self.llm(self._compose_llm_message(text))  # type: ignore[misc]
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

        thoughts, edits, extra_plan, graph_raw = extract_llm_payload(raw)
        if graph_raw is None and edits:
            return self._widget_edit_result(
                edits,
                thoughts=thoughts,
                plan=extra_plan,
                source="llm",
            )

        if graph_raw is None:
            fallback = self._build_offline(text)
            if thoughts and not fallback.thoughts:
                fallback.thoughts = thoughts
            fallback.repairs.append("LLM returned no graph; used offline planner")
            fallback.source = "offline_fallback"
            return fallback

        candidate, repairs, first_error, repair_kinds = self._repair_llm_graph(
            graph_raw, text
        )

        try:
            spec = parse_graph(candidate, contracts=self.contracts)
        except ParseError as exc:
            if edits:
                return self._widget_edit_result(
                    edits,
                    thoughts=thoughts,
                    plan=extra_plan,
                    source="llm",
                    repairs=repairs + [f"graph dropped ({first_error or exc})"],
                )
            observability.inc(
                "neoscaffold_graph_build_rejected_total", reason="llm_invalid"
            )
            fallback = self._build_offline(text)
            fallback.repairs.append(
                f"LLM graph invalid ({first_error or exc}); used offline planner"
            )
            fallback.source = "offline_fallback"
            return fallback

        if not spec.nodes:
            if edits:
                return self._widget_edit_result(
                    edits, thoughts=thoughts, plan=extra_plan, source="llm", repairs=repairs
                )
            observability.inc("neoscaffold_graph_build_rejected_total", reason="llm_empty")
            fallback = self._build_offline(text)
            fallback.repairs = repairs + ["LLM graph was empty after repair; used offline planner"]
            fallback.source = "offline_fallback"
            return fallback

        warnings = lint_graph(spec, self.contracts) if self.contracts else []
        refine_rounds = 0
        while lint_needs_refine(warnings) and refine_rounds < 2:
            refine_rounds += 1
            refined = self._refine_graph_from_feedback(
                text, spec.to_prompt(), warnings
            )
            if refined is None:
                break
            candidate, more_repairs, _, more_kinds = self._repair_llm_graph(
                refined, text
            )
            repairs.extend(more_repairs)
            for key, count in more_kinds.items():
                repair_kinds[key] = repair_kinds.get(key, 0) + count
            try:
                spec = parse_graph(candidate, contracts=self.contracts)
            except ParseError:
                break
            if not spec.nodes:
                break
            warnings = lint_graph(spec, self.contracts) if self.contracts else []
            repairs.append(f"refined graph from lint feedback (round {refine_rounds})")

        if lint_needs_refine(warnings):
            candidate, literal_repairs = fill_unwired_if_literals(candidate)
            if literal_repairs:
                repairs.extend(literal_repairs)
                try:
                    spec = parse_graph(candidate, contracts=self.contracts)
                    warnings = lint_graph(spec, self.contracts) if self.contracts else []
                except ParseError:
                    pass

        plan = extra_plan or ["Graph proposed by LLM, parsed and accepted."]
        if repair_kinds.get("combiner"):
            plan.append(
                "Harness replaced SwarmJoinNode with ConcatString (not a swarm)."
            )
        if repair_kinds.get("control"):
            plan.append("Harness completed if/loop control-flow nodes.")
        if repair_kinds.get("connectivity"):
            plan.append("Harness wired disconnected nodes and filled empty prompts.")
        if repair_kinds.get("value_path"):
            plan.append("Harness inserted ValuePath nodes to deconstruct dict outputs.")
        if refine_rounds:
            plan.append(
                f"Harness refined the graph from missing-wire feedback ({refine_rounds} round(s))."
            )
        return BuildResult(
            spec=spec,
            prompt=spec.to_prompt(),
            plan=plan,
            warnings=warnings,
            repairs=repairs,
            source="llm",
            thoughts=thoughts,
            widget_edits=edits,
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


_ENVELOPE_KEYS = {
    "thoughts",
    "thought",
    "widget_edits",
    "edits",
    "plan",
    "warnings",
    "repairs",
    "source",
    "layout",
    "canvas",
    "history",
}
_EDIT_WORDS = ("set", "change", "update", "edit", "fill", "replace")
_CREDENTIAL_WIDGETS = frozenset({"api_key", "key", "token", "password", "secret"})


def _looks_like_node(value: Any) -> bool:
    return isinstance(value, dict) and isinstance(value.get("type"), str) and bool(value.get("type"))


def extract_llm_payload(raw: Any) -> tuple:
    """Split an LLM payload into thoughts, widget edits, plan, and a graph dict."""
    thoughts = ""
    edits: List[Dict[str, Any]] = []
    plan: List[str] = []
    graph: Optional[Dict[str, Any]] = None
    if not isinstance(raw, dict):
        return thoughts, edits, plan, None

    thoughts = raw.get("thoughts") or raw.get("thought") or ""
    if not isinstance(thoughts, str):
        thoughts = str(thoughts)
    raw_edits = raw.get("widget_edits") if raw.get("widget_edits") is not None else raw.get("edits")
    if isinstance(raw_edits, list):
        for item in raw_edits:
            if not isinstance(item, dict):
                continue
            widget = item.get("widget") or item.get("name")
            if not widget:
                continue
            edits.append(
                {
                    "node_id": str(item.get("node_id") or item.get("id") or ""),
                    "widget": str(widget),
                    "value": item.get("value"),
                    "type": item.get("type"),
                    "name": item.get("name"),
                    "index": item.get("index"),
                }
            )
    raw_plan = raw.get("plan")
    if isinstance(raw_plan, list):
        plan = [str(step) for step in raw_plan]
    elif isinstance(raw_plan, str) and raw_plan.strip():
        plan = [raw_plan.strip()]

    if isinstance(raw.get("prompt"), dict) and any(_looks_like_node(v) for v in raw["prompt"].values()):
        graph = raw["prompt"]
    else:
        nodes = {
            str(key): value
            for key, value in raw.items()
            if key not in _ENVELOPE_KEYS and _looks_like_node(value)
        }
        graph = nodes or None
    return thoughts, edits, plan, graph


def offline_widget_edits(text: str, canvas: Mapping[str, Any]) -> List[Dict[str, Any]]:
    """Deterministic widget edits from a 'set/change X on Type to Y' request."""
    if not canvas or not any(word in text.lower() for word in _EDIT_WORDS):
        return []

    quoted = [match.strip() for match in _QUOTED.findall(text) if match.strip()]
    value: Any = quoted[-1] if quoted else None
    if value is None:
        trailing = re.search(r"\bto\s+([A-Za-z0-9_.-]+)\s*$", text.strip(), re.I)
        if trailing:
            value = trailing.group(1)
    if value is None:
        return []

    widget_names = set()
    for node in canvas.values():
        if isinstance(node, dict):
            widget_names.update((node.get("widgets") or {}).keys())

    mentioned = [
        name for name in widget_names if re.search(rf"\b{re.escape(name)}\b", text, re.I)
    ]
    node_id_match = re.search(r"\bnode\s+(\d+)\b", text, re.I)
    targets: List[str] = []
    if node_id_match and node_id_match.group(1) in canvas:
        targets = [node_id_match.group(1)]
    else:
        lowered = text.lower()
        for node_id, node in canvas.items():
            if not isinstance(node, dict):
                continue
            node_type = str(node.get("type") or "").lower()
            node_name = str(node.get("name") or "").lower()
            if node_type and node_type in lowered:
                targets.append(str(node_id))
            elif node_name and node_name in lowered:
                targets.append(str(node_id))

    if not targets:
        return []
    if not mentioned:
        if re.search(r"\bprompt\b", text, re.I):
            mentioned = ["prompt"]
        elif re.search(r"\btext\b", text, re.I):
            mentioned = ["text"]
        else:
            return []

    edits: List[Dict[str, Any]] = []
    for node_id in targets:
        node = canvas.get(node_id) or {}
        widgets = node.get("widgets") or {}
        for widget_name in mentioned:
            if widget_name not in widgets:
                continue
            if widget_name in _CREDENTIAL_WIDGETS and widget_name not in text.lower():
                continue
            edits.append(
                {
                    "node_id": str(node_id),
                    "widget": widget_name,
                    "value": value,
                    "type": node.get("type"),
                    "name": node.get("name"),
                }
            )
    return edits


def build_graph(
    prompt: str,
    *,
    known_nodes: Optional[Mapping[str, Any]] = None,
    llm: Optional[Callable[[str], Any]] = None,
    canvas: Optional[Mapping[str, Any]] = None,
    history: Optional[List[Any]] = None,
    workflow: Optional[Mapping[str, Any]] = None,
) -> BuildResult:
    """Convenience wrapper around :class:`GraphBuilder`."""
    return GraphBuilder(known_nodes=known_nodes, llm=llm).build(
        prompt, canvas=canvas, history=history, workflow=workflow
    )


_PREFERRED_PLANNER_TYPES = (
    "PromptNode",
    "BuildGraphNode",
    "CerebrasAgent",
    "CerebrasAgentAsync",
    "SwarmSolverNode",
    "SwarmJoinNode",
    "ValuePath",
    "nsString",
    "nsInteger",
    "nsBoolean",
    "ConcatString",
    "StringJoin",
    "ConsoleLog",
    "PassThrough",
    "nsArray",
    "nsArrayAppend",
    "MemoryRead",
    "MemoryWrite",
    "IfEqual",
    "IfEqualTrue",
    "IfEqualFalse",
    "EndIfEqual",
    "WhileLoop",
    "EndWhileLoop",
    "ForLoop",
    "EndForLoop",
    "ForEachLoop",
    "EndForEachLoop",
)


def _registration_class(registration: Any) -> Any:
    if isinstance(registration, dict):
        return registration.get("python_class")
    return registration


def _contract_line(name: str, cls: Any) -> str:
    inputs = getattr(cls, "INPUT", {}) or {}
    required = list((inputs.get("required_inputs") or {}).keys())
    optional = list((inputs.get("optional_inputs") or {}).keys())
    description = (getattr(cls, "DESCRIPTION", "") or "").strip()
    parts = []
    if required:
        parts.append("in " + ", ".join(required))
    if optional:
        parts.append("opt " + ", ".join(optional))
    signature = "; ".join(parts)
    desc = f" — {description}" if description else ""
    if signature:
        return f"- {name}: {signature}{desc}"
    return f"- {name}{desc}"


def _planner_prompt(known_nodes: Optional[Mapping[str, Any]]) -> str:
    """System prompt listing node types the model may emit."""
    registry = known_nodes or {}
    detailed: List[str] = []
    seen = set()
    for name in _PREFERRED_PLANNER_TYPES:
        cls = _registration_class(registry.get(name))
        if cls is None:
            continue
        detailed.append(_contract_line(name, cls))
        seen.add(name)
    other_names = sorted(n for n in registry if n not in seen)
    others = ", ".join(other_names) if other_names else "(none)"
    palette = "\n".join(detailed) if detailed else "- nsString: in text\n- ConsoleLog: in any"

    return (
        "You are NeoScaffold's graph planner and widget editor.\n\n"
        "Return ONLY valid JSON (no markdown fences) using this envelope:\n"
        "{\n"
        '  "thoughts": "short reasoning the user can read",\n'
        '  "plan": ["step", "..."],\n'
        '  "widget_edits": [{"node_id": "15", "widget": "prompt", "value": "..."}],\n'
        '  "prompt": {"<id>": {"type": "<NodeType>", "name": "...", "inputs": {...}}}\n'
        "}\n"
        "Use widget_edits to change existing canvas widgets (any widget on any node). "
        "Use prompt only when the user wants new nodes. You may return both.\n\n"
        "Rules:\n"
        "- Node ids are unique string keys (\"1\", \"2\", ...).\n"
        "- EVERY dataflow input MUST be wired with "
        '{"originId": "<source_node_id>"}. Never leave combiners or logs unwired.\n'
        "- Fill agent/node `prompt` (and `text`) with a concrete string derived "
        "from the user's request. Distinct agents get distinct prompts.\n"
        "- Do not invent api_key values; omit them or leave them empty.\n"
        "- Prefer a small DAG that ends in ConsoleLog.\n"
        "- Dict outputs MUST be deconstructed with ValuePath before concat/log:\n"
        "  CerebrasAgent/CerebrasAgentAsync returns "
        "{chat_id, chat_history, summary, cost, human_input}.\n"
        "  SwarmSolverNode returns {problem_id, title, code, verified, ...}.\n"
        "  ValuePath.object is an originId; value_path is a literal field name "
        "(default 'summary' for agents, 'code' for swarm solvers).\n"
        "- Two agents whose results are combined MUST look like this pattern:\n"
        "  CerebrasAgent -> ValuePath(summary) -> ConcatString.a / .b -> ConsoleLog.any\n"
        "- SwarmJoinNode is ONLY for SwarmSolverNode results collected in an "
        "nsArray. Never use it to combine CerebrasAgent / text outputs.\n"
        "- Never wire an agent dict straight into ConcatString or ConsoleLog.\n"
        "- If / else MUST use IfEqual + IfEqualTrue + IfEqualFalse + EndIfEqual:\n"
        "  IfEqual.a / .b are originIds; each branch and EndIfEqual.IfEqual "
        "wire back to the IfEqual. Put branch work after IfEqualTrue/False "
        "(PassThrough.ignored_input <- branch) and EndIfEqual.node_inputs "
        "from a branch result.\n"
        "- Loops MUST pair start and end nodes:\n"
        "  ForLoop (start/stop/step literals, optional index_key) + body + "
        "EndForLoop.ForLoop originId and .node_inputs from the body.\n"
        "  WhileLoop.condition_key is a memory key; EndWhileLoop.WhileLoop "
        "is an originId. ForEachLoop.collection is an originId to an array.\n"
        "  The first body node must be a successor of the loop "
        "(wire ignored_input from the loop).\n"
        "- Import: if the user pastes a workflow JSON (prompt-graph or "
        "LiteGraph {nodes, links}), return that graph in prompt.\n"
        "- Export: if the user asks to export/save the workflow, return "
        "widget_edits=[] and prompt={} and put the current graph in "
        "thoughts as confirmation; the server attaches exported_workflow.\n"
        "- Only use node types from this palette (preferred, with contracts):\n"
        f"{palette}\n"
        f"Other allowed types (name only): {others}\n"
    )


def make_openai_planner(
    known_nodes: Optional[Mapping[str, Any]] = None,
    *,
    model: Optional[str] = None,
) -> Optional[Callable[[str], Any]]:
    """Return an OpenAI-backed planner when a key is configured, else ``None``.

    Controlled by env:
    - ``OPENAI_API_KEY`` — enables the live planner
    - ``NEOSCAFFOLD_GRAPH_MODEL`` — model id (default ``gpt-4o-mini``)
    - ``NEOSCAFFOLD_GRAPH_OFFLINE=1`` — force the offline planner even if a key is set
    """
    offline_forced = os.environ.get("NEOSCAFFOLD_GRAPH_OFFLINE", "").lower() in (
        "1",
        "true",
        "yes",
    )
    if offline_forced or not os.environ.get("OPENAI_API_KEY"):
        return None

    chosen_model = model or DEFAULT_GRAPH_MODEL
    system = _planner_prompt(known_nodes)

    def planner(user_prompt: str) -> Any:
        from openai import OpenAI

        client = OpenAI()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ]
        kwargs: Dict[str, Any] = {
            "model": chosen_model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }
        try:
            response = client.chat.completions.create(**kwargs)
        except Exception as exc:
            # Some models (e.g. gpt-5.6-*) only allow the default temperature.
            if "temperature" in str(exc):
                kwargs.pop("temperature", None)
                response = client.chat.completions.create(**kwargs)
            else:
                raise
        content = response.choices[0].message.content or "{}"
        return content

    return planner
