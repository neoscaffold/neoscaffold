"""Execution-in-the-loop workflow harness.

The conversational workspace harness: given a user's request, propose a workflow
(graph), **execute** it, and if the run fails, feed the failure back and refine —
iterating on both the workflow and its executions until it runs (or the attempt
budget is exhausted).

The loop is dependency-injected (``propose`` + ``execute``) so it is
unit-testable offline; the live wiring composes the graph builder/planner
(``make_graph_proposer``) with the real graph executor (``run_prompt_graph``).
Per-iteration progress is streamed to the Agent Activity UI via ``AGENT_EVENTS``.
"""

from __future__ import annotations

import asyncio
import inspect
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

from . import observability
from .agent_events import AGENT_EVENTS


# --- graph change communication -------------------------------------------
def _edges(node_id: str, node: Dict[str, Any]):
    inputs = (node or {}).get("inputs") or {}
    for name, value in inputs.items():
        if isinstance(value, dict) and "originId" in value:
            yield (str(node_id), str(name), str(value["originId"]))


def _literals(node: Dict[str, Any]) -> Dict[str, Any]:
    inputs = (node or {}).get("inputs") or {}
    return {
        name: value
        for name, value in inputs.items()
        if not (isinstance(value, dict) and "originId" in value)
    }


@dataclass
class GraphDiff:
    added_nodes: List[Dict[str, Any]] = field(default_factory=list)
    removed_nodes: List[Dict[str, Any]] = field(default_factory=list)
    retyped_nodes: List[Dict[str, Any]] = field(default_factory=list)
    widget_changes: List[Dict[str, Any]] = field(default_factory=list)
    added_edges: List[Dict[str, Any]] = field(default_factory=list)
    removed_edges: List[Dict[str, Any]] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not (
            self.added_nodes
            or self.removed_nodes
            or self.retyped_nodes
            or self.widget_changes
            or self.added_edges
            or self.removed_edges
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def diff_graphs(before: Optional[Dict[str, Any]], after: Optional[Dict[str, Any]]) -> GraphDiff:
    """Compute a structured diff between two prompt-graphs (nodes/edges/widgets).

    Only dict-valued entries are treated as nodes, so a raw LiteGraph workflow
    (with list/metadata values) or any non-prompt-graph input is tolerated.
    """
    before = {
        k: v for k, v in (before or {}).items() if isinstance(v, dict) and v.get("type")
    }
    after = {
        k: v for k, v in (after or {}).items() if isinstance(v, dict) and v.get("type")
    }
    before_ids, after_ids = set(before), set(after)

    added_nodes = sorted(
        (
            {"id": i, "type": after[i].get("type"), "name": after[i].get("name")}
            for i in after_ids - before_ids
        ),
        key=lambda n: str(n["id"]),
    )
    removed_nodes = sorted(
        (
            {"id": i, "type": before[i].get("type"), "name": before[i].get("name")}
            for i in before_ids - after_ids
        ),
        key=lambda n: str(n["id"]),
    )

    before_edges, after_edges = set(), set()
    for i, n in before.items():
        before_edges.update(_edges(i, n))
    for i, n in after.items():
        after_edges.update(_edges(i, n))

    def _edge_dicts(edges):
        return sorted(
            ({"target": t, "input": inp, "originId": o} for (t, inp, o) in edges),
            key=lambda e: (e["target"], e["input"], e["originId"]),
        )

    added_edges = _edge_dicts(after_edges - before_edges)
    removed_edges = _edge_dicts(before_edges - after_edges)

    retyped_nodes = []
    widget_changes = []
    for i in sorted(before_ids & after_ids, key=str):
        if before[i].get("type") != after[i].get("type"):
            retyped_nodes.append(
                {"id": i, "from": before[i].get("type"), "to": after[i].get("type")}
            )
        b_lit, a_lit = _literals(before[i]), _literals(after[i])
        for name in sorted(set(b_lit) | set(a_lit)):
            b_val, a_val = b_lit.get(name), a_lit.get(name)
            if b_val != a_val:
                widget_changes.append(
                    {"id": i, "type": after[i].get("type"), "input": name, "from": b_val, "to": a_val}
                )

    return GraphDiff(
        added_nodes, removed_nodes, retyped_nodes, widget_changes, added_edges, removed_edges
    )


def summarize_diff(diff: GraphDiff) -> List[str]:
    """Human-readable, one-line-per-change summary of a graph diff."""
    lines: List[str] = []
    for node in diff.added_nodes:
        lines.append(f"Added {node['type']} (node {node['id']})")
    for node in diff.removed_nodes:
        lines.append(f"Removed {node['type']} (node {node['id']})")
    for node in diff.retyped_nodes:
        lines.append(f"Changed node {node['id']} type: {node['from']} → {node['to']}")
    for edge in diff.added_edges:
        lines.append(f"Wired node {edge['target']}.{edge['input']} ← node {edge['originId']}")
    for edge in diff.removed_edges:
        lines.append(
            f"Unwired node {edge['target']}.{edge['input']} (was ← node {edge['originId']})"
        )
    for change in diff.widget_changes:
        if change["from"] is None:
            lines.append(f"Set node {change['id']}.{change['input']} = {change['to']!r}")
        elif change["to"] is None:
            lines.append(f"Cleared node {change['id']}.{change['input']}")
        else:
            lines.append(
                f"Changed node {change['id']}.{change['input']}: "
                f"{change['from']!r} → {change['to']!r}"
            )
    return lines


# --- node code-update suggestions ------------------------------------------
@dataclass
class CodeSuggestion:
    node_type: str
    rationale: str
    current_code: str = ""
    suggested_code: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def get_node_source(known_nodes: Mapping[str, Any], node_type: str) -> Optional[str]:
    """Return the Python source of a node's implementation class, if available."""
    registration = known_nodes.get(node_type)
    cls = registration.get("python_class") if isinstance(registration, dict) else registration
    if cls is None:
        return None
    try:
        return inspect.getsource(cls)
    except Exception:
        return None


@dataclass
class ProposeResult:
    prompt: Dict[str, Any]
    thoughts: str = ""
    plan: List[str] = field(default_factory=list)
    source: str = ""


@dataclass
class ExecResult:
    ok: bool
    node_errors: List[Dict[str, Any]] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: str = ""


@dataclass
class VerifyResult:
    met: bool
    reason: str = ""


@dataclass
class Iteration:
    index: int
    thoughts: str
    plan: List[str]
    node_count: int
    execution_ok: bool
    node_errors: List[Dict[str, Any]]
    feedback: str = ""
    intent_met: Optional[bool] = None
    verify_reason: str = ""
    changes: Dict[str, Any] = field(default_factory=dict)
    change_summary: List[str] = field(default_factory=list)
    code_suggestions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class HarnessRun:
    request: str
    passed: bool
    iterations_used: int
    max_iterations: int
    final_prompt: Dict[str, Any]
    final_outputs: Dict[str, Any]
    iterations: List[Iteration] = field(default_factory=list)
    reply: str = ""
    intent_met: Optional[bool] = None
    intent_reason: str = ""
    change_summary: List[str] = field(default_factory=list)
    code_suggestions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request,
            "passed": self.passed,
            "iterations_used": self.iterations_used,
            "max_iterations": self.max_iterations,
            "final_prompt": self.final_prompt,
            "final_outputs": self.final_outputs,
            "iterations": [asdict(it) for it in self.iterations],
            "reply": self.reply,
            "intent_met": self.intent_met,
            "intent_reason": self.intent_reason,
            "change_summary": self.change_summary,
            "code_suggestions": self.code_suggestions,
        }


