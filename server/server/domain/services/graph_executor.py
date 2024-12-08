import asyncio
from typing import Any, Dict, List
import networkx as nx

from ...domain.utilities.make_stack_trace_dict import make_stack_trace_dict

from ...domain.enums.runtime_action import RuntimeAction

from ..models.evaluation_action import EvaluationAction
from ..quality.models.rule import Rule
from ..models.node import Node

# TODO: Server needs to track a list of nodes, their version, their source plugins, and the versions of the source plugins, nodes are not only dependent on the types of their inputs but they may also be dependent on the version of the source plugin that they are using, make these loose relationships requiring only "prototypical" relationships because any node that meets the signature is "technically" compatible (make it as easy to connect new nodes to old as possible, forwards and backwards compatibility is a must)
# Cache busting should take place even when an upstream event takes place that would change the output of a node, this is because the node may have been updated to be compatible with the new upstream event, and the user may want to take advantage of that


class GraphExecutor:
    def __init__(self, server=None):
        self.server = server

    def prompt_to_graph(self, prompt):
        if self.server is None:
            raise Exception("Server not set")

        graph = nx.DiGraph()

        edges_to_add = []

        # add just the nodes to our graph
        for node_id, node in prompt.items():
            widget_values = {}
            # get all inputs sourced from widgets
            if "inputs" in node and isinstance(node["inputs"], dict):
                # check if inputs is a dict
                for input_name, input_value in node["inputs"].items():
                    # check if input_value is a dict
                    if isinstance(input_value, dict):
                        # if it's NOT a link-based input it's a widget-based input
                        if "originId" not in input_value:
                            widget_values[input_name] = input_value
                        else:
                            # if it is a link-based input, add it to the list of edges to add
                            edges_to_add.append((input_value["originId"], node_id))
                            # originId is used to find the edges in the graph (from which we get the input value)
                            widget_values[input_name] = {
                                "originId": input_value["originId"]
                            }
                    else:
                        # if it's not even a dict it must be a widget-based input
                        widget_values[input_name] = input_value

            widget_values["kind"] = node["type"]
            widget_values["nickname"] = node["name"]

            # add the node with the attributes we have for it
            graph.add_node(node_id, **widget_values)

        # add the edges to the graph
        graph.add_edges_from(edges_to_add)

        return graph

    # def run_parallel(self, graph):
    # TODO: implement parallel execution with this algorithm
    # Most efficient way to execute the graph
    # whenever a node executes
    # check which nodes have yet to be resolved
    # start executing all nodes that have all their dependencies met at that time
    # pass

    async def run_sequential(self, graph: nx.DiGraph, response: Dict[str, Any]):
        if self.server is None:
            raise Exception("Server not set")

        # get the topological sort of the graph
        graph_nodes = list(nx.topological_sort(graph))
        # print("graph_nodes", graph_nodes)

        graph_results = {}  # type: ignore
        parameterized_rules = {}  # type: ignore
        evaluation_override_actions = {}  # type: ignore

        # SEMAPHORE variables
        # TODO: DO THIS BEFORE RUN_PARALLEL these should be handled carefully since they will need to be thread safe
        memory = {
            "graph_results": graph_results,
            "parameterized_rules": parameterized_rules,
            "evaluation_override_actions": evaluation_override_actions,
            "graph_nodes": graph_nodes,
            "graph": graph,
            "server": self.server,
        }

        if self.server.ENABLE_SMART_CACHE:
            memory["graph_node_instances"] = {}

        current_action = EvaluationAction(
            node_id=graph_nodes[0], runtime_action=RuntimeAction.EVALUATE
        ).to_dict()

        # run each node in the graph
        while current_action:
            current_action = await sequential_runtime_step(
                current_action, memory, response
            )

        return graph_results


