import asyncio
import inspect
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

    async def run_parallel(
        self,
        graph: nx.DiGraph,
        response: Dict[str, Any],
        max_concurrency: int | None = None,
    ):
        if self.server is None:
            raise Exception("Server not set")

        graph_nodes = list(nx.topological_sort(graph))
        if not graph_nodes:
            return {}

        graph_results = {}  # type: ignore
        parameterized_rules = {}  # type: ignore
        evaluation_override_actions = {}  # type: ignore

        memory = {
            "graph_results": graph_results,
            "parameterized_rules": parameterized_rules,
            "evaluation_override_actions": evaluation_override_actions,
            "graph_nodes": graph_nodes,
            "graph": graph,
            "server": self.server,
            "client_id": response.get("client_id", self.server.client_id),
            "workflow_id": response.get("workflow_id", self.server.current_workflow_id),
            "parallel": True,
        }

        if self.server.ENABLE_SMART_CACHE:
            memory["graph_node_instances"] = {}

        max_parallel_nodes = (
            max_concurrency
            or getattr(self.server, "MAX_PARALLEL_NODES", None)
            or len(graph_nodes)
        )
        max_parallel_nodes = max(1, max_parallel_nodes)
        semaphore = asyncio.Semaphore(max_parallel_nodes)

        def get_if_equal_end_nodes(if_equal_node_id):
            return {
                node_id
                for node_id in graph.successors(if_equal_node_id)
                if graph.nodes[node_id].get("kind") == "EndIfEqual"
            }

        def get_if_equal_branch_support_nodes(branch_node_id):
            if_equal_node_ids = [
                node_id
                for node_id in graph.predecessors(branch_node_id)
                if graph.nodes[node_id].get("kind") == "IfEqual"
            ]
            if not if_equal_node_ids:
                return {branch_node_id}

            if_equal_node_id = if_equal_node_ids[0]
            end_node_ids = get_if_equal_end_nodes(if_equal_node_id)
            end_region_node_ids = set(end_node_ids)
            for end_node_id in end_node_ids:
                end_region_node_ids.update(nx.descendants(graph, end_node_id))

            condition_node_ids = {if_equal_node_id}
            condition_node_ids.update(nx.ancestors(graph, if_equal_node_id))
            branch_marker_input_node_ids = set(nx.ancestors(graph, branch_node_id))
            branch_marker_input_node_ids.difference_update(condition_node_ids)

            branch_node_ids = {branch_node_id}
            branch_node_ids.update(nx.descendants(graph, branch_node_id))
            branch_node_ids.difference_update(end_region_node_ids)

            support_node_ids = set(branch_node_ids)
            for node_id in branch_node_ids:
                if node_id == branch_node_id:
                    continue
                support_node_ids.update(nx.ancestors(graph, node_id))

            support_node_ids.difference_update(condition_node_ids)
            support_node_ids.difference_update(branch_marker_input_node_ids)
            support_node_ids.difference_update(end_region_node_ids)
            return support_node_ids

        if_equal_gated_nodes = set()
        for node_id in graph_nodes:
            if graph.nodes[node_id].get("kind") in {"IfEqualTrue", "IfEqualFalse"}:
                if_equal_gated_nodes.update(get_if_equal_branch_support_nodes(node_id))

        running_tasks = {}
        active_nodes = set(graph_nodes).difference(if_equal_gated_nodes)
        pending_dependencies = {}
        ready_queue = []

        def reset_pending_dependencies():
            for active_node_id in active_nodes:
                pending_dependencies[active_node_id] = sum(
                    1
                    for predecessor_id in graph.predecessors(active_node_id)
                    if predecessor_id in active_nodes
                )

        def enqueue_ready_nodes():
            ready_queue.clear()
            ready_queue.extend(
                node_id
                for node_id in graph_nodes
                if node_id in active_nodes and pending_dependencies[node_id] == 0
            )

        reset_pending_dependencies()
        enqueue_ready_nodes()

        async def cancel_running_tasks():
            for task in running_tasks:
                task.cancel()
            if running_tasks:
                await asyncio.gather(*running_tasks.keys(), return_exceptions=True)
            running_tasks.clear()

        def invalidate_parallel_goto(destination_node_id):
            nonlocal active_nodes
            affected_nodes = {destination_node_id}
            affected_nodes.update(nx.descendants(graph, destination_node_id))
            if graph.nodes[destination_node_id].get("kind") in {
                "IfEqualTrue",
                "IfEqualFalse",
            }:
                affected_nodes.update(
                    get_if_equal_branch_support_nodes(destination_node_id)
                )

            for affected_node_id in affected_nodes:
                graph_results.pop(affected_node_id, None)
                parameterized_rules.pop(affected_node_id, None)
                graph_node = graph.nodes[affected_node_id]
                graph_node.pop("node_instance", None)
                graph_node.pop("rule_instance", None)

            active_nodes = affected_nodes
            reset_pending_dependencies()
            enqueue_ready_nodes()

        def is_deferred_control_end_node(node_id):
            return graph.nodes[node_id].get("kind") in {"EndIfEqual", "EndWhileLoop"}

        def pop_next_ready_node():
            for index, node_id in enumerate(ready_queue):
                if not is_deferred_control_end_node(node_id):
                    return ready_queue.pop(index)

            if running_tasks:
                return None

            if ready_queue:
                return ready_queue.pop(0)

            return None

        def start_ready_tasks():
            while ready_queue and len(running_tasks) < max_parallel_nodes:
                node_id = pop_next_ready_node()
                if node_id is None:
                    break
                task = asyncio.create_task(
                    parallel_runtime_step(
                        node_id=node_id,
                        memory=memory,
                        response=response,
                        semaphore=semaphore,
                    )
                )
                running_tasks[task] = node_id

        while ready_queue or running_tasks:
            scheduler_action = await apply_parallel_scheduler_interventions(
                ready_queue=ready_queue,
                running_tasks=running_tasks,
                memory=memory,
            )
            if scheduler_action:
                await cancel_running_tasks()
                runtime_action = RuntimeAction(
                    scheduler_action.get("runtime_action", RuntimeAction.EVALUATE)
                )
                if runtime_action == RuntimeAction.RETURN:
                    return graph_results
                if runtime_action == RuntimeAction.GOTO:
                    destination_node_id = scheduler_action.get("destination_node_id")
                    if not destination_node_id:
                        return graph_results
                    invalidate_parallel_goto(destination_node_id)
                    continue

            start_ready_tasks()

            if not running_tasks:
                break

            completed_tasks, _ = await asyncio.wait(
                running_tasks.keys(), return_when=asyncio.FIRST_COMPLETED
            )

            for task in completed_tasks:
                node_id = running_tasks.pop(task)
                result = task.result()
                node_errors = result.get("node_errors", [])
                evaluation_action = result.get("evaluation_action")

                if node_errors:
                    await node_executed_client_update(
                        server=self.server,
                        graph_results=graph_results,
                        event=result.get("event", "message"),
                        node_errors=node_errors,
                        response=response,
                        evaluation_action=evaluation_action,
                    )
                    await cancel_running_tasks()
                    raise Exception(node_errors[0])

                result_kind = result.get("kind")
                if result_kind == "node":
                    graph_results[node_id] = result["node_output"]
                    await node_executed_client_update(
                        server=self.server,
                        graph_results=graph_results,
                        event="message",
                        node_errors=[],
                        response=response,
                        evaluation_action=evaluation_action,
                    )
                elif result_kind == "rule":
                    parameterized_rules[node_id] = result["rule"]

                runtime_action = RuntimeAction(
                    evaluation_action.get("runtime_action", RuntimeAction.EVALUATE)
                )
                if runtime_action == RuntimeAction.RETURN:
                    await cancel_running_tasks()
                    return graph_results
                if runtime_action == RuntimeAction.GOTO:
                    await cancel_running_tasks()
                    destination_node_id = evaluation_action.get("destination_node_id")
                    if not destination_node_id:
                        return graph_results
                    invalidate_parallel_goto(destination_node_id)
                    break

                for child_id in graph.successors(node_id):
                    if child_id not in active_nodes:
                        continue
                    pending_dependencies[child_id] -= 1
                    if pending_dependencies[child_id] == 0:
                        ready_queue.append(child_id)

        return graph_results

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
            "client_id": response.get("client_id", self.server.client_id),
            "workflow_id": response.get("workflow_id", self.server.current_workflow_id),
            "parallel": False,
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
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)

    node_id = action.get("node_id")

    # TODO: refactor this section to be less repetitive and more readable
    interventions = (
        server.sessions.get(client_id, {})
        .get(workflow_id, {})
        .get("interventions", {})
    )

    breakpoints = interventions.get("breakpoints")
    if breakpoints:
        # all_break is a flag that breaks the workflow at the current node
        all_break = breakpoints.get("all_break", False)

        in_list = node_id in breakpoints.get("nodes", {})
        if in_list or all_break:
            # notify the client that the execution has been paused at this node
            await server.send_json(
                event="message",
                data={"breakpoint": node_id},
                sid=client_id,
            )

            if all_break:
                # reset the all_break flag
                breakpoints["all_break"] = False
                if not in_list:
                    # create a new event
                    breakpoints["nodes"][node_id] = asyncio.Event()

            # check if the event has been set
            event = breakpoints["nodes"][node_id]
            event.clear()
            control_action = await wait_for_breakpoint_resume_or_control(
                event=event,
                node_id=node_id,
                memory=memory,
            )
            if control_action:
                action = control_action

    restart_points = interventions.get("restart-points")
    if restart_points:
        # all_restart is a flag that restarts the workflow to the first node
        all_restart = restart_points.get("all_restart", False)

        in_list = node_id in restart_points.get("nodes", {})
        if in_list or all_restart:
            # notify the client that the execution has been paused at this node
            await server.send_json(
                event="message",
                data={"restart-point": node_id},
                sid=client_id,
            )
            # restart the graph from the first node
            evaluation_override_actions[node_id] = EvaluationAction(
                node_id=node_id,
                runtime_action=RuntimeAction.GOTO,
                destination_node_id=graph_nodes[0],
            ).to_dict()

            # reset the all_restart flag
            restart_points["all_restart"] = False

    stop_points = interventions.get("stop-points")
    if stop_points:
        # handle stop points

        # all_stop is a flag that stops the workflow at the last node
        all_stop = stop_points.get("all_stop", False)

        in_list = node_id in stop_points.get("nodes", {})
        if in_list or all_stop:
            # notify the client that the execution has been stopped
            await server.send_json(
                event="message",
                data={"stop-point": node_id},
                sid=client_id,
            )
            # set the runtime action to return
            evaluation_override_actions[node_id] = EvaluationAction(
                node_id=node_id, runtime_action=RuntimeAction.RETURN
            ).to_dict()

            # reset the all_stop flag
            stop_points["all_stop"] = False

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
            graph_results[node.node_id] = await execute_node_async(
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


async def parallel_runtime_step(
    node_id: str,
    memory: Dict[str, Any],
    response: Dict[str, Any],
    semaphore: asyncio.Semaphore,
):
    graph = memory["graph"]
    graph_results = memory["graph_results"]
    parameterized_rules = memory["parameterized_rules"]
    evaluation_override_actions = memory["evaluation_override_actions"]
    server = memory["server"]

    action = EvaluationAction(
        node_id=node_id, runtime_action=RuntimeAction.EVALUATE
    ).to_dict()

    action = await apply_parallel_interventions(action, memory)
    runtime_action = RuntimeAction(action.get("runtime_action", RuntimeAction.EVALUATE))
    if runtime_action != RuntimeAction.EVALUATE:
        return {
            "kind": "control",
            "node_id": node_id,
            "evaluation_action": action,
            "node_errors": [],
        }

    if not isinstance(node_id, str):
        raise Exception("problem node_id type")

    graph_node = graph.nodes[node_id]
    node_class_name = graph_node["kind"]

    try:
        async with semaphore:
            if node_class_name in server.nodes:
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

                node = get_or_create_node(
                    node_id=node_id,
                    graph_node=graph_node,
                    memory=memory,
                )
                node_output = await execute_node_async(
                    node=node,
                    graph_node=graph_node,
                    graph_results=graph_results,
                    parameterized_rules=parameterized_rules,
                )
                override_action = evaluation_override_actions.pop(node_id, None)
                return {
                    "kind": "node",
                    "node_id": node_id,
                    "node_output": node_output,
                    "evaluation_action": override_action or action,
                    "node_errors": [],
                }

            if node_class_name in server.rules:
                rule = get_or_create_rule(
                    node_id=node_id,
                    graph_node=graph_node,
                    memory=memory,
                )
                parameterize_rule(
                    rule=rule,
                    graph_node=graph_node,
                    graph_results=graph_results,
                    parameterized_rules=parameterized_rules,
                )
                parameterized_rule = parameterized_rules.pop(node_id)
                return {
                    "kind": "rule",
                    "node_id": node_id,
                    "rule": parameterized_rule,
                    "evaluation_action": action,
                    "node_errors": [],
                }

            raise Exception(f"Node kind '{node_class_name}' not found in server nodes or rules")
    except Exception as e:
        return {
            "kind": "error",
            "node_id": node_id,
            "evaluation_action": action,
            "node_errors": [make_stack_trace_dict(e)],
            "event": "error" if node_class_name not in server.nodes else "message",
        }


async def apply_parallel_interventions(
    action: EvaluationAction, memory: Dict[str, Any]
):
    server = memory["server"]
    node_id = action.get("node_id")
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)

    interventions = (
        server.sessions.get(client_id, {})
        .get(workflow_id, {})
        .get("interventions", {})
    )

    breakpoints = interventions.get("breakpoints")
    if breakpoints:
        all_break = breakpoints.get("all_break", False)
        in_list = node_id in breakpoints.get("nodes", {})
        if in_list or all_break:
            await server.send_json(
                event="message",
                data={"breakpoint": node_id},
                sid=client_id,
            )

            if all_break:
                breakpoints["all_break"] = False
                if not in_list:
                    breakpoints["nodes"][node_id] = asyncio.Event()

            event = breakpoints["nodes"][node_id]
            event.clear()
            control_action = await wait_for_breakpoint_resume_or_control(
                event=event,
                node_id=node_id,
                memory=memory,
            )
            if control_action:
                return control_action

    restart_points = interventions.get("restart-points")
    if restart_points:
        all_restart = restart_points.get("all_restart", False)
        in_list = node_id in restart_points.get("nodes", {})
        if in_list or all_restart:
            await server.send_json(
                event="message",
                data={"restart-point": node_id},
                sid=client_id,
            )
            restart_points["all_restart"] = False
            return EvaluationAction(
                node_id=node_id,
                runtime_action=RuntimeAction.GOTO,
                destination_node_id=memory["graph_nodes"][0],
            ).to_dict()

    stop_points = interventions.get("stop-points")
    if stop_points:
        all_stop = stop_points.get("all_stop", False)
        in_list = node_id in stop_points.get("nodes", {})
        if in_list or all_stop:
            await server.send_json(
                event="message",
                data={"stop-point": node_id},
                sid=client_id,
            )
            stop_points["all_stop"] = False
            return EvaluationAction(
                node_id=node_id, runtime_action=RuntimeAction.RETURN
            ).to_dict()

    return action


