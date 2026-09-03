"""End-to-end execution of a PromptNode graph through GraphExecutor."""

import asyncio

from custom_extensions.agent_graph.extension import EXTENSION_MAPPINGS as AGENT
from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE
from custom_extensions.network_requests.extension import EXTENSION_MAPPINGS as NET
from server.domain.services.graph_executor import GraphExecutor

KNOWN = {**CORE["nodes"], **NET["nodes"], **AGENT["nodes"]}


class AcceptanceServer:
    def __init__(self):
        self.ENABLE_SMART_CACHE = True
        self.INSPECTION_DELAY = 0
        self.MAX_PARALLEL_NODES = 8
        self.client_id = "acc"
        self.current_workflow_id = "wf"
        self.sessions = {}
        self.rules = {}
        self.sent_messages = []
        self.nodes = KNOWN

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


def _run(prompt_dict):
    server = AcceptanceServer()
    executor = GraphExecutor(server)
    graph = executor.prompt_to_graph(prompt_dict)
    response = {"prompt_id": "p", "number": 1, "client_id": "acc", "workflow_id": "wf"}
    return asyncio.run(executor.run_parallel(graph, response)), server


def test_prompt_node_feeds_console_log():
    prompt = {
        "1": {
            "type": "PromptNode",
            "name": "prompt",
            "inputs": {"prompt": "hello {input}", "input": "harness"},
        },
        "2": {
            "type": "ConsoleLog",
            "name": "log",
            "inputs": {"any": {"originId": "1"}},
        },
    }
    results, server = _run(prompt)
    assert results["1"].values == "hello harness"
    assert results["2"].values == "hello harness"
    assert server.sent_messages
