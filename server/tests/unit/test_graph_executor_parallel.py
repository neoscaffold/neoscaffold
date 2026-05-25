import asyncio
import threading
import time

import networkx as nx

from server.domain.enums.runtime_action import RuntimeAction
from server.domain.models.evaluation_action import EvaluationAction
from server.domain.services.graph_executor import GraphExecutor


class FakeServer:
    def __init__(self, max_parallel_nodes=8, enable_smart_cache=False):
        self.ENABLE_SMART_CACHE = enable_smart_cache
        self.INSPECTION_DELAY = 0
        self.MAX_PARALLEL_NODES = max_parallel_nodes
        self.client_id = "test-client"
        self.current_workflow_id = "test-workflow"
        self.sessions = {}
        self.rules = {}
        self.sent_messages = []
        self.nodes = {
            "AsyncValue": {"python_class": AsyncValueNode},
            "AwaitableValue": {"python_class": AwaitableValueNode},
            "CountingValue": {"python_class": CountingValueNode},
            "GotoOnce": {"python_class": GotoOnceNode},
            "SlowCancellableValue": {"python_class": SlowCancellableValueNode},
            "SyncValue": {"python_class": SyncValueNode},
            "Join": {"python_class": JoinNode},
        }

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


class AsyncValueNode:
    active_count = 0
    max_active_count = 0

    INPUT = {"required_inputs": {}}
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    async def evaluate(self, node_inputs):
        AsyncValueNode.active_count += 1
        AsyncValueNode.max_active_count = max(
            AsyncValueNode.max_active_count,
            AsyncValueNode.active_count,
        )
        await asyncio.sleep(0.01)
        AsyncValueNode.active_count -= 1
        return self._node.node_id


class SyncValueNode:
    active_count = 0
    max_active_count = 0
    lock = threading.Lock()

    INPUT = {"required_inputs": {}}
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    def evaluate(self, node_inputs):
        with SyncValueNode.lock:
            SyncValueNode.active_count += 1
            SyncValueNode.max_active_count = max(
                SyncValueNode.max_active_count,
                SyncValueNode.active_count,
            )
        time.sleep(0.01)
        with SyncValueNode.lock:
            SyncValueNode.active_count -= 1
        return self._node.node_id


class AwaitableValueNode:
    INPUT = {"required_inputs": {}}
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    def evaluate(self, node_inputs):
        async def evaluate_later():
            await asyncio.sleep(0)
            return self._node.node_id

        return evaluate_later()


class SlowCancellableValueNode:
    active_count = 0
    all_started = None
    cancelled_nodes = set()
    delays = {"a": 0.01, "b": 0.2}

    INPUT = {"required_inputs": {}}
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    async def evaluate(self, node_inputs):
        node_id = self._node.node_id
        SlowCancellableValueNode.active_count += 1
        if (
            SlowCancellableValueNode.active_count == 2
            and SlowCancellableValueNode.all_started
        ):
            SlowCancellableValueNode.all_started.set()

        try:
            await asyncio.sleep(SlowCancellableValueNode.delays[node_id])
            return node_id
        except asyncio.CancelledError:
            SlowCancellableValueNode.cancelled_nodes.add(node_id)
            raise
        finally:
            SlowCancellableValueNode.active_count -= 1


class CountingValueNode:
    counts = {}
    init_count = 0

    INPUT = {"required_inputs": {}}
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    def __init__(self):
        CountingValueNode.init_count += 1

    def evaluate(self, node_inputs):
        node_id = self._node.node_id
        CountingValueNode.counts[node_id] = CountingValueNode.counts.get(node_id, 0) + 1
        return f"{node_id}:{CountingValueNode.counts[node_id]}"


