"""End-to-end: natural language -> built graph -> executed by GraphExecutor.

Proves the agent-generated-topology slice runs on the real executor without any
external API key.
"""

import asyncio

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE_MAPPINGS
from custom_extensions.network_requests.extension import (
    EXTENSION_MAPPINGS as NETWORK_MAPPINGS,
)
from server.domain.services.graph_builder import build_graph
from server.domain.services.graph_executor import GraphExecutor

KNOWN = {**CORE_MAPPINGS["nodes"], **NETWORK_MAPPINGS["nodes"]}


class AcceptanceServer:
    def __init__(self):
        self.ENABLE_SMART_CACHE = True
        self.INSPECTION_DELAY = 0
        self.MAX_PARALLEL_NODES = 8
        self.client_id = "acceptance-client"
        self.current_workflow_id = "acceptance-workflow"
        self.sessions = {}
        self.rules = {}
        self.sent_messages = []
        self.nodes = KNOWN

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


def _run(prompt_dict, runtime="parallel"):
    server = AcceptanceServer()
    executor = GraphExecutor(server)
    graph = executor.prompt_to_graph(prompt_dict)
    response = {
        "prompt_id": "acceptance-prompt",
        "number": 1,
        "client_id": server.client_id,
        "workflow_id": server.current_workflow_id,
    }
    if runtime == "parallel":
        return asyncio.run(executor.run_parallel(graph, response)), server
    return asyncio.run(executor.run_sequential(graph, response)), server


def test_built_log_graph_executes_and_logs_literal():
    result = build_graph('log "hello harness"', known_nodes=KNOWN)
    graph_results, server = _run(result.prompt, "parallel")

    # The ConsoleLog node should carry the string through as its value.
    log_ids = [nid for nid, n in result.prompt.items() if n["type"] == "ConsoleLog"]
    assert log_ids
    assert graph_results[log_ids[0]].values == "hello harness"
    assert server.sent_messages  # results were streamed


def test_built_join_graph_executes():
    result = build_graph('concatenate "foo" and "bar" and log', known_nodes=KNOWN)
    graph_results, _ = _run(result.prompt, "parallel")
    log_ids = [nid for nid, n in result.prompt.items() if n["type"] == "ConsoleLog"]
    assert graph_results[log_ids[0]].values == "foo bar"


def test_built_wired_join_edges_execute_end_to_end():
    # The concat path is a wired nsString -> nsArray/append chain -> StringJoin.
    result = build_graph('concatenate "alpha" and "beta" then log it', known_nodes=KNOWN)
    # sanity: the graph actually contains wiring, not a literal array
    join = next(n for n in result.prompt.values() if n["type"] == "StringJoin")
    assert isinstance(join["inputs"]["array"], dict) and "originId" in join["inputs"]["array"]

    graph_results, _ = _run(result.prompt, "parallel")
    log_ids = [nid for nid, n in result.prompt.items() if n["type"] == "ConsoleLog"]
    assert graph_results[log_ids[0]].values == "alpha beta"
    # also verify sequential mode wires identically
    graph_results_seq, _ = _run(result.prompt, "sequential")
    assert graph_results_seq[log_ids[0]].values == "alpha beta"


def test_built_passthrough_pipe_executes():
    result = build_graph('log "piped" through a passthrough', known_nodes=KNOWN)
    graph_results, _ = _run(result.prompt, "parallel")
    log_ids = [nid for nid, n in result.prompt.items() if n["type"] == "ConsoleLog"]
    assert graph_results[log_ids[0]].values == "piped"
    assert any(n["type"] == "PassThrough" for n in result.prompt.values())


def test_built_graph_executes_sequentially_too():
    result = build_graph('log "seq mode"', known_nodes=KNOWN)
    graph_results, _ = _run(result.prompt, "sequential")
    log_ids = [nid for nid, n in result.prompt.items() if n["type"] == "ConsoleLog"]
    assert graph_results[log_ids[0]].values == "seq mode"
