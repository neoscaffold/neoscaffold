"""Run the agent-control experiment: one-shot vs controlled on complex tasks.

For each task, runs a single one-shot attempt and a controlled loop (up to
--max-attempts with test feedback) against a live model, then reports whether
each mode solved the task and how many attempts the controlled loop needed.

Usage (from the server/ directory, with OPENAI_API_KEY set):
    python -m agent_control.run_experiment --model gpt-5.6-terra --max-attempts 4
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Dict, List

from .controller import control_agent, make_openai_model
from .tasks import TASK_IDS, get_task


def _print_stream_factory(prefix: str):
    def on_token(chunk: str) -> None:
        sys.stdout.write(chunk)
        sys.stdout.flush()

    return on_token


def run(model_name: str, max_attempts: int, task_ids: List[str], stream: bool) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    one_shot_solved = 0
    controlled_solved = 0
    recovered = []  # solved by control but not one-shot

    for task_id in task_ids:
        task = get_task(task_id)
        on_token = _print_stream_factory(task_id) if stream else None
        model = make_openai_model(model_name, on_token=on_token)

        t0 = time.time()
        one = control_agent(task, model, mode="one_shot", model_name=model_name)
        controlled = control_agent(
            task, model, mode="controlled", max_attempts=max_attempts, model_name=model_name
        )
        elapsed = time.time() - t0

        one_shot_solved += 1 if one.passed else 0
        controlled_solved += 1 if controlled.passed else 0
        if controlled.passed and not one.passed:
            recovered.append(task_id)

        results.append(
            {
                "task_id": task_id,
                "title": task["title"],
                "one_shot_passed": one.passed,
                "controlled_passed": controlled.passed,
                "controlled_attempts": controlled.attempts_used,
                "controlled_progress": [
                    f"{a.passed_count}/{a.total}" for a in controlled.attempts
                ],
                "elapsed_s": round(elapsed, 1),
            }
        )
        print(
            f"[{task_id:16}] one-shot={'PASS' if one.passed else 'FAIL'}  "
            f"controlled={'PASS' if controlled.passed else 'FAIL'} "
            f"(attempts={controlled.attempts_used}, progress="
            f"{'->'.join(f'{a.passed_count}/{a.total}' for a in controlled.attempts)})",
            flush=True,
        )

    total = len(task_ids)
    summary = {
        "model": model_name,
        "max_attempts": max_attempts,
        "total_tasks": total,
        "one_shot_solved": one_shot_solved,
        "controlled_solved": controlled_solved,
        "recovered_by_control": recovered,
        "results": results,
    }
    print("\n=== SUMMARY ===")
    print(f"model: {model_name}  tasks: {total}  max_attempts: {max_attempts}")
    print(f"one-shot solved:   {one_shot_solved}/{total}")
    print(f"controlled solved: {controlled_solved}/{total}")
    print(f"recovered by control (failed one-shot, passed controlled): {recovered}")
    return summary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--max-attempts", type=int, default=4)
    parser.add_argument("--tasks", nargs="*", default=None, help="Subset of task ids.")
    parser.add_argument("--json", default=None, help="Write full results JSON to this path.")
    parser.add_argument("--stream", action="store_true", help="Stream model tokens to stdout.")
    args = parser.parse_args(argv)

    task_ids = args.tasks or TASK_IDS
    summary = run(args.model, args.max_attempts, task_ids, args.stream)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
