"""Sandbox seam for node execution (harness.md §7).

v1.0.0 ships a minimal in-process guard: run a callable under a wall-clock
timeout so a runaway node cannot hang the executor. This is the seam where a
Dockerized (or Cloudflare-sandbox) per-node runner is swapped in later without
changing node code. Timeouts are recorded as metrics.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass
from typing import Any, Callable, Optional

from . import observability

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_CODE_TIMEOUT_SECONDS = 10.0


@dataclass
class GuardResult:
    """Outcome of a guarded call."""

    ok: bool
    value: Any = None
    error: Optional[BaseException] = None
    timed_out: bool = False
    duration_seconds: float = 0.0


def run_guarded(
    fn: Callable[..., Any],
    *args: Any,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    label: str = "node",
    **kwargs: Any,
) -> GuardResult:
    """Run ``fn(*args, **kwargs)`` with a wall-clock timeout.

    Returns a :class:`GuardResult` instead of raising, so the executor can decide
    to reject/repair/escalate. On timeout the underlying worker thread is left to
    finish in the background (a true kill requires the container runner this seam
    will host); the caller is unblocked and the event is recorded as a metric.
    """
    start = time.perf_counter()
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn, *args, **kwargs)
    try:
        value = future.result(timeout=timeout)
        duration = time.perf_counter() - start
        observability.observe(
            "neoscaffold_sandbox_duration_seconds",
            duration,
            help="Guarded execution duration",
            label=label,
        )
        executor.shutdown(wait=False)
        return GuardResult(ok=True, value=value, duration_seconds=duration)
    except FuturesTimeout:
        duration = time.perf_counter() - start
        observability.inc(
            "neoscaffold_sandbox_timeouts_total",
            help="Guarded executions that exceeded their timeout",
            label=label,
        )
        # Do not block on the runaway worker.
        executor.shutdown(wait=False)
        return GuardResult(ok=False, timed_out=True, duration_seconds=duration)
    except BaseException as exc:  # noqa: BLE001 - surface any node error as data
        duration = time.perf_counter() - start
        observability.inc(
            "neoscaffold_sandbox_errors_total",
            help="Guarded executions that raised",
            label=label,
        )
        executor.shutdown(wait=False)
        return GuardResult(ok=False, error=exc, duration_seconds=duration)


@dataclass
class CodeRunResult:
    """Outcome of running a code snippet in a subprocess."""

    ok: bool
    stdout: str = ""
    stderr: str = ""
    returncode: Optional[int] = None
    timed_out: bool = False
    duration_seconds: float = 0.0


def run_python_code(
    code: str,
    stdin: str = "",
    *,
    timeout: float = DEFAULT_CODE_TIMEOUT_SECONDS,
    label: str = "agent_code",
) -> CodeRunResult:
    """Run agent-authored Python in a subprocess with a wall-clock timeout.

    This is the first-step sandbox for verifying generated solutions (harness.md
    §7): a fresh temp dir, captured stdout/stderr, and a hard timeout. It is not
    a security boundary; the Docker/Cloudflare runner the seam targets is where
    real isolation lands.
    """
    start = time.perf_counter()
    with tempfile.TemporaryDirectory() as work_dir:
        script_path = os.path.join(work_dir, "solution.py")
        with open(script_path, "w", encoding="utf-8") as handle:
            handle.write(code or "")
        try:
            proc = subprocess.run(
                [sys.executable, script_path],
                input=stdin,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=work_dir,
            )
            duration = time.perf_counter() - start
            observability.observe(
                "neoscaffold_code_run_seconds",
                duration,
                help="Duration of a sandboxed code run",
                label=label,
            )
            return CodeRunResult(
                ok=(proc.returncode == 0),
                stdout=proc.stdout,
                stderr=proc.stderr,
                returncode=proc.returncode,
                duration_seconds=duration,
            )
        except subprocess.TimeoutExpired as exc:
            observability.inc(
                "neoscaffold_code_run_timeouts_total",
                help="Sandboxed code runs that timed out",
                label=label,
            )
            return CodeRunResult(
                ok=False,
                stdout=exc.stdout or "" if isinstance(exc.stdout, str) else "",
                stderr="timeout",
                timed_out=True,
                duration_seconds=time.perf_counter() - start,
            )