async def sequential_runtime_step(
    action: EvaluationAction, memory: Dict[str, Any], response: Dict[str, Any]
):
    graph = memory["graph"]
    graph_results = memory["graph_results"]
    graph_nodes: List[str] = memory["graph_nodes"]

    evaluation_override_actions = memory["evaluation_override_actions"]

    parameterized_rules = memory["parameterized_rules"]
    server = memory["server"]

    node_id = action.get("node_id")

    breakpoints = (
        server.sessions.get(server.client_id, {})
        .get(server.current_workflow_id, {})
        .get("breakpoints", {})
    )
    if breakpoints.get("last_modified"):
        in_list = node_id in breakpoints.get("nodes", {})
        if in_list:
            # notify the client that the execution has been paused at this node
            await server.send_json(
                event="message",
                data={"breakpoint": node_id},
                sid=server.client_id,
            )
            # check if the event has been set
            event = breakpoints["nodes"][node_id]
            await event.wait()
            # clean up the event
            event.clear()

    # override the action if there is an override for it planned
    if node_id in evaluation_override_actions:
        action = evaluation_override_actions[node_id]
        del evaluation_override_actions[node_id]

    # if the action has an action OTHER than evaluate to perform, perform it
    match RuntimeAction(action.get("runtime_action", 0)):
        case RuntimeAction.RETURN:
            return
        case RuntimeAction.BYPASS:
            next_node_id_topological = graph_nodes[graph_nodes.index(node_id) + 1]
            next_action = EvaluationAction(
                node_id=next_node_id_topological, runtime_action=RuntimeAction.EVALUATE
            ).to_dict()
            return next_action
        case RuntimeAction.GOTO:
            if action.get("destination_node_id"):
                next_node_id_from_goto = action.get("destination_node_id")
                next_action = EvaluationAction(
                    node_id=next_node_id_from_goto,
                    runtime_action=RuntimeAction.EVALUATE,
                ).to_dict()
                return next_action

    index_of_node_id = graph_nodes.index(node_id)

    # if there is no next node, return None to end the loop
    next_action_topological = None

    # if there is a next node, return the next action
    if index_of_node_id < len(graph_nodes) - 1:
        # print(
        #     f"current node {node_id}, next node {graph_nodes[index_of_node_id + 1]} \n\n\n"
        # )
        next_node_id_topological = graph_nodes[index_of_node_id + 1]
        next_action_topological = EvaluationAction(
            node_id=next_node_id_topological, runtime_action=RuntimeAction.EVALUATE
        ).to_dict()

    memory["_next_action"] = next_action_topological

    if not isinstance(node_id, str):
        raise Exception("problem node_id type")

    # get the node from the graph
    graph_node = graph.nodes[node_id]

    # get the node class
    node_class_name = graph_node["kind"]

    # TODO: introduce a way to prevent issues when node is named the same as a rule
    if node_class_name in server.nodes:
        # notify the client that the node is evaluating
        await node_executed_client_update(
            server=server,
            graph_results=None,
            event="message",
            node_errors=[],
            response=response,
            evaluation_action=action,
        )
        if server.INSPECTION_DELAY and server.INSPECTION_DELAY > 0:
            await asyncio.sleep(server.INSPECTION_DELAY)

        node = None

        if server.ENABLE_SMART_CACHE:
            node = graph_node.get("node_instance")

        if not node:
            node_class = server.nodes[node_class_name].get("python_class")

            node_instance = node_class()

            # semaphore variables
            node_instance._memory = memory

            node = Node(
                node_id=node_id,
                name=graph_node["nickname"],
                class_instance=node_instance,
            )
            cls_ins = node.class_instance
            cls_ins._node = node

            if server.ENABLE_SMART_CACHE:
                graph_node["node_instance"] = node

        node_errors = []

        try:
            execute_node(
                node=node,
                graph_node=graph_node,
                graph_results=graph_results,
                parameterized_rules=parameterized_rules,
            )
        except Exception as e:
            # create a dict that displays the stack trace
            stack_trace = make_stack_trace_dict(e)
            node_errors.append(stack_trace)

        await node_executed_client_update(
            server=server,
            graph_results=graph_results,
            event="message",
            node_errors=node_errors,
            response=response,
            evaluation_action=action,
        )

        # TODO: consider adding a way to permit the user to continue execution despite the error
        if len(node_errors) > 0:
            raise Exception(node_errors[0])

    elif node_class_name in server.rules:
        rule = None

        if server.ENABLE_SMART_CACHE:
            rule = graph_node.get("rule_instance")

        if not rule:
            rule_class = server.rules[node_class_name].get("python_class")
            rule_instance = rule_class()

            # semaphore variables
            rule_instance._memory = memory

            rule = Rule(
                name=graph_node["nickname"],
                class_instance=rule_instance,
            )
            rule.rule_id = node_id
            cls_ins = rule.class_instance
            cls_ins._rule = rule

            if server.ENABLE_SMART_CACHE:
                graph_node["rule_instance"] = rule

        # we continue because inputs to rules don't have to the "resolved" until the actual rule group is executed together (i.e in a node instance)
        parameterize_rule(
            rule=rule,
            graph_node=graph_node,
            graph_results=graph_results,
            parameterized_rules=parameterized_rules,
        )

    else:
        node_missing_exception = Exception(
            f"Node kind '{node_class_name}' not found in server nodes or rules"
        )
        await node_executed_client_update(
            server=server,
            graph_results=graph_results,
            event="error",
            node_errors=[node_missing_exception],
            response=response,
            evaluation_action=action,
        )
        raise node_missing_exception

    # if this is the last node but it now has an evaluation_override_action that it self-assigned, return that action, because this is a program that ends with a control-flow node
    if (
        node_id in evaluation_override_actions
        and index_of_node_id < len(graph_nodes) - 1
    ):
        memory["_next_action"] = evaluation_override_actions[node_id]

    return memory["_next_action"]