async def apply_parallel_scheduler_interventions(
    ready_queue: List[str],
    running_tasks: Dict[asyncio.Task, str],
    memory: Dict[str, Any],
):
    server = memory["server"]
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)
    interventions = get_workflow_interventions(
        server=server,
        client_id=client_id,
        workflow_id=workflow_id,
    )

    node_id = (
        ready_queue[0]
        if ready_queue
        else next(iter(running_tasks.values()), None)
    )
    stop_action = await apply_stop_intervention(node_id=node_id, memory=memory)
    if stop_action:
        return stop_action

    restart_action = await apply_restart_intervention(node_id=node_id, memory=memory)
    if restart_action:
        return restart_action

    breakpoints = interventions.get("breakpoints")
    if breakpoints and breakpoints.get("all_break", False) and ready_queue:
        node_id = ready_queue[0]
        await server.send_json(
            event="message",
            data={"breakpoint": node_id},
            sid=client_id,
        )

        breakpoints["all_break"] = False
        if node_id not in breakpoints.get("nodes", {}):
            breakpoints.setdefault("nodes", {})[node_id] = asyncio.Event()

        event = breakpoints["nodes"][node_id]
        event.clear()
        control_action = await wait_for_breakpoint_resume_or_control(
            event=event,
            node_id=node_id,
            memory=memory,
        )
        if control_action:
            return control_action

    return None


