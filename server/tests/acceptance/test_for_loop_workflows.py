import asyncio

from custom_extensions.core.extension import EXTENSION_MAPPINGS as CORE_MAPPINGS
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
        self.nodes = CORE_MAPPINGS["nodes"]

    async def send_json(self, event, data, sid=None):
        self.sent_messages.append({"event": event, "data": data, "sid": sid})


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


def build_for_loop_prompt():
    return {
        "1": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "index"},
        },
        "2": {
            "type": "ForLoop",
            "name": "ForLoop",
            "inputs": {
                "start": 0,
                "stop": 3,
                "step": 1,
                "index_key": {"originId": "1"},
                "node_inputs": "",
            },
        },
        "3": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "1"},
                "ignored_input": {"originId": "2"},
            },
        },
        "4": {
            "type": "MemoryRead",
            "name": "MemoryRead",
            "inputs": {"key": {"originId": "3"}},
        },
        "5": {
            "type": "EndForLoop",
            "name": "EndForLoop",
            "inputs": {
                "ForLoop": {"originId": "2"},
                "node_inputs": {"originId": "4"},
            },
        },
    }


def build_foreach_array_prompt():
    return {
        "1": {
            "type": "nsArray",
            "name": "nsArray",
            "inputs": {"initial_data": [2, 4, 6]},
        },
        "2": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "item"},
        },
        "3": {
            "type": "ForEachLoop",
            "name": "ForEachLoop",
            "inputs": {
                "collection": {"originId": "1"},
                "item_key": {"originId": "2"},
                "node_inputs": "",
            },
        },
        "4": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "2"},
                "ignored_input": {"originId": "3"},
            },
        },
        "5": {
            "type": "MemoryRead",
            "name": "MemoryRead",
            "inputs": {"key": {"originId": "4"}},
        },
        "6": {
            "type": "EndForEachLoop",
            "name": "EndForEachLoop",
            "inputs": {
                "ForEachLoop": {"originId": "3"},
                "node_inputs": {"originId": "5"},
            },
        },
    }


def build_foreach_hashmap_prompt():
    return {
        "1": {
            "type": "nsHashMap",
            "name": "nsHashMap",
            "inputs": {"initial_data": {"a": 10, "b": 20}},
        },
        "2": {
            "type": "ForEachLoop",
            "name": "ForEachLoop",
            "inputs": {
                "collection": {"originId": "1"},
                "item_key": "hashItem",
                "key_key": "hashKey",
                "index_key": "hashIndex",
                "node_inputs": "",
            },
        },
        "3": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "hashItem"},
        },
        "4": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "3"},
                "ignored_input": {"originId": "2"},
            },
        },
        "5": {
            "type": "MemoryRead",
            "name": "MemoryRead",
            "inputs": {"key": {"originId": "4"}},
        },
        "6": {
            "type": "EndForEachLoop",
            "name": "EndForEachLoop",
            "inputs": {
                "ForEachLoop": {"originId": "2"},
                "node_inputs": {"originId": "5"},
            },
        },
    }


def test_sequential_for_loop_iterates_numeric_range():
    graph_results, server = run_acceptance_prompt(build_for_loop_prompt(), "sequential")

    assert output_update_was_emitted(server, "4", 0)
    assert output_update_was_emitted(server, "4", 1)
    assert output_update_was_emitted(server, "4", 2)
    assert graph_results["5"].values["node_inputs"]["values"] == 2


def test_parallel_for_loop_iterates_numeric_range():
    graph_results, server = run_acceptance_prompt(build_for_loop_prompt(), "parallel")

    assert output_update_was_emitted(server, "4", 0)
    assert output_update_was_emitted(server, "4", 1)
    assert output_update_was_emitted(server, "4", 2)
    assert "5" in graph_results


def test_sequential_foreach_loop_iterates_array():
    graph_results, server = run_acceptance_prompt(
        build_foreach_array_prompt(), "sequential"
    )

    assert output_update_was_emitted(server, "5", 2)
    assert output_update_was_emitted(server, "5", 4)
    assert output_update_was_emitted(server, "5", 6)
    assert graph_results["6"].values["node_inputs"]["values"] == 6


def test_parallel_foreach_loop_iterates_array():
    graph_results, server = run_acceptance_prompt(build_foreach_array_prompt(), "parallel")

    assert output_update_was_emitted(server, "5", 2)
    assert output_update_was_emitted(server, "5", 4)
    assert output_update_was_emitted(server, "5", 6)
    assert "6" in graph_results


def test_sequential_foreach_loop_iterates_hashmap():
    graph_results, server = run_acceptance_prompt(
        build_foreach_hashmap_prompt(), "sequential"
    )

    assert output_update_was_emitted(server, "2", {
        "node_inputs": "",
        "key": "a",
        "item": 10,
        "index": 0,
    })
    assert output_update_was_emitted(server, "2", {
        "node_inputs": "",
        "key": "b",
        "item": 20,
        "index": 1,
    })
    assert graph_results["6"].values["node_inputs"]["values"] == 20


def test_parallel_foreach_loop_iterates_hashmap():
    graph_results, server = run_acceptance_prompt(
        build_foreach_hashmap_prompt(), "parallel"
    )

    assert output_update_was_emitted(server, "2", {
        "node_inputs": "",
        "key": "a",
        "item": 10,
        "index": 0,
    })
    assert output_update_was_emitted(server, "2", {
        "node_inputs": "",
        "key": "b",
        "item": 20,
        "index": 1,
    })
    assert "6" in graph_results