def execute_node(node, graph_node, graph_results, parameterized_rules):
    node_input_group = node.input_template()

    resolve_input_group_inputs(
        node=node,
        input_group_inputs=node_input_group.get("required_inputs"),
        graph_node=graph_node,
        graph_results=graph_results,
        parameterized_rules=parameterized_rules,
    )

    resolve_input_group_inputs(
        node=node,
        input_group_inputs=node_input_group.get("optional_inputs"),
        graph_node=graph_node,
        graph_results=graph_results,
        parameterized_rules=parameterized_rules,
    )

    graph_results[node.node_id] = node._evaluate(node_input_group)


def resolve_input_group_inputs(
    node, input_group_inputs, graph_node, graph_results, parameterized_rules
):
    if input_group_inputs is not None:
        for node_input in input_group_inputs.values():
            if node_input.name in graph_node:
                if node_input.kind == "rule_group":
                    if (
                        isinstance(graph_node[node_input.name], dict)
                        and "originId" in graph_node[node_input.name]
                    ):
                        # sets the value to the previous parameterized rule for destructuring recursively later
                        rule_chained = parameterized_rules[
                            graph_node[node_input.name]["originId"]
                        ]
                        print(f"rule_chained {rule_chained}")
                        unrolled_rule_chain = unroll_rule_chain(rule_chained)

                        if node_input.name == "in_rules":
                            node.set_input_rules(*unrolled_rule_chain)
                        elif node_input.name == "out_rules":
                            node.set_output_rules(*unrolled_rule_chain)
                        else:
                            node_input.values = unrolled_rule_chain

                    # NOTICE: there is no else block here because you can't set a rule_group to a value
                else:
                    if (
                        isinstance(graph_node[node_input.name], dict)
                        and "originId" in graph_node[node_input.name]
                    ):
                        # get the edge data
                        node_input.values = graph_results.get(
                            graph_node[node_input.name]["originId"], None
                        )
                        node_input.node_id = graph_node[node_input.name]["originId"]
                    else:
                        node_input.values = graph_node[node_input.name]
            # else:
            #     print(f"Class {node.name} does not have input {node_input.name}")
            #     print(graph_node, node_input.name)


