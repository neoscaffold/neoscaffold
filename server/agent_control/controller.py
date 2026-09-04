"""Agent control loop.

The core experiment: can we *control* a coding agent on complex tasks by running
its solution against hidden tests and feeding failures back for another attempt?

- ``mode="one_shot"``: a single attempt, no feedback.
- ``mode="controlled"``: up to ``max_attempts`` attempts; after each failure the
  first failing test (input / expected / actual / error) is fed back to the model.

The model is injected as ``model_fn(messages, attempt_index) -> str`` so the loop
is deterministic and unit-testable offline; ``make_openai_model`` provides the
live client.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from . import sandbox

# model_fn(messages, attempt_index) -> raw model text (which should contain code)
ModelFn = Callable[[List[Dict[str, str]], int], str]

SYSTEM_PROMPT = (
    "You are a coding agent. Given a problem, respond with ONLY a complete "
    "Python 3 program that reads from stdin and writes to stdout. No prose, no "
    "markdown fences. When given feedback about a failing test, fix your program "
    "and return the full corrected program."
)


@dataclass
class TestOutcome:
    input: str
    expected: str
    actual: str
    passed: bool
    error: str = ""


@dataclass
class Attempt:
    index: int
    code: str
    passed: bool
    passed_count: int
    total: int
    outcomes: List[TestOutcome] = field(default_factory=list)


@dataclass
class ControlResult:
    task_id: str
    mode: str
    model: str
    passed: bool
    attempts_used: int
    max_attempts: int
    attempts: List[Attempt] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "mode": self.mode,
            "model": self.model,
            "passed": self.passed,
            "attempts_used": self.attempts_used,
            "max_attempts": self.max_attempts,
            "attempts": [
                {
                    "index": a.index,
                    "passed": a.passed,
                    "passed_count": a.passed_count,
                    "total": a.total,
                }
                for a in self.attempts
            ],
        }


def extract_code(text: str) -> str:
    if not text:
        return ""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (match.group(1) if match else text).strip()


def run_tests(code: str, tests: List[Dict[str, str]], timeout: float) -> List[TestOutcome]:
    outcomes: List[TestOutcome] = []
    for test in tests:
        run = sandbox.run_python_code(code, stdin=test.get("input", ""), timeout=timeout)
        expected = test.get("output", "")
        passed = run.ok and run.stdout.strip() == expected.strip()
        error = ""
        if run.timed_out:
            error = "timed out"
        elif not run.ok:
            error = (run.stderr or "").strip()[-300:]
        outcomes.append(
            TestOutcome(
                input=test.get("input", ""),
                expected=expected,
                actual=run.stdout,
                passed=passed,
                error=error,
            )
        )
    return outcomes


def _initial_prompt(task: Dict[str, Any]) -> str:
    samples = "\n".join(
        f"Input:\n{s.get('input', '')}Output:\n{s.get('output', '')}"
        for s in task.get("public_samples", [])
    )
    return (
        f"Problem: {task.get('title')}\n\n{task.get('statement')}\n\n"
        f"Examples:\n{samples}"
    )


def _feedback(outcome: TestOutcome) -> str:
    detail = f"error: {outcome.error}" if outcome.error else f"your program printed: {outcome.actual!r}"
    return (
        "Your program is incorrect. On this input:\n"
        f"{outcome.input!r}\n"
        f"the expected output is:\n{outcome.expected!r}\n"
        f"but {detail}.\n"
        "Return a corrected, complete Python program."
    )


def control_agent(
    task: Dict[str, Any],
    model_fn: ModelFn,
    *,
    mode: str = "controlled",
    max_attempts: int = 4,
    model_name: str = "",
    timeout: float = 8.0,
    on_event: Optional[Callable[[str, Dict[str, Any]], None]] = None,
) -> ControlResult:
    """Run the control loop for one task and return the outcome."""
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _initial_prompt(task)},
    ]
    limit = 1 if mode == "one_shot" else max(1, max_attempts)
    attempts: List[Attempt] = []

    def emit(event: str, **data: Any) -> None:
        if on_event:
            try:
                on_event(event, {"task_id": task["id"], "mode": mode, **data})
            except Exception:
                pass

    for index in range(1, limit + 1):
        emit("attempt_start", attempt=index)
        raw = model_fn(messages, index)
        code = extract_code(raw)
        outcomes = run_tests(code, task.get("hidden_tests", []), timeout)
        passed_count = sum(1 for o in outcomes if o.passed)
        total = len(outcomes)
        ok = total > 0 and passed_count == total
        attempts.append(
            Attempt(
                index=index,
                code=code,
                passed=ok,
                passed_count=passed_count,
                total=total,
                outcomes=outcomes,
            )
        )
        emit("attempt_end", attempt=index, passed=ok, passed_count=passed_count, total=total)
        if ok:
            return ControlResult(
                task_id=task["id"],
                mode=mode,
                model=model_name,
                passed=True,
                attempts_used=index,
                max_attempts=limit,
                attempts=attempts,
            )
        # Feed the first failing test back for the next attempt.
        failing = next((o for o in outcomes if not o.passed), None)
        if failing is not None and index < limit:
            messages.append({"role": "assistant", "content": code})
            messages.append({"role": "user", "content": _feedback(failing)})

    return ControlResult(
        task_id=task["id"],
        mode=mode,
        model=model_name,
        passed=False,
        attempts_used=limit,
        max_attempts=limit,
        attempts=attempts,
    )


def make_openai_model(
    model_name: str = "gpt-5.6-terra",
    *,
    max_tokens: int = 1200,
    on_token: Optional[Callable[[str], None]] = None,
) -> ModelFn:
    """Build a live model function backed by the OpenAI API (streaming)."""
    from openai import OpenAI

    client = OpenAI()

    def model_fn(messages: List[Dict[str, str]], attempt_index: int) -> str:
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            max_completion_tokens=max_tokens,
        )
        parts: List[str] = []
        for event in stream:
            choices = getattr(event, "choices", None)
            delta = choices[0].delta.content if choices and choices[0].delta else None
            if delta:
                parts.append(delta)
                if on_token:
                    on_token(delta)
        return "".join(parts)

    return model_fn
