"""Offline tests for the agent-control loop and the task set (no network)."""

from agent_control import sandbox
from agent_control.controller import (
    control_agent,
    extract_code,
    run_tests,
)
from agent_control.tasks import TASKS, get_task


# --- task set integrity: every reference solution passes its hidden tests ---
def test_reference_solutions_pass_all_hidden_tests():
    for task in TASKS:
        outcomes = run_tests(task["reference_solution"], task["hidden_tests"], timeout=8)
        failed = [o for o in outcomes if not o.passed]
        assert not failed, (task["id"], [(o.input, o.expected, o.actual, o.error) for o in failed])


# --- extract_code ---
def test_extract_code_from_fence():
    assert extract_code("```python\nprint(1)\n```") == "print(1)"


def test_extract_code_raw():
    assert extract_code("print(1)") == "print(1)"


# --- sandbox ---
def test_sandbox_runs_stdin():
    result = sandbox.run_python_code("print(input())", stdin="hi\n")
    assert result.ok and result.stdout.strip() == "hi"


# --- control loop: stubbed models make it deterministic ---
WRONG = "print('WRONG')\n"


def _correct(task):
    return task["reference_solution"]


def test_one_shot_fails_with_wrong_solution():
    task = get_task("balanced_brackets")
    result = control_agent(task, lambda messages, i: WRONG, mode="one_shot", model_name="stub")
    assert result.passed is False
    assert result.attempts_used == 1
    assert len(result.attempts) == 1


def test_one_shot_passes_with_correct_solution():
    task = get_task("rle_encode")
    result = control_agent(task, lambda messages, i: _correct(task), mode="one_shot")
    assert result.passed is True
    assert result.attempts_used == 1


def test_controlled_recovers_after_feedback():
    task = get_task("balanced_brackets")
    seen_messages = {}

    def model(messages, attempt_index):
        seen_messages[attempt_index] = list(messages)
        # wrong on the first attempt, correct once feedback arrives
        return WRONG if attempt_index == 1 else _correct(task)

    result = control_agent(task, model, mode="controlled", max_attempts=4, model_name="stub")
    assert result.passed is True
    assert result.attempts_used == 2
    # the second attempt must have received failure feedback
    second = seen_messages[2]
    assert any("expected output" in m["content"] for m in second if m["role"] == "user")
    assert any(m["role"] == "assistant" for m in second)


def test_controlled_stops_early_when_first_attempt_passes():
    task = get_task("kth_largest")
    calls = {"n": 0}

    def model(messages, attempt_index):
        calls["n"] += 1
        return _correct(task)

    result = control_agent(task, model, mode="controlled", max_attempts=4)
    assert result.passed is True
    assert result.attempts_used == 1
    assert calls["n"] == 1  # did not waste further attempts


def test_controlled_gives_up_after_max_attempts():
    task = get_task("roman_to_int")
    result = control_agent(task, lambda messages, i: WRONG, mode="controlled", max_attempts=3)
    assert result.passed is False
    assert result.attempts_used == 3
    assert len(result.attempts) == 3


def test_result_to_dict_shape():
    task = get_task("caesar_cipher")
    result = control_agent(task, lambda messages, i: _correct(task), mode="one_shot")
    d = result.to_dict()
    assert d["passed"] is True
    assert d["task_id"] == "caesar_cipher"
    assert isinstance(d["attempts"], list) and d["attempts"][0]["total"] > 0