class GotoOnceNode:
    has_jumped = False
    init_count = 0

    INPUT = {
        "required_inputs": {
            "value": {"kind": "*", "name": "value"},
        }
    }
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    def __init__(self):
        GotoOnceNode.init_count += 1

    def evaluate(self, node_inputs):
        if not GotoOnceNode.has_jumped:
            GotoOnceNode.has_jumped = True
            self._memory["evaluation_override_actions"][self._node.node_id] = (
                EvaluationAction(
                    node_id=self._node.node_id,
                    runtime_action=RuntimeAction.GOTO,
                    destination_node_id="b",
                ).to_dict()
            )
        return "goto"


class JoinNode:
    INPUT = {
        "required_inputs": {
            "left": {"kind": "*", "name": "left"},
            "right": {"kind": "*", "name": "right"},
        }
    }
    OUTPUT = {"kind": "VALUE", "name": "VALUE", "cacheable": True}

    def evaluate(self, node_inputs):
        required_inputs = node_inputs["required_inputs"]
        return [
            required_inputs["left"]["values"],
            required_inputs["right"]["values"],
        ]


def build_diamond_graph():
    graph = nx.DiGraph()
    graph.add_node("a", kind="AsyncValue", nickname="A")
    graph.add_node("b", kind="AsyncValue", nickname="B")
    graph.add_node(
        "join",
        kind="Join",
        nickname="Join",
        left={"originId": "a"},
        right={"originId": "b"},
    )
    graph.add_edges_from([("a", "join"), ("b", "join")])
    return graph


def build_sync_diamond_graph():
    graph = build_diamond_graph()
    graph.nodes["a"]["kind"] = "SyncValue"
    graph.nodes["b"]["kind"] = "SyncValue"
    return graph


def build_awaitable_graph():
    graph = nx.DiGraph()
    graph.add_node("a", kind="AwaitableValue", nickname="A")
    return graph


def build_independent_slow_graph():
    graph = nx.DiGraph()
    graph.add_node("a", kind="SlowCancellableValue", nickname="A")
    graph.add_node("b", kind="SlowCancellableValue", nickname="B")
    return graph


def build_soft_goto_graph():
    graph = nx.DiGraph()
    graph.add_node("a", kind="CountingValue", nickname="A")
    graph.add_node("b", kind="CountingValue", nickname="B")
    graph.add_node(
        "goto",
        kind="GotoOnce",
        nickname="Goto",
        value={"originId": "b"},
    )
    graph.add_node("c", kind="CountingValue", nickname="C")
    graph.add_edges_from([("a", "b"), ("b", "goto"), ("goto", "c")])
    return graph


def run_parallel(graph, max_parallel_nodes=8, enable_smart_cache=False):
    AsyncValueNode.active_count = 0
    AsyncValueNode.max_active_count = 0
    SyncValueNode.active_count = 0
    SyncValueNode.max_active_count = 0
    CountingValueNode.counts = {}
    CountingValueNode.init_count = 0
    GotoOnceNode.has_jumped = False
    GotoOnceNode.init_count = 0
    server = FakeServer(
        max_parallel_nodes=max_parallel_nodes,
        enable_smart_cache=enable_smart_cache,
    )
    server.client_id = "wrong-client"
    server.current_workflow_id = "wrong-workflow"
    executor = GraphExecutor(server)
    response = {
        "prompt_id": "prompt",
        "number": 1,
        "client_id": "test-client",
        "workflow_id": "test-workflow",
    }
    return asyncio.run(executor.run_parallel(graph, response)), server


def run_sequential(graph):
    AsyncValueNode.active_count = 0
    AsyncValueNode.max_active_count = 0
    SyncValueNode.active_count = 0
    SyncValueNode.max_active_count = 0
    CountingValueNode.counts = {}
    CountingValueNode.init_count = 0
    GotoOnceNode.has_jumped = False
    GotoOnceNode.init_count = 0
    server = FakeServer()
    server.client_id = "wrong-client"
    server.current_workflow_id = "wrong-workflow"
    executor = GraphExecutor(server)
    response = {
        "prompt_id": "prompt",
        "number": 1,
        "client_id": "test-client",
        "workflow_id": "test-workflow",
    }
    return asyncio.run(executor.run_sequential(graph, response)), server


