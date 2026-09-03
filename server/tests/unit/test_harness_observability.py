"""Tests for server.harness.observability (metrics, exposition, logging)."""

import io
import json

from server.harness.observability import (
    MetricsRegistry,
    log_event,
    set_log_stream,
    time_block,
)


def test_counter_increments_and_renders():
    reg = MetricsRegistry()
    reg.inc("neoscaffold_nodes_executed_total", help="nodes executed")
    reg.inc("neoscaffold_nodes_executed_total")
    assert reg.counter_value("neoscaffold_nodes_executed_total") == 2.0
    text = reg.render()
    assert "# TYPE neoscaffold_nodes_executed_total counter" in text
    assert "neoscaffold_nodes_executed_total 2.0" in text
    assert "# HELP neoscaffold_nodes_executed_total nodes executed" in text


def test_counter_with_labels():
    reg = MetricsRegistry()
    reg.inc("runs_total", mode="parallel")
    reg.inc("runs_total", mode="sequential")
    reg.inc("runs_total", mode="parallel")
    assert reg.counter_value("runs_total", mode="parallel") == 2.0
    assert reg.counter_value("runs_total", mode="sequential") == 1.0
    text = reg.render()
    assert 'runs_total{mode="parallel"} 2.0' in text
    assert 'runs_total{mode="sequential"} 1.0' in text


def test_histogram_render_shape():
    reg = MetricsRegistry()
    reg.observe("dur_seconds", 0.02, help="durations")
    reg.observe("dur_seconds", 0.2)
    assert reg.histogram_count("dur_seconds") == 2
    text = reg.render()
    assert "# TYPE dur_seconds histogram" in text
    assert 'dur_seconds_bucket{le="+Inf"} 2' in text
    assert "dur_seconds_count 2" in text
    assert "dur_seconds_sum" in text
    # 0.02 and 0.2 are both <= 0.5 bucket, only 0.2 is > 0.05
    assert 'dur_seconds_bucket{le="0.05"} 1' in text


def test_time_block_records_duration():
    reg = MetricsRegistry()
    with time_block("block_seconds", registry=reg, op="test"):
        pass
    assert reg.histogram_count("block_seconds", op="test") == 1


def test_log_event_emits_json_line():
    stream = io.StringIO()
    set_log_stream(stream)
    try:
        record = log_event("graph_build", level="info", prompt="make a string", nodes=3)
    finally:
        set_log_stream(__import__("sys").stderr)
    line = stream.getvalue().strip()
    parsed = json.loads(line)
    assert parsed["event"] == "graph_build"
    assert parsed["level"] == "info"
    assert parsed["nodes"] == 3
    assert "ts" in parsed
    assert record["event"] == "graph_build"


def test_render_empty_registry():
    assert MetricsRegistry().render() == ""