def unroll_rule_chain(rule_chained):
    rule_list = []
    while rule_chained.parameters.optional_parameters.get("rule_group") is not None:
        rule_list.append(rule_chained)
        rule_group = rule_chained.parameters.optional_parameters.get("rule_group")

        if rule_group and rule_group.values is not None:
            rule_chained = rule_group.values
        else:
            break

    return rule_list


def parameterize_rule(rule, graph_node, graph_results, parameterized_rules):
    # goal is to parameterize the rule so it could be passed into the in_rules or out_rules of a node

    parameter_group = rule.parameter_template()

    resolve_rule_parameters(
        rule=rule,
        parameter_group_inputs=parameter_group.get("required_parameters"),
        graph_node=graph_node,
        graph_results=graph_results,
        parameterized_rules=parameterized_rules,
    )

    resolve_rule_parameters(
        rule=rule,
        parameter_group_inputs=parameter_group.get("optional_parameters"),
        graph_node=graph_node,
        graph_results=graph_results,
        parameterized_rules=parameterized_rules,
    )

    rule.parameters = parameter_group

    parameterized_rules[rule.rule_id] = rule


def resolve_rule_parameters(
    rule,
    parameter_group_inputs,
    graph_node,
    graph_results,
    parameterized_rules,
):
    if parameter_group_inputs is not None:
        for parameter in parameter_group_inputs.values():
            if parameter.name in graph_node:
                if parameter.kind == "rule_group":
                    if (
                        isinstance(graph_node[parameter.name], dict)
                        and "originId" in graph_node[parameter.name]
                    ):
                        # sets the value to the previous parameterized rule for destructuring recursively later
                        parameter.values = parameterized_rules[
                            graph_node[parameter.name]["originId"]
                        ]
                    # NOTICE: there is no else block here because the first rule_group shouldn't have a value
                else:
                    if (
                        isinstance(graph_node[parameter.name], dict)
                        and "originId" in graph_node[parameter.name]
                    ):
                        # get the edge data
                        parameter.values = graph_results[
                            graph_node[parameter.name]["originId"]
                        ]
                    else:
                        parameter.values = graph_node[parameter.name]
            # else:
            #     print(f"Class {rule.name} does not have input {parameter.name}")
            #     print(graph_node, parameter.name)


async def node_executed_client_update(
    server, graph_results, event, node_errors, response, evaluation_action
):
    # send the results to the client

    response_value = {}
    if graph_results:
        for node_id, node_output in graph_results.items():
            response_value[node_id] = {
                "kind": node_output.kind,
                "name": node_output.name,
                "node_id": node_output.node_id,
                "values": node_output.values,
                "cacheable": node_output.cacheable,
            }
            if node_output.input_evaluation:
                outcome_dict = {}
                for outcome in node_output.input_evaluation.outcomes:
                    outcome_dict[outcome.uid] = {
                        "passed": outcome.passed,
                        "causes": {
                            k: {"message": v.message, "outliers": v.outliers}
                            for k, v in outcome.causes.items()
                        },
                    }

                response_value[node_id]["input_evaluation"] = {
                    "passed": node_output.input_evaluation.passed,
                    "outcomes": outcome_dict,
                }

            if node_output.output_evaluation:
                outcome_dict = {}
                for outcome in node_output.output_evaluation.outcomes:
                    outcome_dict[outcome.uid] = {
                        "passed": outcome.passed,
                        "causes": {
                            k: {"message": v.message, "outliers": v.outliers}
                            for k, v in outcome.causes.items()
                        },
                    }

                response_value[node_id]["output_evaluation"] = {
                    "passed": node_output.output_evaluation.passed,
                    "outcomes": outcome_dict,
                }

    response_object = {
        "prompt_id": response["prompt_id"],
        "number": response["number"],
        "node_errors": node_errors,
        "results": response_value,
        "evaluation_action": evaluation_action if evaluation_action else None,
    }

    await server.send_json(
        event=event,
        data=response_object,
        # get sid from clientid while processing the queue and send the data to the client
        sid=server.client_id,
    )