# propose(request, workflow, feedback) -> ProposeResult
ProposeFn = Callable[[str, Dict[str, Any], Optional[str]], ProposeResult]
# execute(prompt_graph) -> ExecResult
ExecuteFn = Callable[[Dict[str, Any]], ExecResult]
# verify(request, prompt_graph, outputs) -> VerifyResult
VerifyFn = Callable[[str, Dict[str, Any], Dict[str, Any]], VerifyResult]
# suggest_code(request, prompt_graph, error) -> Optional[CodeSuggestion]
CodeSuggestFn = Callable[[str, Dict[str, Any], str], Optional[CodeSuggestion]]


def execution_feedback(ex: ExecResult) -> str:
    """Human/agent-readable feedback describing why a run was not successful."""
    if ex.node_errors:
        parts = []
        for err in ex.node_errors[:5]:
            node_id = err.get("node_id", "?")
            message = err.get("message") or err.get("error") or err
            parts.append(f"node {node_id}: {message}")
        return "Execution failed on -> " + "; ".join(str(p) for p in parts)
    if ex.error:
        return f"Execution raised: {ex.error}"
    if not ex.outputs:
        return "The workflow ran but produced no output; ensure it ends in a logged result."
    return ""


class WorkflowHarness:
    """Iterate on a workflow and its executions from a conversational request."""

    def __init__(
        self,
        propose: ProposeFn,
        execute: ExecuteFn,
        *,
        verify: Optional[VerifyFn] = None,
        suggest_code: Optional[CodeSuggestFn] = None,
        max_iterations: int = 3,
    ):
        self.propose = propose
        self.execute = execute
        self.verify = verify
        self.suggest_code = suggest_code
        self.max_iterations = max(1, max_iterations)

    def run(self, request: str, *, workflow: Optional[Dict[str, Any]] = None) -> HarnessRun:
        current: Dict[str, Any] = dict(workflow or {})
        feedback: Optional[str] = None
        iterations: List[Iteration] = []
        passed = False
        final_outputs: Dict[str, Any] = {}
        intent_met: Optional[bool] = None
        intent_reason = ""

        span = AGENT_EVENTS.start("harness", request[:80], detail={"request": request})

        def stream(msg: str) -> None:
            AGENT_EVENTS.stream(span, msg, name="harness")

        stream(f"[harness] request: {request}\n")
        last_failed_error = ""
        for index in range(1, self.max_iterations + 1):
            stream(f"[harness] iteration {index}: proposing a workflow...\n")
            prior = current
            proposal = self.propose(request, current, feedback)
            if proposal.prompt:
                current = proposal.prompt

            # Communicate exactly what the agent proposes to change on the graph.
            diff = diff_graphs(prior, current)
            change_summary = summarize_diff(diff)
            for line in change_summary:
                stream(f"[harness] change: {line}\n")

            if proposal.thoughts:
                stream(f"[harness] plan: {proposal.thoughts}\n")
            stream(f"[harness] iteration {index}: executing {len(current)} node(s)...\n")
            ex = self.execute(current)

            iteration = Iteration(
                index=index,
                thoughts=proposal.thoughts,
                plan=proposal.plan,
                node_count=len(current),
                execution_ok=ex.ok,
                node_errors=ex.node_errors,
                changes=diff.to_dict(),
                change_summary=change_summary,
            )
            iterations.append(iteration)

            if not ex.ok:
                fb = execution_feedback(ex)
                iteration.feedback = fb
                feedback = fb
                last_failed_error = ex.error or fb
                stream(f"[harness] iteration {index}: execution failed — {fb}\n")
                continue

            stream(f"[harness] iteration {index}: execution OK; verifying intent...\n")
            final_outputs = ex.outputs
            if self.verify is None:
                intent_met, intent_reason = True, "no verifier configured; execution succeeded"
            else:
                try:
                    verdict = self.verify(request, current, ex.outputs)
                except Exception as exc:  # never let the judge crash the run
                    verdict = VerifyResult(met=True, reason=f"verifier error, accepting: {exc}")
                intent_met, intent_reason = verdict.met, verdict.reason
            iteration.intent_met = intent_met
            iteration.verify_reason = intent_reason

            if intent_met:
                stream(f"[harness] iteration {index}: intent met — {intent_reason}\n")
                passed = True
                break

            fb = (
                f"The workflow executed but did NOT meet the request: {intent_reason}. "
                "Adjust the workflow so the final logged output satisfies the request."
            )
            iteration.feedback = fb
            feedback = fb
            stream(f"[harness] iteration {index}: intent NOT met — {intent_reason}\n")

        # When we couldn't satisfy the request by editing the graph, communicate
        # a suggested change to the code powering an implicated node (for review;
        # never auto-applied).
        code_suggestions: List[Dict[str, Any]] = []
        if not passed and self.suggest_code is not None and last_failed_error:
            try:
                suggestion = self.suggest_code(request, current, last_failed_error)
            except Exception:
                suggestion = None
            if suggestion is not None and suggestion.node_type:
                code_suggestions = [suggestion.to_dict()]
                if iterations:
                    iterations[-1].code_suggestions = code_suggestions
                stream(
                    f"[harness] suggested code update to {suggestion.node_type}: "
                    f"{suggestion.rationale}\n"
                )

        AGENT_EVENTS.finish(
            span,
            status="succeeded" if passed else "failed",
            detail={"iterations": len(iterations), "passed": passed, "intent_met": intent_met},
        )
        observability.inc(
            "neoscaffold_harness_runs_total",
            help="Workflow harness runs",
            passed=str(passed).lower(),
        )
        observability.observe(
            "neoscaffold_harness_iterations",
            float(len(iterations)),
            help="Iterations used by the workflow harness",
        )

        reply = intent_reason or (iterations[-1].thoughts if iterations else "")
        return HarnessRun(
            request=request,
            passed=passed,
            iterations_used=len(iterations),
            max_iterations=self.max_iterations,
            final_prompt=current,
            final_outputs=final_outputs if passed else {},
            iterations=iterations,
            reply=reply,
            intent_met=intent_met,
            intent_reason=intent_reason,
            change_summary=iterations[-1].change_summary if iterations else [],
            code_suggestions=code_suggestions,
        )


