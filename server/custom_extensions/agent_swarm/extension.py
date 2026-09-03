"""agent_swarm extension: a fork-join swarm of coding agents.

Prompt mode can build a graph that fans out to one ``SwarmSolverNode`` per
problem. Each solver runs an independent agent that writes a Python solution,
streams its work to the UI scoped to its node, and verifies the solution by
running it in the sandbox against sample I/O. A ``SwarmJoinNode`` fork-joins the
results into a report.

Offline by default (deterministic reference solutions, no API key) so automated
tests pass; when ``OPENAI_API_KEY`` is set it uses a real model (default
``gpt-5.6-terra``) with token streaming.
"""

from __future__ import annotations

import os
import re

from .problems import PROBLEM_IDS, get_problem

version = "1.0.0"

DEFAULT_MODEL = os.environ.get("NEOSCAFFOLD_SWARM_MODEL", "gpt-5.6-terra")

try:
    from server.harness import sandbox
    from server.harness.agent_events import AGENT_EVENTS
except Exception:  # keep the extension importable even if harness is unavailable
    sandbox = None
    AGENT_EVENTS = None


def _get(node_inputs, group, name, default=None):
    return (node_inputs.get(group, {}) or {}).get(name, {}).get("values", default)


def _stream(node_id, chunk, name=None):
    if AGENT_EVENTS is not None and node_id:
        try:
            AGENT_EVENTS.stream(node_id, chunk, name=name)
        except Exception:
            pass


def _extract_code(text):
    """Pull a Python program out of a model response (fenced block or raw)."""
    if not text:
        return ""
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.S)
    return (match.group(1) if match else text).strip()


def offline_coder(problem, stream):
    """Deterministic coder: emit the known-correct reference solution."""
    code = problem.get("reference_solution", "")
    for i in range(0, len(code), 40):
        stream(code[i : i + 40])
    return code


def openai_coder(problem, stream, model=DEFAULT_MODEL):
    """Live coder: stream a solution from an OpenAI model."""
    from openai import OpenAI

    client = OpenAI()
    samples = "\n".join(
        f"input:\n{s.get('input', '')}\noutput:\n{s.get('output', '')}"
        for s in problem.get("samples", [])
    )
    prompt = (
        "You are a competitive-programming agent. Solve the problem and respond "
        "with ONLY a complete Python 3 program that reads from stdin and writes "
        "to stdout. No explanation, no markdown fences.\n\n"
        f"Title: {problem.get('title')}\n\n{problem.get('statement')}\n\n"
        f"Samples:\n{samples}\n"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        max_completion_tokens=900,
    )
    parts = []
    for event in response:
        choices = getattr(event, "choices", None)
        delta = choices[0].delta.content if choices and choices[0].delta else None
        if delta:
            parts.append(delta)
            stream(delta)
    return _extract_code("".join(parts))


def _select_coder(model):
    """Pick the live coder when a key is configured, else the offline coder."""
    offline_forced = os.environ.get("NEOSCAFFOLD_SWARM_OFFLINE", "").lower() in ("1", "true", "yes")
    if os.environ.get("OPENAI_API_KEY") and not offline_forced:
        return lambda problem, stream: openai_coder(problem, stream, model=model or DEFAULT_MODEL)
    return offline_coder


def verify(code, samples):
    """Run the code in the sandbox against each sample; report pass/fail."""
    results = []
    if sandbox is None:
        return results
    for sample in samples:
        run = sandbox.run_python_code(code, stdin=sample.get("input", ""), timeout=8)
        passed = run.ok and run.stdout.strip() == sample.get("output", "").strip()
        results.append(
            {
                "passed": passed,
                "stdout": run.stdout,
                "expected": sample.get("output", ""),
                "timed_out": run.timed_out,
                "stderr": (run.stderr or "")[:400],
            }
        )
    return results