def get_workflow_interventions(server, client_id, workflow_id):
    return (
        server.sessions.get(client_id, {})
        .get(workflow_id, {})
        .get("interventions", {})
    )


async def wait_for_breakpoint_resume_or_control(event, node_id, memory):
    while not event.is_set():
        stop_action = await apply_stop_intervention(node_id=node_id, memory=memory)
        if stop_action:
            return stop_action

        restart_action = await apply_restart_intervention(
            node_id=node_id,
            memory=memory,
        )
        if restart_action:
            clear_breakpoint_intervention(node_id=node_id, memory=memory)
            return restart_action

        try:
            await asyncio.wait_for(event.wait(), timeout=0.1)
        except asyncio.TimeoutError:
            pass

    return None


def clear_breakpoint_intervention(node_id, memory):
    server = memory["server"]
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)
    interventions = get_workflow_interventions(
        server=server,
        client_id=client_id,
        workflow_id=workflow_id,
    )
    breakpoints = interventions.get("breakpoints")
    if not breakpoints:
        return

    event = breakpoints.get("nodes", {}).pop(node_id, None)
    if event:
        event.set()


async def apply_stop_intervention(node_id, memory):
    server = memory["server"]
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)
    interventions = get_workflow_interventions(
        server=server,
        client_id=client_id,
        workflow_id=workflow_id,
    )
    stop_points = interventions.get("stop-points")
    if not stop_points:
        return None

    all_stop = stop_points.get("all_stop", False)
    in_list = node_id in stop_points.get("nodes", {})
    if not (all_stop or in_list):
        return None

    await server.send_json(
        event="message",
        data={"stop-point": node_id},
        sid=client_id,
    )
    stop_points["all_stop"] = False
    return EvaluationAction(
        node_id=node_id, runtime_action=RuntimeAction.RETURN
    ).to_dict()


