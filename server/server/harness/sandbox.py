"""Sandbox seam for node execution (harness.md §7).

v1.0.0 ships a minimal in-process guard: run a callable under a wall-clock
timeout so a runaway node cannot hang the executor. This is the seam where a
Dockerized (or Cloudflare-sandbox) per-node runner is swapped in later without
changing node code. Timeouts are recorded as metrics.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass
from typing import Any, Callable, Optional

from . import observability

DEFAULT_TIMEOUT_SECONDS = 30.0


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