# --- live wiring -----------------------------------------------------------
def run_prompt_graph(
    prompt: Dict[str, Any],
    known_nodes: Mapping[str, Any],
    *,
    mode: str = "parallel",
) -> ExecResult:
    """Execute a prompt-graph via the real GraphExecutor and capture results."""
    from ..domain.services.graph_executor import GraphExecutor

    if not prompt:
        return ExecResult(ok=False, error="empty workflow")

    class _HarnessServer:
        ENABLE_SMART_CACHE = False
        INSPECTION_DELAY = 0
        MAX_PARALLEL_NODES = 8

        def __init__(self, nodes: Mapping[str, Any]):
            self.nodes = nodes
            self.rules = {}
            self.sessions = {}
            self.client_id = "harness"
            self.current_workflow_id = "harness-wf"
            self.sent_messages: List[Any] = []

        async def send_json(self, event, data, sid=None):
            self.sent_messages.append({"event": event, "data": data})

    server = _HarnessServer(known_nodes)
    executor = GraphExecutor(server)
    response = {
        "prompt_id": "harness",
        "number": 1,
        "client_id": "harness",
        "workflow_id": "harness-wf",
    }
    try:
        graph = executor.prompt_to_graph(prompt)
        runner = executor.run_parallel if mode == "parallel" else executor.run_sequential
        results = asyncio.run(runner(graph, response))
    except Exception as exc:  # invalid graph / node crash
        return ExecResult(ok=False, error=str(exc)[:400])

    node_errors: List[Dict[str, Any]] = []
    for message in server.sent_messages:
        data = message.get("data") if isinstance(message, dict) else None
        errs = data.get("node_errors") if isinstance(data, dict) else None
        if errs:
            for err in errs:
                node_errors.append(err if isinstance(err, dict) else {"message": str(err)})

    outputs = {nid: getattr(value, "values", None) for nid, value in (results or {}).items()}
    ok = bool(results) and not node_errors
    return ExecResult(ok=ok, node_errors=node_errors, outputs=outputs)