async def apply_restart_intervention(node_id, memory):
    server = memory["server"]
    client_id = memory.get("client_id", server.client_id)
    workflow_id = memory.get("workflow_id", server.current_workflow_id)
    interventions = get_workflow_interventions(
        server=server,
        client_id=client_id,
        workflow_id=workflow_id,
    )
    restart_points = interventions.get("restart-points")
    if not restart_points:
        return None

    all_restart = restart_points.get("all_restart", False)
    in_list = node_id in restart_points.get("nodes", {})
    if not (all_restart or in_list):
        return None

    await server.send_json(
        event="message",
        data={"restart-point": node_id},
        sid=client_id,
    )
    restart_points["all_restart"] = False
    return EvaluationAction(
        node_id=node_id,
        runtime_action=RuntimeAction.GOTO,
        destination_node_id=memory["graph_nodes"][0],
    ).to_dict()


def get_or_create_node(node_id, graph_node, memory):
    server = memory["server"]
    node = None

    if server.ENABLE_SMART_CACHE:
        node = graph_node.get("node_instance")

    if not node:
        node_class_name = graph_node["kind"]
        node_class = server.nodes[node_class_name].get("python_class")
        node_instance = node_class()
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

    return node


def get_or_create_rule(node_id, graph_node, memory):
    server = memory["server"]
    rule = None

    if server.ENABLE_SMART_CACHE:
        rule = graph_node.get("rule_instance")

    if not rule:
        node_class_name = graph_node["kind"]
        rule_class = server.rules[node_class_name].get("python_class")
        rule_instance = rule_class()
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

    return rule


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


async def execute_node_async(node, graph_node, graph_results, parameterized_rules):
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

    if inspect.iscoroutinefunction(node.class_instance.evaluate):
        return await node._evaluate_async(node_input_group)

    node_output = await asyncio.to_thread(node._evaluate, node_input_group)
    if inspect.isawaitable(node_output.values):
        node_output.values = await node_output.values
        node._finish_evaluation(node_input_group, node_output)
    return node_output


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
        sid=response.get("client_id", server.client_id),
    )
