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
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

from . import observability
from .agent_events import AGENT_EVENTS


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
class Iteration:
    index: int
    thoughts: str
    plan: List[str]
    node_count: int
    execution_ok: bool
    node_errors: List[Dict[str, Any]]
    feedback: str = ""


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
        }


# propose(request, workflow, feedback) -> ProposeResult
ProposeFn = Callable[[str, Dict[str, Any], Optional[str]], ProposeResult]
# execute(prompt_graph) -> ExecResult
ExecuteFn = Callable[[Dict[str, Any]], ExecResult]


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

    def __init__(self, propose: ProposeFn, execute: ExecuteFn, *, max_iterations: int = 3):
        self.propose = propose
        self.execute = execute
        self.max_iterations = max(1, max_iterations)

    def run(self, request: str, *, workflow: Optional[Dict[str, Any]] = None) -> HarnessRun:
        current: Dict[str, Any] = dict(workflow or {})
        feedback: Optional[str] = None
        iterations: List[Iteration] = []
        passed = False
        final_outputs: Dict[str, Any] = {}

        span = AGENT_EVENTS.start("harness", request[:80], detail={"request": request})

        def stream(msg: str) -> None:
            AGENT_EVENTS.stream(span, msg, name="harness")

        stream(f"[harness] request: {request}\n")
        for index in range(1, self.max_iterations + 1):
            stream(f"[harness] iteration {index}: proposing a workflow...\n")
            proposal = self.propose(request, current, feedback)
            if proposal.prompt:
                current = proposal.prompt
            if proposal.thoughts:
                stream(f"[harness] plan: {proposal.thoughts}\n")
            stream(f"[harness] iteration {index}: executing {len(current)} node(s)...\n")
            ex = self.execute(current)
            fb = "" if ex.ok else execution_feedback(ex)
            iterations.append(
                Iteration(
                    index=index,
                    thoughts=proposal.thoughts,
                    plan=proposal.plan,
                    node_count=len(current),
                    execution_ok=ex.ok,
                    node_errors=ex.node_errors,
                    feedback=fb,
                )
            )
            if ex.ok:
                stream(f"[harness] iteration {index}: execution OK\n")
                passed = True
                final_outputs = ex.outputs
                break
            feedback = fb
            stream(f"[harness] iteration {index}: {fb}\n")

        AGENT_EVENTS.finish(
            span,
            status="succeeded" if passed else "failed",
            detail={"iterations": len(iterations), "passed": passed},
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

        reply = iterations[-1].thoughts if iterations else ""
        return HarnessRun(
            request=request,
            passed=passed,
            iterations_used=len(iterations),
            max_iterations=self.max_iterations,
            final_prompt=current,
            final_outputs=final_outputs,
            iterations=iterations,
            reply=reply,
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
