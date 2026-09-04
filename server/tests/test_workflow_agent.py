"""Offline tests for the execution-in-the-loop workflow harness."""

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET
from server.harness.workflow_agent import (
    CodeSuggestion,
    ProposeResult,
    VerifyResult,
    WorkflowHarness,
    diff_graphs,
    get_node_source,
    make_graph_executor,
    make_graph_proposer,
    run_prompt_graph,
    summarize_diff,
)

KNOWN = {**CORE["nodes"], **NET["nodes"]}


# --- control loop with injected stubs (deterministic) ---
def _proposer(good_when_feedback=True):
    seen = {"feedbacks": []}

    def propose(request, workflow, feedback):
        seen["feedbacks"].append(feedback)
        node_type = "GOOD" if (feedback and good_when_feedback) else "BAD"
        return ProposeResult(
            prompt={"1": {"type": node_type, "name": "n", "inputs": {}}},
            thoughts="fixing" if feedback else "first try",
        )

    return propose, seen


def _executor():
    def execute(prompt):
        from server.harness.workflow_agent import ExecResult

        ok = any(n.get("type") == "GOOD" for n in prompt.values())
        errors = [] if ok else [{"node_id": "1", "message": "BAD node cannot run"}]
        return ExecResult(ok=ok, node_errors=errors, outputs={"1": "out"} if ok else {})

    return execute


def test_harness_recovers_after_execution_feedback():
    propose, seen = _proposer()
    harness = WorkflowHarness(propose, _executor(), max_iterations=4)
    run = harness.run("do a thing")
    assert run.passed is True
    assert run.iterations_used == 2
    # first proposal had no feedback; second got execution feedback
    assert seen["feedbacks"][0] is None
    assert seen["feedbacks"][1] and "BAD node" in seen["feedbacks"][1]
    assert run.iterations[0].execution_ok is False
    assert run.iterations[1].execution_ok is True


def test_harness_stops_early_on_success():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}})

    harness = WorkflowHarness(propose, _executor(), max_iterations=4)
    run = harness.run("x")
    assert run.passed is True
    assert run.iterations_used == 1


def test_harness_gives_up_after_max_iterations():
    propose, _ = _proposer(good_when_feedback=False)
    harness = WorkflowHarness(propose, _executor(), max_iterations=3)
    run = harness.run("x")
    assert run.passed is False
    assert run.iterations_used == 3
    assert run.final_outputs == {}


# --- graph change communication (diff) ---
def test_diff_graphs_reports_all_change_kinds():
    before = {
        "1": {"type": "nsString", "name": "s", "inputs": {"text": "hi"}},
        "2": {"type": "ConsoleLog", "name": "log", "inputs": {"any": {"originId": "1"}}},
    }
    after = {
        "1": {"type": "nsString", "name": "s", "inputs": {"text": "bye"}},  # widget change
        "3": {"type": "StringToUpper", "name": "up", "inputs": {"text": {"originId": "1"}}},  # added + edge
    }
    diff = diff_graphs(before, after)
    assert [n["id"] for n in diff.added_nodes] == ["3"]
    assert [n["id"] for n in diff.removed_nodes] == ["2"]
    assert any(w["id"] == "1" and w["to"] == "bye" for w in diff.widget_changes)
    assert {"target": "3", "input": "text", "originId": "1"} in diff.added_edges
    assert {"target": "2", "input": "any", "originId": "1"} in diff.removed_edges

    summary = summarize_diff(diff)
    joined = " | ".join(summary)
    assert "Added StringToUpper (node 3)" in summary
    assert "Removed ConsoleLog (node 2)" in summary
    assert "Wired node 3.text ← node 1" in joined
    assert any("bye" in line for line in summary)


def test_diff_graphs_reports_retype():
    diff = diff_graphs(
        {"1": {"type": "nsString", "inputs": {}}}, {"1": {"type": "nsInteger", "inputs": {}}}
    )
    assert diff.retyped_nodes == [{"id": "1", "from": "nsString", "to": "nsInteger"}]
    assert "Changed node 1 type: nsString → nsInteger" in summarize_diff(diff)


def test_harness_communicates_graph_changes_per_iteration():
    graphs = [
        {"1": {"type": "BAD", "name": "n", "inputs": {}}},
        {"2": {"type": "GOOD", "name": "n", "inputs": {}}},
    ]
    seq = iter(graphs)

    def propose(request, workflow, feedback):
        return ProposeResult(prompt=next(seq))

    run = WorkflowHarness(propose, _executor(), max_iterations=2).run("x")
    # iter 1 added node 1; iter 2 added node 2 and removed node 1
    assert "Added BAD (node 1)" in run.iterations[0].change_summary
    assert "Added GOOD (node 2)" in run.iterations[1].change_summary
    assert "Removed BAD (node 1)" in run.iterations[1].change_summary
    assert run.change_summary == run.iterations[-1].change_summary