def test_parallel_executor_runs_ready_siblings_concurrently_and_waits_for_join():
    graph_results, _server = run_parallel(build_diamond_graph(), max_parallel_nodes=2)

    assert AsyncValueNode.max_active_count == 2
    assert graph_results["a"].values == "a"
    assert graph_results["b"].values == "b"
    assert graph_results["join"].values == ["a", "b"]


def test_parallel_executor_respects_max_concurrency():
    graph_results, _server = run_parallel(build_diamond_graph(), max_parallel_nodes=1)

    assert AsyncValueNode.max_active_count == 1
    assert graph_results["join"].values == ["a", "b"]


def test_parallel_executor_runs_sync_nodes_in_worker_threads():
    graph_results, _server = run_parallel(
        build_sync_diamond_graph(),
        max_parallel_nodes=2,
    )

    assert SyncValueNode.max_active_count == 2
    assert graph_results["join"].values == ["a", "b"]


def test_sequential_executor_awaits_async_nodes():
    graph_results, _server = run_sequential(build_diamond_graph())

    assert graph_results["a"].values == "a"
    assert graph_results["b"].values == "b"
    assert graph_results["join"].values == ["a", "b"]


def test_executor_awaits_sync_evaluate_returning_awaitable():
    graph_results, _server = run_parallel(build_awaitable_graph())

    assert graph_results["a"].values == "a"


def test_executor_sends_updates_to_response_client_id():
    _graph_results, server = run_parallel(build_awaitable_graph())

    assert server.sent_messages
    assert {message["sid"] for message in server.sent_messages} == {"test-client"}


def test_parallel_executor_honors_stop_requested_while_tasks_are_running():
    async def run_with_runtime_stop():
        SlowCancellableValueNode.active_count = 0
        SlowCancellableValueNode.all_started = asyncio.Event()
        SlowCancellableValueNode.cancelled_nodes = set()

        server = FakeServer(max_parallel_nodes=2)
        server.sessions = {
            "test-client": {
                "test-workflow": {
                    "interventions": {
                        "stop-points": {"nodes": {}, "all_stop": False},
                    },
                },
            },
        }
        executor = GraphExecutor(server)
        response = {
            "prompt_id": "prompt",
            "number": 1,
            "client_id": "test-client",
            "workflow_id": "test-workflow",
        }

        execution_task = asyncio.create_task(
            executor.run_parallel(build_independent_slow_graph(), response)
        )
        await asyncio.wait_for(SlowCancellableValueNode.all_started.wait(), 1)
        server.sessions["test-client"]["test-workflow"]["interventions"][
            "stop-points"
        ]["all_stop"] = True

        return await asyncio.wait_for(execution_task, 1), server

    graph_results, server = asyncio.run(run_with_runtime_stop())

    assert graph_results["a"].values == "a"
    assert "b" not in graph_results
    assert SlowCancellableValueNode.cancelled_nodes == {"b"}
    assert any(
        message["data"].get("stop-point") == "b"
        for message in server.sent_messages
    )


def test_parallel_executor_honors_stop_requested_while_paused():
    async def run_with_pause_then_stop():
        server = FakeServer(max_parallel_nodes=1)
        server.sessions = {
            "test-client": {
                "test-workflow": {
                    "interventions": {
                        "breakpoints": {
                            "nodes": {},
                            "all_break": True,
                        },
                        "stop-points": {"nodes": {}, "all_stop": False},
                    },
                },
            },
        }
        executor = GraphExecutor(server)
        response = {
            "prompt_id": "prompt",
            "number": 1,
            "client_id": "test-client",
            "workflow_id": "test-workflow",
        }

        execution_task = asyncio.create_task(
            executor.run_parallel(build_awaitable_graph(), response)
        )
        for _ in range(10):
            if any(
                message["data"].get("breakpoint") == "a"
                for message in server.sent_messages
            ):
                break
            await asyncio.sleep(0.01)

        server.sessions["test-client"]["test-workflow"]["interventions"][
            "stop-points"
        ]["all_stop"] = True

        return await asyncio.wait_for(execution_task, 1), server

    graph_results, server = asyncio.run(run_with_pause_then_stop())

    assert graph_results == {}
    assert any(
        message["data"].get("breakpoint") == "a"
        for message in server.sent_messages
    )
    assert any(
        message["data"].get("stop-point") == "a"
        for message in server.sent_messages
    )