def make_graph_executor(known_nodes: Mapping[str, Any]) -> ExecuteFn:
    def execute(prompt: Dict[str, Any]) -> ExecResult:
        return run_prompt_graph(prompt, known_nodes)

    return execute


def make_llm_verifier(model: Optional[str] = None) -> Optional[VerifyFn]:
    """LLM-as-judge intent verifier (or ``None`` when no key is configured).

    Given the request and the workflow's execution outputs, decide whether the
    result satisfies the user's intent. Returns ``VerifyResult(met, reason)``.
    """
    import json
    import os

    if os.environ.get("NEOSCAFFOLD_GRAPH_OFFLINE", "").lower() in ("1", "true", "yes"):
        return None
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    chosen_model = model or os.environ.get("NEOSCAFFOLD_GRAPH_MODEL", "gpt-5.6-terra")

    def verify(request: str, prompt: Dict[str, Any], outputs: Dict[str, Any]) -> VerifyResult:
        from openai import OpenAI

        client = OpenAI()
        # Prefer the terminal (sink) node outputs; include all, truncated.
        rendered = {str(k): str(v)[:400] for k, v in (outputs or {}).items()}
        system = (
            "You verify whether a built workflow satisfied a user's request. "
            "You are given the request and the workflow's node outputs "
            "(node_id -> produced value). Judge whether the FINAL/most relevant "
            "output satisfies the request. Be strict about the actual value, not "
            "just that something ran. Respond ONLY with JSON: "
            '{"met": true|false, "reason": "one concise sentence"}.'
        )
        user = (
            f"Request:\n{request}\n\nWorkflow node outputs:\n{json.dumps(rendered)}\n"
        )
        try:
            response = client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=200,
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return VerifyResult(met=bool(data.get("met")), reason=str(data.get("reason", "")))
        except Exception as exc:
            # If the judge fails, accept (don't block a runnable workflow).
            return VerifyResult(met=True, reason=f"verifier unavailable, accepting: {exc}")

    return verify


