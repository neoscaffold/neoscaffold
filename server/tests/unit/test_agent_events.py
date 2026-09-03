"""Tests for the agent/subagent event log and builder instrumentation."""

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET
from server.domain.services.graph_builder import build_graph
from server.harness.agent_events import AGENT_EVENTS, AgentEventLog

KNOWN = {**CORE["nodes"], **NET["nodes"]}


def test_start_finish_span():
    log = AgentEventLog()
    event_id = log.start("graph_build", "do a thing", detail={"prompt": "x"})
    events = log.recent()
    assert events[-1]["status"] == "started"
    log.finish(event_id, status="succeeded", detail={"nodes": 2})
    events = log.recent()
    last = events[-1]
    assert last["id"] == event_id
    assert last["status"] == "succeeded"
    assert last["ended_at"] is not None
    assert last["detail"]["nodes"] == 2


def test_record_one_shot_with_parent():
    log = AgentEventLog()
    parent = log.start("graph_build", "parent")
    child = log.record("node", "nsString", parent_id=parent, detail={"node_id": "1"})
    events = {e["id"]: e for e in log.recent()}
    assert events[child]["parent_id"] == parent
    assert events[child]["status"] == "succeeded"


def test_recent_limit_and_capacity():
    log = AgentEventLog(capacity=5)
    for i in range(10):
        log.record("node", f"n{i}")
    recent = log.recent(limit=3)
    assert len(recent) == 3
    # capacity trims the oldest
    assert len(log.recent(limit=100)) == 5


def test_subscribers_receive_events():
    log = AgentEventLog()
    seen = []
    log.subscribe(lambda e: seen.append(e))
    log.record("test", "x")
    assert seen and seen[-1]["kind"] == "test"


def test_failing_subscriber_does_not_break_emit():
    log = AgentEventLog()

    def boom(_):
        raise RuntimeError("nope")

    log.subscribe(boom)
    # should not raise
    log.record("test", "x")


def test_build_graph_emits_agent_events():
    AGENT_EVENTS.clear()
    build_graph('log "watch me"', known_nodes=KNOWN)
    events = AGENT_EVENTS.recent(limit=100)
    kinds = [e["kind"] for e in events]
    assert "graph_build" in kinds
    # per-node child spans parented to the build span
    build_events = [e for e in events if e["kind"] == "graph_build"]
    build_id = build_events[-1]["id"]
    node_events = [e for e in events if e["kind"] == "node" and e["parent_id"] == build_id]
    assert node_events
    assert build_events[-1]["status"] == "succeeded"
    assert build_events[-1]["detail"]["nodes"] >= 1
