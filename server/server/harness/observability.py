"""Dependency-free observability: metrics, structured logs, timers.

Metrics are stored on the system itself and exported in Prometheus text
exposition format (PromQL-compatible) with no ``prometheus_client`` dependency
(utilities hoisted into the repo, harness.md §5). Structured logs are emitted as
one JSON object per line so a shipper can index fields for LogQL queries.
"""

from __future__ import annotations

import json
import sys
import threading
import time
from contextlib import contextmanager
from typing import Dict, Iterator, List, Optional, TextIO, Tuple

# Histogram buckets in seconds (upper bounds), matching Prometheus conventions.
DEFAULT_BUCKETS: Tuple[float, ...] = (
    0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0,
)

_LabelKey = Tuple[Tuple[str, str], ...]


def _label_key(labels: Dict[str, str]) -> _LabelKey:
    return tuple(sorted((str(k), str(v)) for k, v in labels.items()))


def _render_labels(key: _LabelKey, extra: Optional[Tuple[str, str]] = None) -> str:
    pairs = list(key)
    if extra is not None:
        pairs = pairs + [extra]
    if not pairs:
        return ""
    inner = ",".join(f'{name}="{_escape(value)}"' for name, value in pairs)
    return "{" + inner + "}"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


class MetricsRegistry:
    """A tiny thread-safe counter + histogram registry."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: Dict[str, Dict[_LabelKey, float]] = {}
        self._counter_help: Dict[str, str] = {}
        self._hist_buckets: Dict[str, Tuple[float, ...]] = {}
        self._hist_counts: Dict[str, Dict[_LabelKey, List[int]]] = {}
        self._hist_sum: Dict[str, Dict[_LabelKey, float]] = {}
        self._hist_total: Dict[str, Dict[_LabelKey, int]] = {}
        self._hist_help: Dict[str, str] = {}

    def inc(self, name: str, amount: float = 1.0, *, help: str = "", **labels: str) -> None:
        key = _label_key(labels)
        with self._lock:
            self._counter_help.setdefault(name, help)
            series = self._counters.setdefault(name, {})
            series[key] = series.get(key, 0.0) + amount

    def observe(
        self,
        name: str,
        value: float,
        *,
        help: str = "",
        buckets: Tuple[float, ...] = DEFAULT_BUCKETS,
        **labels: str,
    ) -> None:
        key = _label_key(labels)
        with self._lock:
            self._hist_help.setdefault(name, help)
            self._hist_buckets.setdefault(name, buckets)
            buckets = self._hist_buckets[name]
            counts = self._hist_counts.setdefault(name, {})
            if key not in counts:
                counts[key] = [0] * len(buckets)
            for i, upper in enumerate(buckets):
                if value <= upper:
                    counts[key][i] += 1
            self._hist_sum.setdefault(name, {})
            self._hist_sum[name][key] = self._hist_sum[name].get(key, 0.0) + value
            self._hist_total.setdefault(name, {})
            self._hist_total[name][key] = self._hist_total[name].get(key, 0) + 1

    def counter_value(self, name: str, **labels: str) -> float:
        with self._lock:
            return self._counters.get(name, {}).get(_label_key(labels), 0.0)

    def histogram_count(self, name: str, **labels: str) -> int:
        with self._lock:
            return self._hist_total.get(name, {}).get(_label_key(labels), 0)

    def render(self) -> str:
        """Render all metrics in Prometheus text exposition format."""
        lines: List[str] = []
        with self._lock:
            for name in sorted(self._counters):
                help_text = self._counter_help.get(name, "")
                if help_text:
                    lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} counter")
                for key in sorted(self._counters[name]):
                    lines.append(f"{name}{_render_labels(key)} {self._counters[name][key]}")

            for name in sorted(self._hist_counts):
                help_text = self._hist_help.get(name, "")
                if help_text:
                    lines.append(f"# HELP {name} {help_text}")
                lines.append(f"# TYPE {name} histogram")
                buckets = self._hist_buckets[name]
                for key in sorted(self._hist_counts[name]):
                    cumulative = self._hist_counts[name][key]
                    for i, upper in enumerate(buckets):
                        le = repr(upper)
                        lines.append(
                            f"{name}_bucket{_render_labels(key, ('le', le))} {cumulative[i]}"
                        )
                    total = self._hist_total[name][key]
                    lines.append(
                        f"{name}_bucket{_render_labels(key, ('le', '+Inf'))} {total}"
                    )
                    lines.append(f"{name}_sum{_render_labels(key)} {self._hist_sum[name][key]}")
                    lines.append(f"{name}_count{_render_labels(key)} {total}")
        return "\n".join(lines) + ("\n" if lines else "")

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._counter_help.clear()
            self._hist_buckets.clear()
            self._hist_counts.clear()
            self._hist_sum.clear()
            self._hist_total.clear()
            self._hist_help.clear()


# Process-wide default registry.
REGISTRY = MetricsRegistry()


def inc(name: str, amount: float = 1.0, *, help: str = "", **labels: str) -> None:
    REGISTRY.inc(name, amount, help=help, **labels)


def observe(name: str, value: float, *, help: str = "", **labels: str) -> None:
    REGISTRY.observe(name, value, help=help, **labels)


def render() -> str:
    return REGISTRY.render()


# --- structured logging (JSON lines for LogQL) ---
_log_stream: TextIO = sys.stderr


def set_log_stream(stream: TextIO) -> None:
    """Redirect structured log output (used by tests)."""
    global _log_stream
    _log_stream = stream


def log_event(event: str, level: str = "info", **fields: object) -> Dict[str, object]:
    """Emit one structured JSON log line and return the record."""
    record: Dict[str, object] = {
        "ts": time.time(),
        "level": level,
        "event": event,
    }
    record.update(fields)
    try:
        _log_stream.write(json.dumps(record, default=str) + "\n")
        _log_stream.flush()
    except Exception:
        pass
    return record


@contextmanager
def time_block(
    name: str,
    *,
    help: str = "",
    registry: Optional[MetricsRegistry] = None,
    **labels: str,
) -> Iterator[None]:
    """Observe the wall-clock duration of a block into a histogram (seconds)."""
    target = registry or REGISTRY
    start = time.perf_counter()
    try:
        yield
    finally:
        target.observe(name, time.perf_counter() - start, help=help, **labels)