def solve(problem, node_id, *, node_label=None, model=None, coder=None):
    """Run one agent: generate a solution, stream progress, verify it."""
    label = node_label or f"cf {problem.get('codeforces_id')}"
    event_id = None
    if AGENT_EVENTS is not None:
        event_id = AGENT_EVENTS.start(
            "solver",
            label,
            detail={"problem": problem.get("codeforces_id"), "title": problem.get("title")},
        )

    def stream(chunk):
        _stream(node_id, chunk, name=label)

    stream(f"[agent] problem {problem.get('codeforces_id')}: {problem.get('title')}\n")
    used = coder or _select_coder(model)
    is_offline = used is offline_coder
    error = None
    code = ""
    try:
        stream("[agent] generating solution...\n")
        code = used(problem, stream)
    except Exception as exc:  # surface coder failures as data
        error = str(exc)
        stream(f"\n[agent] coder error: {error}\n")

    samples = problem.get("samples", [])
    stream(f"\n[agent] verifying against {len(samples)} sample(s) in the sandbox...\n")
    sample_results = verify(code, samples) if code and samples else []
    passed_count = sum(1 for r in sample_results if r["passed"])
    verified = bool(sample_results) and passed_count == len(sample_results)
    stream(f"[agent] verified={verified} ({passed_count}/{len(sample_results)} samples)\n")

    if AGENT_EVENTS is not None and event_id is not None:
        AGENT_EVENTS.finish(
            event_id,
            status="succeeded" if verified else "failed",
            detail={"verified": verified, "samples": f"{passed_count}/{len(sample_results)}"},
        )

    return {
        "problem_id": problem.get("codeforces_id"),
        "title": problem.get("title"),
        "node_id": node_id,
        "model": "offline" if is_offline else (model or DEFAULT_MODEL),
        "code": code,
        "verified": verified,
        "samples_passed": passed_count,
        "samples_total": len(sample_results),
        "sample_results": sample_results,
        "error": error,
    }


class SwarmSolverNode:
    CATEGORY = "agent"
    SUBCATEGORY = "swarm"
    DESCRIPTION = (
        "An independent coding agent: given a Codeforces problem id, it writes a "
        "Python solution, streams its work to the UI (scoped to this node), and "
        "verifies the solution in the sandbox against sample I/O."
    )

    INPUT = {
        "required_inputs": {
            "problem_id": {
                "kind": "string",
                "name": "problem_id",
                "widget": {"kind": "string", "name": "problem_id", "default": ""},
            },
        },
        "optional_inputs": {
            "model": {
                "kind": "string",
                "name": "model",
                "widget": {"kind": "string", "name": "model", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "solution",
        "cacheable": False,
    }

    def _node_id(self):
        node = getattr(self, "_node", None)
        return getattr(node, "node_id", None) or "swarm-node"

    def evaluate(self, node_inputs):
        problem_id = _get(node_inputs, "required_inputs", "problem_id", "")
        model = _get(node_inputs, "optional_inputs", "model", "") or None
        node_id = self._node_id()
        problem = get_problem(problem_id)
        if problem is None:
            _stream(node_id, f"[agent] unknown problem '{problem_id}'\n", name=str(problem_id))
            return {
                "problem_id": problem_id,
                "node_id": node_id,
                "verified": False,
                "error": "unknown problem",
            }
        return solve(problem, node_id, node_label=f"cf {problem_id}", model=model)


class SwarmJoinNode:
    CATEGORY = "agent"
    SUBCATEGORY = "swarm"
    DESCRIPTION = (
        "Fork-join: aggregate the swarm's solver results into a single report "
        "showing how each agent solved and verified its problem."
    )

    INPUT = {
        "required_inputs": {
            "results": {
                "kind": "array",
                "name": "results",
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "report",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        results = _get(node_inputs, "required_inputs", "results", []) or []
        if not isinstance(results, list):
            results = [results]
        problems = []
        solved = 0
        for result in results:
            if not isinstance(result, dict):
                continue
            if result.get("verified"):
                solved += 1
            problems.append(
                {
                    "problem_id": result.get("problem_id"),
                    "title": result.get("title"),
                    "verified": bool(result.get("verified")),
                    "samples": f"{result.get('samples_passed', 0)}/{result.get('samples_total', 0)}",
                    "model": result.get("model"),
                    "node_id": result.get("node_id"),
                }
            )
        report = {"total": len(problems), "solved": solved, "problems": problems}
        if AGENT_EVENTS is not None:
            try:
                AGENT_EVENTS.record(
                    "fork_join", "SwarmJoin", detail={"solved": solved, "total": len(problems)}
                )
            except Exception:
                pass
        return report


EXTENSION_MAPPINGS = {
    "name": "AgentSwarm",
    "version": version,
    "description": "A fork-join swarm of coding agents with per-node streaming and verification.",
    "javascript_class_name": "AgentSwarm",
    "nodes": {
        "SwarmSolverNode": {
            "python_class": SwarmSolverNode,
            "javascript_class_name": "SwarmSolverNode",
            "display_name": "SwarmSolverNode",
        },
        "SwarmJoinNode": {
            "python_class": SwarmJoinNode,
            "javascript_class_name": "SwarmJoinNode",
            "display_name": "SwarmJoinNode",
        },
    },
    "rules": {},
}