def test_sequential_executor_honors_restart_requested_while_paused():
    async def run_with_pause_then_restart():
        server = FakeServer(max_parallel_nodes=1)
        server.sessions = {
            "test-client": {
                "test-workflow": {
                    "interventions": {
                        "breakpoints": {
                            "nodes": {},
                            "all_break": True,
                        },
                        "restart-points": {"nodes": {}, "all_restart": False},
                    },
                },
            },
        }
        executor = GraphExecutor(server)
        response = {
            "prompt_id": "prompt",
            "number": 1,
            "client_id": "test-client",
            "workflow_id": "test-workflow",
        }

        execution_task = asyncio.create_task(
            executor.run_sequential(build_awaitable_graph(), response)
        )
        for _ in range(10):
            if any(
                message["data"].get("breakpoint") == "a"
                for message in server.sent_messages
            ):
                break
            await asyncio.sleep(0.01)

        server.sessions["test-client"]["test-workflow"]["interventions"][
            "restart-points"
        ]["all_restart"] = True

        return await asyncio.wait_for(execution_task, 1), server

    graph_results, server = asyncio.run(run_with_pause_then_restart())

    assert graph_results["a"].values == "a"
    assert any(
        message["data"].get("breakpoint") == "a"
        for message in server.sent_messages
    )
    assert any(
        message["data"].get("restart-point") == "a"
        for message in server.sent_messages
    )


def test_parallel_executor_honors_restart_requested_while_paused():
    async def run_with_pause_then_restart():
        server = FakeServer(max_parallel_nodes=1)
        server.sessions = {
            "test-client": {
                "test-workflow": {
                    "interventions": {
                        "breakpoints": {
                            "nodes": {},
                            "all_break": True,
                        },
                        "restart-points": {"nodes": {}, "all_restart": False},
                    },
                },
            },
        }
        executor = GraphExecutor(server)
        response = {
            "prompt_id": "prompt",
            "number": 1,
            "client_id": "test-client",
            "workflow_id": "test-workflow",
        }

        execution_task = asyncio.create_task(
            executor.run_parallel(build_awaitable_graph(), response)
        )
        for _ in range(10):
            if any(
                message["data"].get("breakpoint") == "a"
                for message in server.sent_messages
            ):
                break
            await asyncio.sleep(0.01)

        server.sessions["test-client"]["test-workflow"]["interventions"][
            "restart-points"
        ]["all_restart"] = True

        return await asyncio.wait_for(execution_task, 1), server

    graph_results, server = asyncio.run(run_with_pause_then_restart())

    assert graph_results["a"].values == "a"
    assert any(
        message["data"].get("breakpoint") == "a"
        for message in server.sent_messages
    )
    assert any(
        message["data"].get("restart-point") == "a"
        for message in server.sent_messages
    )


def test_parallel_executor_supports_soft_goto_to_completed_upstream_node():
    graph_results, _server = run_parallel(build_soft_goto_graph())

    assert CountingValueNode.counts["a"] == 1
    assert CountingValueNode.counts["b"] == 2
    assert CountingValueNode.counts["c"] == 1
    assert graph_results["a"].values == "a:1"
    assert graph_results["b"].values == "b:2"
    assert graph_results["c"].values == "c:1"


def test_parallel_soft_goto_busts_smart_cache_for_destination_and_descendants():
    graph_results, _server = run_parallel(
        build_soft_goto_graph(),
        enable_smart_cache=True,
    )

    assert graph_results["b"].values == "b:2"
    assert CountingValueNode.init_count == 4
    assert GotoOnceNode.init_count == 2
