import asyncio

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE_MAPPINGS
from custom_extensions.network_requests.extension import (
    EXTENSION_MAPPINGS as NETWORK_MAPPINGS,
)
from server.domain.services.graph_executor import GraphExecutor


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
        self.nodes = {
            **CORE_MAPPINGS["nodes"],
            **NETWORK_MAPPINGS["nodes"],
        }

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


def build_while_loop_prompt():
    return {
        "5": {
            "type": "nsInteger",
            "name": "nsInteger",
            "inputs": {"value": -5},
        },
        "6": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "conditionKey"},
        },
        "4": {
            "type": "MemoryWrite",
            "name": "MemoryWrite",
            "inputs": {
                "key": {"originId": "6"},
                "value": {"originId": "5"},
            },
        },
        "13": {
            "type": "ValuePath",
            "name": "ValuePath",
            "inputs": {
                "object": {"originId": "4"},
                "value_path": "key",
            },
        },
        "1": {
            "type": "WhileLoop",
            "name": "WhileLoop",
            "inputs": {
                "condition_key": {"originId": "13"},
                "node_inputs": "",
            },
        },
        "12": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "6"},
                "ignored_input": {"originId": "1"},
            },
        },
        "9": {
            "type": "MemoryRead",
            "name": "MemoryRead",
            "inputs": {"key": {"originId": "12"}},
        },
        "10": {
            "type": "nsInteger",
            "name": "nsInteger",
            "inputs": {"value": 1},
        },
        "8": {
            "type": "Add",
            "name": "Add",
            "inputs": {
                "a": {"originId": "9"},
                "b": {"originId": "10"},
            },
        },
        "7": {
            "type": "MemoryWrite",
            "name": "MemoryWrite",
            "inputs": {
                "key": {"originId": "6"},
                "value": {"originId": "8"},
            },
        },
        "11": {
            "type": "ConsoleLog",
            "name": "ConsoleLog",
            "inputs": {"any": {"originId": "7"}},
        },
        "3": {
            "type": "EndWhileLoop",
            "name": "EndWhileLoop",
            "inputs": {
                "WhileLoop": {"originId": "1"},
                "node_inputs": {"originId": "11"},
            },
        },
    }


def run_acceptance_prompt(prompt, runtime):
    server = AcceptanceServer()
    executor = GraphExecutor(server)
    graph = executor.prompt_to_graph(prompt)
    response = {
        "prompt_id": "acceptance-prompt",
        "number": 1,
        "client_id": server.client_id,
        "workflow_id": server.current_workflow_id,
    }
    if runtime == "parallel":
        return asyncio.run(executor.run_parallel(graph, response)), server
    if runtime == "sequential":
        return asyncio.run(executor.run_sequential(graph, response)), server
    raise ValueError(f"Unsupported runtime: {runtime}")


def output_update_was_emitted(server, node_id, values):
    return any(
        message["data"]["results"].get(node_id, {}).get("values") == values
        for message in server.sent_messages
        if "data" in message and "results" in message["data"]
    )


def node_first_emission_index(server, node_id):
    for index, message in enumerate(server.sent_messages):
        if message["data"]["results"].get(node_id):
            return index
    return None


def assert_while_loop_execution(graph_results, server, runtime):
    assert server.sent_messages
    assert output_update_was_emitted(server, "7", {"key": "conditionKey", "value": 0})
    assert output_update_was_emitted(server, "8", 0)
    assert output_update_was_emitted(server, "9", -1)
    assert output_update_was_emitted(server, "11", {"key": "conditionKey", "value": 0})
    assert "3" in graph_results
    assert graph_results["3"].values["WhileLoop"]["values"] == {"node_inputs": ""}

    if runtime == "sequential":
        assert graph_results["7"].values == {"key": "conditionKey", "value": 0}
        assert graph_results["8"].values == 0
        assert graph_results["9"].values == -1
        assert graph_results["11"].values == {"key": "conditionKey", "value": 0}
    else:
        assert graph_results["1"].values == {"node_inputs": ""}
        end_index = node_first_emission_index(server, "3")
        assert end_index is not None
        assert node_first_emission_index(server, "11") < end_index


def test_parallel_while_loop_workflow_increments_until_condition_is_false():
    graph_results, server = run_acceptance_prompt(build_while_loop_prompt(), "parallel")

    assert_while_loop_execution(graph_results, server, "parallel")


def test_sequential_while_loop_workflow_increments_until_condition_is_false():
    graph_results, server = run_acceptance_prompt(build_while_loop_prompt(), "sequential")

    assert_while_loop_execution(graph_results, server, "sequential")
