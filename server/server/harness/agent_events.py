"""In-repo agent/subagent event log for visibility into the swarm.

Records span-like events (start/finish, with parent linkage) for agent work such
as graph builds and prompt-driven nodes, so users and other agents can see what
the subagents are doing. A bounded ring buffer keeps recent events; subscribers
(e.g. the WebSocket bridge) receive events live. Thread-safe and dependency-free.
"""

from __future__ import annotations

import itertools
import threading
import time
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional

STARTED = "started"
RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"


@dataclass
class AgentEvent:
    id: str
    parent_id: Optional[str]
    kind: str
    name: str
    status: str
    started_at: float
    ended_at: Optional[float] = None
    detail: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentEventLog:
    """A bounded, thread-safe log of agent/subagent events with live subscribers."""

    def __init__(self, capacity: int = 500):
        self._lock = threading.Lock()
        self._capacity = capacity
        self._events: "OrderedDict[str, AgentEvent]" = OrderedDict()
        self._counter = itertools.count(1)
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def _next_id(self) -> str:
        return f"ae-{next(self._counter)}"

    def _notify(self, event: AgentEvent) -> None:
        payload = event.to_dict()
        for subscriber in list(self._subscribers):
            try:
                subscriber(payload)
            except Exception:
                # A dead/failing subscriber must never break event emission.
                pass

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        with self._lock:
            self._subscribers.append(callback)

    def clear_subscribers(self) -> None:
        with self._lock:
            self._subscribers = []

    def start(
        self,
        kind: str,
        name: str,
        *,
        parent_id: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Open a span; returns its id. Call :meth:`finish` to close it."""
        with self._lock:
            event = AgentEvent(
                id=self._next_id(),
                parent_id=parent_id,
                kind=kind,
                name=name,
                status=STARTED,
                started_at=time.time(),
                detail=dict(detail or {}),
            )
            self._events[event.id] = event
            while len(self._events) > self._capacity:
                self._events.popitem(last=False)
            snapshot = AgentEvent(**event.to_dict())
        self._notify(snapshot)
        return event.id

    def finish(
        self,
        event_id: str,
        *,
        status: str = SUCCEEDED,
        detail: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._lock:
            event = self._events.get(event_id)
            if event is None:
                return
            event.status = status
            event.ended_at = time.time()
            if detail:
                event.detail.update(detail)
            snapshot = AgentEvent(**event.to_dict())
        self._notify(snapshot)

    def record(
        self,
        kind: str,
        name: str,
        *,
        status: str = SUCCEEDED,
        parent_id: Optional[str] = None,
        detail: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Record a completed one-shot event."""
        event_id = self.start(kind, name, parent_id=parent_id, detail=detail)
        self.finish(event_id, status=status)
        return event_id

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            events = list(self._events.values())
        if limit and limit > 0:
            events = events[-limit:]
        return [event.to_dict() for event in events]

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


# Process-wide default log.
AGENT_EVENTS = AgentEventLog()