def make_code_suggester(
    known_nodes: Mapping[str, Any], model: Optional[str] = None
) -> Optional[CodeSuggestFn]:
    """LLM-backed suggester of code changes to a node's implementation.

    When a workflow can't be made to run by editing the graph, this proposes a
    minimal revision to the Python code of the most-implicated node (identified
    by the model from the graph's node types + the runtime error) plus a
    rationale. Returns ``None`` when it's not a code issue or no key is set.
    Suggestions are communicated for human review and never auto-applied.
    """
    import json
    import os

    if os.environ.get("NEOSCAFFOLD_GRAPH_OFFLINE", "").lower() in ("1", "true", "yes"):
        return None
    if not os.environ.get("OPENAI_API_KEY"):
        return None

    chosen_model = model or os.environ.get("NEOSCAFFOLD_GRAPH_MODEL", "gpt-5.6-terra")

    def suggest(request: str, prompt: Dict[str, Any], error: str) -> Optional[CodeSuggestion]:
        from openai import OpenAI

        # Candidate node types actually used in the failing workflow, with source.
        candidates: Dict[str, str] = {}
        for node in (prompt or {}).values():
            node_type = (node or {}).get("type")
            if node_type and node_type not in candidates:
                source = get_node_source(known_nodes, node_type)
                if source:
                    candidates[node_type] = source[:2000]
        if not candidates:
            return None

        catalog = "\n\n".join(
            f"### {name}\n```python\n{src}\n```" for name, src in candidates.items()
        )
        system = (
            "A visual-programming workflow failed at runtime. Its nodes are powered "
            "by Python classes. Decide whether one node's CODE should change to fix "
            "the failure (as opposed to just rewiring). If so, return the node type, "
            "a one-sentence rationale, and a minimal corrected version of that node's "
            "Python class. If it's not a code problem, return node_type null. "
            'Respond ONLY as JSON: {"node_type": string|null, "rationale": string, '
            '"suggested_code": string}.'
        )
        user = (
            f"User request:\n{request}\n\nRuntime error:\n{error}\n\n"
            f"Node implementations used in the workflow:\n{catalog}\n"
        )
        client = OpenAI()
        try:
            response = client.chat.completions.create(
                model=chosen_model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=900,
            )
            data = json.loads(response.choices[0].message.content or "{}")
        except Exception:
            return None
        node_type = data.get("node_type")
        if not node_type or node_type not in candidates:
            return None
        return CodeSuggestion(
            node_type=node_type,
            rationale=str(data.get("rationale", "")),
            current_code=candidates[node_type],
            suggested_code=str(data.get("suggested_code", "")),
        )

    return suggest


def make_graph_proposer(
    known_nodes: Mapping[str, Any],
    planner: Optional[Callable[[str], Any]],
) -> ProposeFn:
    """Build a proposer that uses the graph builder/planner to author workflows."""
    from ..domain.services.graph_builder import GraphBuilder

    def propose(request: str, workflow: Dict[str, Any], feedback: Optional[str]) -> ProposeResult:
        builder = GraphBuilder(known_nodes=known_nodes, llm=planner)
        text = request
        if feedback:
            text = (
                f"{request}\n\nThe previous workflow FAILED when executed:\n{feedback}\n"
                "Return a corrected workflow that runs successfully end to end."
            )
        result = builder.build(text, workflow=workflow or None)
        return ProposeResult(
            prompt=result.prompt,
            thoughts=result.thoughts or "",
            plan=result.plan or [],
            source=result.source,
        )

    return propose
