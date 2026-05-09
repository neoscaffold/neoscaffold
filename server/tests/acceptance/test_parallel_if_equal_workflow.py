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


def build_if_equal_prompt():
    return {
        "1": {
            "type": "nsBoolean",
            "name": "nsBoolean",
            "inputs": {"value": False},
        },
        "2": {
            "type": "ConsoleLog",
            "name": "ConsoleLog",
            "inputs": {"any": {"originId": "1"}},
        },
        "4": {
            "type": "nsBoolean",
            "name": "nsBoolean",
            "inputs": {"value": "false"},
        },
        "14": {
            "type": "IfEqual",
            "name": "IfEqual",
            "inputs": {
                "a": {"originId": "2"},
                "b": {"originId": "4"},
            },
        },
        "9": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "happy"},
        },
        "11": {
            "type": "nsString",
            "name": "nsString",
            "inputs": {"text": "sad"},
        },
        "5": {
            "type": "IfEqualTrue",
            "name": "IfEqualTrue",
            "inputs": {
                "IfEqual": {"originId": "14"},
                "node_inputs": {"originId": "22"},
            },
        },
        "6": {
            "type": "IfEqualFalse",
            "name": "IfEqualFalse",
            "inputs": {"IfEqual": {"originId": "14"}},
        },
        "10": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "11"},
                "ignored_input": {"originId": "6"},
            },
        },
        "12": {
            "type": "ConsoleLog",
            "name": "ConsoleLog",
            "inputs": {"any": {"originId": "10"}},
        },
        "22": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": "",
                "ignored_input": {"originId": "12"},
            },
        },
        "8": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {
                "value": {"originId": "9"},
                "ignored_input": {"originId": "5"},
            },
        },
        "13": {
            "type": "ConsoleLog",
            "name": "ConsoleLog",
            "inputs": {"any": {"originId": "8"}},
        },
        "21": {
            "type": "PassThrough",
            "name": "PassThrough",
            "inputs": {"value": {"originId": "13"}},
        },
        "20": {
            "type": "EndIfEqual",
            "name": "EndIfEqual",
            "inputs": {
                "IfEqual": {"originId": "14"},
                "node_inputs": {"originId": "21"},
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


def assert_true_branch_execution(graph_results, server):

    assert graph_results["14"].values is True
    assert graph_results["9"].values == "happy"
    assert graph_results["8"].values == "happy"
    assert graph_results["13"].values == "happy"
    assert graph_results["21"].values == "happy"
    assert "20" in graph_results
    assert graph_results["20"].values["IfEqual"]["values"] is True

    assert "6" not in graph_results
    assert "10" not in graph_results
    assert "12" not in graph_results
    assert "22" not in graph_results

    assert server.sent_messages


def node_first_emission_index(server, node_id):
    for index, message in enumerate(server.sent_messages):
        if message["data"]["results"].get(node_id):
            return index
    return None


def test_parallel_if_equal_workflow_runs_true_branch_and_skips_false_branch():
    graph_results, server = run_acceptance_prompt(build_if_equal_prompt(), "parallel")

    assert_true_branch_execution(graph_results, server)
    assert "11" not in graph_results
    end_index = node_first_emission_index(server, "20")
    assert end_index is not None
    assert node_first_emission_index(server, "14") < node_first_emission_index(server, "9")
    assert node_first_emission_index(server, "21") < end_index


def test_sequential_if_equal_workflow_runs_true_branch_and_skips_false_branch():
    graph_results, server = run_acceptance_prompt(build_if_equal_prompt(), "sequential")

    assert_true_branch_execution(graph_results, server)