# --- suggested code updates to node implementations ---
def test_get_node_source_returns_class_source():
    src = get_node_source(KNOWN, "nsString")
    assert src and "class nsString" in src and "def evaluate" in src


def test_harness_suggests_code_on_failure():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "BAD", "name": "n", "inputs": {}}})

    def always_fail(prompt):
        from server.harness.workflow_agent import ExecResult

        return ExecResult(ok=False, error="BAD.evaluate raised ValueError")

    calls = {"n": 0}

    def suggest(request, prompt, error):
        calls["n"] += 1
        return CodeSuggestion(
            node_type="BAD",
            rationale="guard the None case in evaluate",
            current_code="class BAD: ...",
            suggested_code="class BAD:\n    def evaluate(self, i): return ''",
        )

    run = WorkflowHarness(propose, always_fail, suggest_code=suggest, max_iterations=2).run("x")
    assert run.passed is False
    # code suggestion produced once, after the loop
    assert calls["n"] == 1
    assert run.code_suggestions and run.code_suggestions[0]["node_type"] == "BAD"
    assert "guard the None case" in run.code_suggestions[0]["rationale"]
    assert run.iterations[-1].code_suggestions == run.code_suggestions


def test_harness_no_code_suggestion_on_success():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}})

    def suggest(request, prompt, error):
        raise AssertionError("should not be called on success")

    run = WorkflowHarness(propose, _executor(), suggest_code=suggest, max_iterations=2).run("x")
    assert run.passed is True
    assert run.code_suggestions == []


# --- intent verification ---
def _always_good_proposer():
    seen = {"feedbacks": []}

    def propose(request, workflow, feedback):
        seen["feedbacks"].append(feedback)
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}}, thoughts="t")

    return propose, seen


def test_harness_iterates_until_intent_met():
    propose, seen = _always_good_proposer()
    verdicts = iter(
        [VerifyResult(met=False, reason="output is wrong"), VerifyResult(met=True, reason="correct")]
    )

    def verify(request, prompt, outputs):
        return next(verdicts)

    run = WorkflowHarness(propose, _executor(), verify=verify, max_iterations=4).run("x")
    assert run.passed is True
    assert run.iterations_used == 2
    assert run.intent_met is True
    # execution succeeded both times, but intent gated the first
    assert run.iterations[0].execution_ok is True
    assert run.iterations[0].intent_met is False
    assert run.iterations[1].intent_met is True
    # the intent failure was fed back to the second proposal
    assert seen["feedbacks"][1] and "did NOT meet" in seen["feedbacks"][1]


def test_harness_without_verifier_passes_on_execution():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}})

    run = WorkflowHarness(propose, _executor(), verify=None, max_iterations=3).run("x")
    assert run.passed is True
    assert run.iterations_used == 1
    assert run.intent_met is True


def test_harness_gives_up_when_intent_never_met():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}})

    def verify(request, prompt, outputs):
        return VerifyResult(met=False, reason="never right")

    run = WorkflowHarness(propose, _executor(), verify=verify, max_iterations=3).run("x")
    assert run.passed is False
    assert run.iterations_used == 3
    assert run.intent_met is False
    assert run.final_outputs == {}


def test_verifier_exception_does_not_crash_run():
    def propose(request, workflow, feedback):
        return ProposeResult(prompt={"1": {"type": "GOOD", "name": "n", "inputs": {}}})

    def verify(request, prompt, outputs):
        raise RuntimeError("judge down")

    run = WorkflowHarness(propose, _executor(), verify=verify, max_iterations=2).run("x")
    assert run.passed is True  # accepts on verifier error
    assert run.iterations_used == 1


# --- real executor bridge ---
def test_run_prompt_graph_executes_valid_graph():
    prompt = {
        "1": {"type": "nsString", "name": "s", "inputs": {"text": "hi"}},
        "2": {"type": "ConsoleLog", "name": "log", "inputs": {"any": {"originId": "1"}}},
    }
    result = run_prompt_graph(prompt, KNOWN)
    assert result.ok is True
    assert "hi" in [str(v) for v in result.outputs.values()]


def test_run_prompt_graph_reports_failure_on_broken_graph():
    prompt = {"1": {"type": "ConsoleLog", "name": "log", "inputs": {"any": {"originId": "99"}}}}
    result = run_prompt_graph(prompt, KNOWN)
    assert result.ok is False


def test_run_prompt_graph_empty():
    assert run_prompt_graph({}, KNOWN).ok is False


# --- end-to-end offline (real proposer + real executor, no network) ---
def test_harness_offline_builds_and_executes():
    harness = WorkflowHarness(
        make_graph_proposer(KNOWN, planner=None),  # offline deterministic builder
        make_graph_executor(KNOWN),
        max_iterations=3,
    )
    run = harness.run('log "harness works"')
    assert run.passed is True
    assert run.iterations_used == 1
    assert any("harness works" == str(v) for v in run.final_outputs.values())
