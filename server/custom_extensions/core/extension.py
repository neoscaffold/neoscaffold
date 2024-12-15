import json


def get_nested(data, *args):
    # print("get_nested", data, args)
    try:
        if args and data:
            element = args[0]
            if element:
                # handle the case where the value is a list
                if isinstance(data, list) and element.isdigit():
                    # if arg is a number, return the value at that index
                    value = data[int(element)]
                else:
                    value = data.get(element)

                return value if len(args) == 1 else get_nested(value, *args[1:])
    except Exception as e:
        print(e)
    return None


def resolve_value_path(path: str):
    """Resolve a property path to a list of strings."""
    # temporarily replace instances of "\." with a placeholder
    if not path:
        return []

    replaced = path.replace("\\.", "§")
    property_path_list = replaced.split(".")
    # replace the placeholder with "."
    property_path_list = [x.replace("§", ".") for x in property_path_list]
    return property_path_list


version = "0.0.1"


class nsString:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates a string primitive, which is a sequence of characters. Strings are immutable and can be used to represent text or other sequences of Unicode characters."

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "*",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "text" in node_inputs.get("required_inputs"):
                self.text = node_inputs.get("required_inputs").get("text").get("values")

        return self.text


class nsBoolean:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates a boolean primitive, which represents a logical value of either True or False."

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "value": {
                "kind": "boolean",
                "name": "value",
                "widget": {"kind": "string", "name": "value", "default": "false"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "value" in node_inputs.get("required_inputs"):
                value = node_inputs.get("required_inputs").get("value").get("values")
                if isinstance(value, str):
                    if value == "" or value.lower() == "false":
                        self.value = False
                    else:
                        self.value = True
                else:
                    self.value = bool(value)

        return bool(self.value)


class nsInteger:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates an integer primitive, which represents a whole number."

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "value": {
                "kind": "number",
                "name": "value",
                "widget": {"kind": "number", "name": "value", "default": 0},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "value" in node_inputs.get("required_inputs"):
                self.value = (
                    node_inputs.get("required_inputs").get("value").get("values")
                )

        return int(self.value)


class nsFloat:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates a float primitive, which represents a decimal number."

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "value": {
                "kind": "number",
                "name": "value",
                "widget": {"kind": "number", "name": "value", "default": 0.0},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "value" in node_inputs.get("required_inputs"):
                self.value = (
                    node_inputs.get("required_inputs").get("value").get("values")
                )

        return float(self.value)


class nsNull:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates a null primitive, which represents the absence of a value."

    # INPUT TYPES
    INPUT = {}  # type: ignore

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        del node_inputs
        return None


class nsHashMap:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates a HashMap primitive, which represents a key-value store."

    # INPUT TYPES
    INPUT = {
        "optional_inputs": {
            "initial_data": {
                "kind": "object",
                "name": "initial_data",
                "widget": {"kind": "object", "name": "initial_data", "default": {}},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "object",
        "name": "hashmap",
        "cacheable": True,
    }

    def __init__(self):
        self.data = {}

    def evaluate(self, node_inputs):
        if node_inputs.get("optional_inputs"):
            if "initial_data" in node_inputs.get("optional_inputs"):
                self.data = (
                    node_inputs.get("optional_inputs")
                    .get("initial_data")
                    .get("values", {})
                )

        return self.data


class nsArray:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Creates an Array primitive, which represents an ordered collection of elements."

    # INPUT TYPES
    INPUT = {
        "optional_inputs": {
            "initial_data": {
                "kind": "array",
                "name": "initial_data",
                "widget": {"kind": "string", "name": "initial_data", "default": "[]"},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "array",
        "cacheable": True,
    }

    def __init__(self):
        self.data = []

    def evaluate(self, node_inputs):
        if node_inputs.get("optional_inputs"):
            if "initial_data" in node_inputs.get("optional_inputs"):
                self.data = (
                    node_inputs.get("optional_inputs")
                    .get("initial_data")
                    .get("values", [])
                )
                # if self.data is a string parse it into an list
                if isinstance(self.data, str):
                    try:
                        self.data = json.loads(self.data)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, split the string into a list
                        self.data = self.data.split(",")

        return self.data

class nsArrayAppend:
    CATEGORY = "core"
    SUBCATEGORY = "primitives"
    DESCRIPTION = "Appends an element to an array"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "array": {
                "kind": "array",
                "name": "array",
            },
            "element": {
                "kind": "*",
                "name": "element",
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "array",
        "name": "array",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "array" in node_inputs.get("required_inputs"):
                self.array = node_inputs.get("required_inputs").get("array").get("values")
            if "element" in node_inputs.get("required_inputs"):
                self.element = node_inputs.get("required_inputs").get("element").get("values")

        self.array.append(self.element)

        return self.array


class IfEqual:
    CATEGORY = "utilities"
    SUBCATEGORY = "control_flow"
    DESCRIPTION = "Compares two values for equality and executes different branches based on the result"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "*",
                "name": "a",
            },
            "b": {
                "kind": "*",
                "name": "b",
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "a" in node_inputs.get("required_inputs"):
                self.a = node_inputs.get("required_inputs").get("a").get("values")
            if "b" in node_inputs.get("required_inputs"):
                self.b = node_inputs.get("required_inputs").get("b").get("values")

        boolean_result = self.a == self.b

        destination_node_name = "IfEqualTrue" if boolean_result else "IfEqualFalse"

        # load the networkx DiGraph graph
        graph = self._memory.get("graph")
        evaluation_override_actions = self._memory.get("evaluation_override_actions")

        current_node_id = self._node.node_id

        # get all nodes that are connected to the current node
        connected_node_ids = list(graph.successors(current_node_id))

        # validate that IfEqualTrue is connected to the current node once only
        equal_true_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "IfEqualTrue"
        ]
        if len(equal_true_node_ids) != 1:
            raise Exception("Only one IfEqualTrue should be connected to a IfEqual")

        # validate that IfEqualFalse is connected to the current node once only
        equal_false_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "IfEqualFalse"
        ]
        if len(equal_false_node_ids) != 1:
            raise Exception("Only one IfEqualFalse should be connected to a IfEqual")

        # validate that EndIfEqual is connected to the current node once only
        equal_end_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "EndIfEqual"
        ]
        if len(equal_end_node_ids) != 1:
            raise Exception("Only one EndIfEqual should be connected to a IfEqual")

        # get the destination node id
        if destination_node_name == "IfEqualTrue":
            node_id_of_destination = equal_true_node_ids[0]

            # make the IfEqualFalse a GOTO to EndIfEqual
            next_action_topological = {
                "node_id": equal_false_node_ids[0],
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": equal_end_node_ids[0],
            }
            evaluation_override_actions[equal_false_node_ids[0]] = (
                next_action_topological
            )
        else:
            node_id_of_destination = equal_false_node_ids[0]

            # make the IfEqualTrue a GOTO to EndIfEqual
            next_action_topological = {
                "node_id": equal_true_node_ids[0],
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": equal_end_node_ids[0],
            }
            evaluation_override_actions[equal_true_node_ids[0]] = (
                next_action_topological
            )

        # make the next action
        print("\n\n\n NEXT ACTION \n\n\n")
        print(
            f'\n\n\n {graph.nodes[self._memory["_next_action"]["node_id"]]["kind"]} \n\n\n'
        )
        self._memory["_next_action"] = {
            "node_id": node_id_of_destination,
            "runtime_action": 0,  # RuntimeAction.EVALUATE
        }
        # make the next action
        print("\n\n\n NEXT ACTION \n\n\n")
        print(
            f'\n\n\n {graph.nodes[self._memory["_next_action"]["node_id"]]["kind"]} \n\n\n'
        )

        return boolean_result


class IfEqualTrue:
    CATEGORY = "utilities"
    SUBCATEGORY = "control_flow"
    DESCRIPTION = "Compares two values for equality and executes different branches based on the result"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "IfEqual": {
                "kind": "*",
                "name": "IfEqual",
            }
        },
        "optional_inputs": {
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            }
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        return


class IfEqualFalse:
    CATEGORY = "utilities"
    SUBCATEGORY = "control_flow"
    DESCRIPTION = "Compares two values for equality and executes different branches based on the result"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "IfEqual": {
                "kind": "*",
                "name": "IfEqual",
            }
        },
        "optional_inputs": {
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            }
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        return


class EndIfEqual:
    CATEGORY = "utilities"
    SUBCATEGORY = "control_flow"
    DESCRIPTION = "Compares two values for equality and executes different branches based on the result"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "IfEqual": {
                "kind": "*",
                "name": "IfEqual",
            }
        },
        "optional_inputs": {
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            }
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        return


class WhileLoop:
    CATEGORY = "utilities"
    SUBCATEGORY = "iteration"
    DESCRIPTION = "Repeats nodes"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "condition_key": {
                "kind": "string",
                "name": "condition_key",
                "widget": {"kind": "string", "name": "condition_key", "default": ""},
            },
        },
        "optional_inputs": {
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
                "widget": {"kind": "string", "name": "node_inputs", "default": ""},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "control_flow",
        "name": "loop",
        "cacheable": False,
    }

    def evaluate(self, node_inputs):
        current_node_id = self._node.node_id

        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "condition_key" in node_inputs.get("required_inputs"):
                self.condition_key = (
                    node_inputs.get("required_inputs")
                    .get("condition_key")
                    .get("values")
                )

            if "node_inputs" in node_inputs.get("optional_inputs"):
                self.node_inputs = (
                    node_inputs.get("optional_inputs").get("node_inputs").get("values")
                )

        # load the networkx DiGraph graph
        graph = self._memory.get("graph")
        graph_nodes = self._memory.get("graph_nodes")
        evaluation_override_actions = self._memory.get("evaluation_override_actions")

        # get all nodes that are connected to the current node
        connected_node_ids = list(graph.successors(current_node_id))

        # validate that EndWhileLoop is connected to the current node once only
        end_while_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "EndWhileLoop"
        ]
        if len(end_while_node_ids) != 1:
            raise Exception("Only one EndWhileLoop should be connected to a WhileLoop")

        # get the while_node_id
        node_id_of_end_while_node = end_while_node_ids[0]

        # make a list of the connected ids omitting endwhileloop
        connected_ids_without_end = [
            node_id
            for node_id in connected_node_ids
            if node_id != node_id_of_end_while_node
        ]
        if len(connected_ids_without_end) < 1:
            raise Exception(
                "At least one node should be connected to a WhileLoop other than EndWhileLoop"
            )

        index_of_node_id = graph_nodes.index(current_node_id)
        next_node_id_topological = graph_nodes[index_of_node_id + 1]

        # if the next topological node happens to be the EndWhileLoop
        if next_node_id_topological == node_id_of_end_while_node:
            raise Exception("EndWhileLoop should placed at end of the while loop.")

        if not self._memory.get(self.condition_key):
            # EvaluationAction but a dict
            next_action_topological = {
                "node_id": next_node_id_topological,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": node_id_of_end_while_node,
            }

            evaluation_override_actions[current_node_id] = next_action_topological
        else:
            # make the EndWhileLoop into a GOTO back to the WhileLoop
            next_action_topological = {
                "node_id": node_id_of_end_while_node,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": current_node_id,
            }
            evaluation_override_actions[node_id_of_end_while_node] = (
                next_action_topological
            )

        return {"node_inputs": self.node_inputs}


class BreakWhileLoop:
    CATEGORY = "utilities"
    SUBCATEGORY = "iteration"
    DESCRIPTION = "Breaks out of WhileLoops"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "WhileLoop": {"kind": "control_flow", "name": "WhileLoop"},
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        current_node_id = self._node.node_id
        self.node_inputs = None
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "WhileLoop" in node_inputs.get("required_inputs"):
                self.WhileLoop = (
                    node_inputs.get("required_inputs").get("WhileLoop").get("values")
                )

            if "node_inputs" in node_inputs.get("optional_inputs"):
                self.node_inputs = (
                    node_inputs.get("optional_inputs").get("node_inputs").get("values")
                )

        # load the networkx DiGraph graph
        graph = self._memory.get("graph")
        graph_nodes = self._memory.get("graph_nodes")
        evaluation_override_actions = self._memory.get("evaluation_override_actions")

        # get all nodes that are connected to the current node
        connected_node_ids = list(graph.predecessors(current_node_id))

        # validate that WhileLoop is connected to the current node once only
        while_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "WhileLoop"
        ]
        if len(while_node_ids) != 1:
            raise Exception(
                "There should be only one WhileLoop connected to a BreakWhileLoop"
            )

        # get the while_node_id
        node_id_of_while_node = while_node_ids[0]

        # get all nodes that are connected to the current node
        connected_node_ids = list(graph.successors(node_id_of_while_node))

        # validate that EndWhileLoop is connected to the current node once only
        end_while_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "EndWhileLoop"
        ]
        if len(end_while_node_ids) != 1:
            raise Exception("Only one EndWhileLoop should be connected to a WhileLoop")

        # get the while_node_id
        node_id_of_end_while_node = end_while_node_ids[0]

        # common case: break the loop and nodes exist after this current node

        index_of_node_id = graph_nodes.index(current_node_id)
        if index_of_node_id < len(graph_nodes) - 1:
            next_node_id_topological = graph_nodes[index_of_node_id + 1]
            # EvaluationAction but a dict
            next_action_topological = {
                "node_id": next_node_id_topological,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": node_id_of_end_while_node,
            }

            # the next node should goto the end of the while loop
            evaluation_override_actions[next_node_id_topological] = (
                next_action_topological
            )

        # uncommon case the break happens at the end of the graph
        else:
            next_action_topological = {
                "node_id": current_node_id,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": node_id_of_end_while_node,
            }
            evaluation_override_actions[current_node_id] = next_action_topological

        return self.node_inputs


class ContinueWhileLoop:
    CATEGORY = "utilities"
    SUBCATEGORY = "iteration"
    DESCRIPTION = "Continues out of WhileLoops"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "WhileLoop": {"kind": "control_flow", "name": "WhileLoop"},
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        current_node_id = self._node.node_id
        self.node_inputs = None
        # load the node_inputs
        if node_inputs.get("required_inputs"):
            if "WhileLoop" in node_inputs.get("required_inputs"):
                self.WhileLoop = (
                    node_inputs.get("required_inputs").get("WhileLoop").get("values")
                )

            if "node_inputs" in node_inputs.get("optional_inputs"):
                self.node_inputs = (
                    node_inputs.get("optional_inputs").get("node_inputs").get("values")
                )

        # load the networkx DiGraph graph
        graph = self._memory.get("graph")
        graph_nodes = self._memory.get("graph_nodes")
        evaluation_override_actions = self._memory.get("evaluation_override_actions")

        # get all nodes that are connected to the current node
        connected_node_ids = list(graph.predecessors(current_node_id))

        # validate that EndWhileLoop is connected to the current node once only
        while_node_ids = [
            node_id
            for node_id in connected_node_ids
            if graph.nodes[node_id]["kind"] == "WhileLoop"
        ]
        if len(while_node_ids) != 1:
            raise Exception(
                "There should be only one WhileLoop connected to a ContinueWhileLoop"
            )

        # get the while_node_id
        node_id_of_while_node = while_node_ids[0]

        # common case: continue the loop and nodes exist after this current node

        index_of_node_id = graph_nodes.index(current_node_id)
        if index_of_node_id < len(graph_nodes) - 1:
            next_node_id_topological = graph_nodes[index_of_node_id + 1]
            # EvaluationAction but a dict
            next_action_topological = {
                "node_id": next_node_id_topological,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": node_id_of_while_node,
            }

            evaluation_override_actions[node_id_of_while_node] = next_action_topological
        # uncommon case the continue happens at the end of the graph
        else:
            next_action_topological = {
                "node_id": current_node_id,
                "runtime_action": 3,  # RuntimeAction.GOTO
                "destination_node_id": node_id_of_while_node,
            }
            evaluation_override_actions[current_node_id] = next_action_topological

        return self.node_inputs


class EndWhileLoop:
    CATEGORY = "utilities"
    SUBCATEGORY = "iteration"
    DESCRIPTION = "Ends WhileLoops"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "WhileLoop": {"kind": "control_flow", "name": "WhileLoop"},
            "node_inputs": {
                "kind": "*",
                "name": "node_inputs",
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        self.node_inputs = None

        if node_inputs.get("required_inputs"):
            if "WhileLoop" in node_inputs.get("required_inputs"):
                self.WhileLoop = node_inputs.get("required_inputs").get("WhileLoop")
            if "node_inputs" in node_inputs.get("required_inputs"):
                self.node_inputs = node_inputs.get("required_inputs").get("node_inputs")

        return {"node_inputs": self.node_inputs, "WhileLoop": self.WhileLoop}


class ValuePath:
    CATEGORY = "utilities"
    SUBCATEGORY = "access"
    DESCRIPTION = "basic property select"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "object": {
                "kind": "*",
                "name": "object",
                "widget": {"kind": "string", "name": "object", "default": ""},
            },
            "value_path": {
                "kind": "*",
                "name": "value_path",
                "widget": {"kind": "string", "name": "value_path", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "object" in node_inputs.get("required_inputs"):
                self.object = (
                    node_inputs.get("required_inputs").get("object").get("values")
                )

            if "value_path" in node_inputs.get("required_inputs"):
                self.value_path = (
                    node_inputs.get("required_inputs").get("value_path").get("values")
                )

        if "." in self.value_path:
            value_path_list = resolve_value_path(self.value_path)
            return get_nested(self.object, *value_path_list)

        return self.object.get(self.value_path)


class MemoryWrite:
    CATEGORY = "utilities"
    SUBCATEGORY = "memory"
    DESCRIPTION = "write to memory"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "key": {
                "kind": "*",
                "name": "key",
                "widget": {"kind": "string", "name": "key", "default": ""},
            },
            "value": {
                "kind": "*",
                "name": "value",
                "widget": {"kind": "string", "name": "value", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        self.key = None
        self.value = None
        if node_inputs.get("required_inputs"):
            if "key" in node_inputs.get("required_inputs"):
                self.key = node_inputs.get("required_inputs").get("key").get("values")

                if "value" in node_inputs.get("required_inputs"):
                    self.value = (
                        node_inputs.get("required_inputs").get("value").get("values")
                    )

                    # store the value
                    self._memory[self.key] = self.value

        return {
            "key": self.key,
            "value": self.value,
        }


class MemoryRead:
    CATEGORY = "utilities"
    SUBCATEGORY = "memory"
    DESCRIPTION = "read from memory"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "key": {
                "kind": "*",
                "name": "key",
                "widget": {"kind": "string", "name": "key", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        if node_inputs.get("required_inputs"):
            if "key" in node_inputs.get("required_inputs"):
                self.key = node_inputs.get("required_inputs").get("key").get("values")
        if not self.key:
            return

        return self._memory.get(self.key)


class PassThrough:
    CATEGORY = "utilities"
    SUBCATEGORY = "links"
    DESCRIPTION = "pass through value or ignore"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "value": {
                "kind": "*",
                "name": "value",
                "widget": {"kind": "string", "name": "value", "default": ""},
            },
        },
        "optional_inputs": {
            "ignored_input": {
                "kind": "*",
                "name": "ignored_input",
                "widget": {"kind": "string", "name": "ignored_input", "default": ""},
            },
        },
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        self.value = None
        if node_inputs.get("required_inputs"):
            if "value" in node_inputs.get("required_inputs"):
                self.value = (
                    node_inputs.get("required_inputs").get("value").get("values")
                )

        return self.value


class JSONParse:
    CATEGORY = "utilities"
    SUBCATEGORY = "parsing"
    DESCRIPTION = "parse json"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "json": {
                "kind": "*",
                "name": "json",
                "widget": {"kind": "string", "name": "json", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        output_value = ""
        if node_inputs.get("required_inputs"):
            if "json" in node_inputs.get("required_inputs"):
                self.json = node_inputs.get("required_inputs").get("json").get("values")

        if self.json:
            output_value = json.loads(self.json)

        return output_value


class ConcatString:
    CATEGORY = "utilities"
    SUBCATEGORY = "parsing"
    DESCRIPTION = "concatenate string"

    # INPUT TYPES
    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "*",
                "name": "a",
                "widget": {"kind": "string", "name": "a", "default": ""},
            },
            "b": {
                "kind": "*",
                "name": "b",
                "widget": {"kind": "string", "name": "b", "default": ""},
            },
        }
    }

    # OUTPUT TYPES
    OUTPUT = {
        "kind": "*",
        "name": "*",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        output_value = ""
        if node_inputs.get("required_inputs"):
            if "a" in node_inputs.get("required_inputs"):
                self.a = node_inputs.get("required_inputs").get("a").get("values")

                if "b" in node_inputs.get("required_inputs"):
                    self.b = node_inputs.get("required_inputs").get("b").get("values")

                    output_value = str(self.a) + str(self.b)

        return output_value


class Add:
    CATEGORY = "utilities"
    SUBCATEGORY = "math"
    DESCRIPTION = "Add two numbers"

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        }
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)

        try:
            result = a + b
        except TypeError:
            raise TypeError("Invalid input: both inputs must be numbers")

        return result


class Subtract:
    CATEGORY = "utilities"
    SUBCATEGORY = "math"
    DESCRIPTION = "Subtract two numbers"

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        }
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)

        try:
            result = a - b
        except ValueError:
            raise ValueError("Invalid input: both inputs must be numbers")

        return result


class Multiply:
    CATEGORY = "utilities"
    SUBCATEGORY = "math"
    DESCRIPTION = "Multiply two numbers"

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 1},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1},
            },
        }
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 1)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1)

        try:
            result = a * b
        except TypeError:
            raise TypeError("Invalid input: both inputs must be numbers")

        return result


class Divide:
    CATEGORY = "utilities"
    SUBCATEGORY = "math"
    DESCRIPTION = "Divide one number by another"

    INPUT = {
        "required_inputs": {
            "numerator": {
                "kind": "number",
                "name": "numerator",
                "widget": {"kind": "number", "name": "numerator", "default": 1},
            },
            "denominator": {
                "kind": "number",
                "name": "denominator",
                "widget": {"kind": "number", "name": "denominator", "default": 1},
            },
        }
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numerator = (
            node_inputs.get("required_inputs", {}).get("numerator", {}).get("values", 1)
        )
        denominator = (
            node_inputs.get("required_inputs", {})
            .get("denominator", {})
            .get("values", 1)
        )

        try:
            if denominator == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result = numerator / denominator
        except TypeError:
            raise TypeError("Invalid input: both inputs must be numbers")

        return result


class Exponent:
    CATEGORY = "utilities"
    SUBCATEGORY = "math"
    DESCRIPTION = "Raise a number to the power of another"

    INPUT = {
        "required_inputs": {
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 1},
            },
            "exponent": {
                "kind": "number",
                "name": "exponent",
                "widget": {"kind": "number", "name": "exponent", "default": 1},
            },
        }
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        base = node_inputs.get("required_inputs", {}).get("base", {}).get("values", 1)
        exponent = (
            node_inputs.get("required_inputs", {}).get("exponent", {}).get("values", 1)
        )

        try:
            result = base**exponent
        except ValueError:
            raise ValueError("Invalid input: both inputs must be numbers")
        except OverflowError:
            raise OverflowError("Result is too large to represent")

        return result


class StringContains:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if a string contains a specified substring"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "substring": {
                "kind": "string",
                "name": "substring",
                "widget": {"kind": "string", "name": "substring", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        substring = (
            node_inputs.get("required_inputs", {})
            .get("substring", {})
            .get("values", "")
        )

        result = substring in string
        return result


class StringStartsWith:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if a string starts with a specified prefix"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "prefix": {
                "kind": "string",
                "name": "prefix",
                "widget": {"kind": "string", "name": "prefix", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        prefix = (
            node_inputs.get("required_inputs", {}).get("prefix", {}).get("values", "")
        )

        result = string.startswith(prefix)
        return result


class StringEndsWith:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if a string ends with a specified suffix"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "suffix": {
                "kind": "string",
                "name": "suffix",
                "widget": {"kind": "string", "name": "suffix", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        suffix = (
            node_inputs.get("required_inputs", {}).get("suffix", {}).get("values", "")
        )

        result = string.endswith(suffix)
        return result


class StringSplit:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Splits a string into an array of substrings based on a specified delimiter"
    )

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "delimiter": {
                "kind": "string",
                "name": "delimiter",
                "widget": {"kind": "string", "name": "delimiter", "default": " "},
            },
        }
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        delimiter = (
            node_inputs.get("required_inputs", {})
            .get("delimiter", {})
            .get("values", " ")
        )

        result = string.split(delimiter)
        return result


class StringJoin:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Joins an array of strings into a single string using a specified delimiter"
    )

    INPUT = {
        "required_inputs": {
            "array": {
                "kind": "array",
                "name": "array",
                "widget": {"kind": "array", "name": "array", "default": []},
            },
            "delimiter": {
                "kind": "string",
                "name": "delimiter",
                "widget": {"kind": "string", "name": "delimiter", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        array = (
            node_inputs.get("required_inputs", {}).get("array", {}).get("values", [])
        )
        delimiter = (
            node_inputs.get("required_inputs", {})
            .get("delimiter", {})
            .get("values", "")
        )

        result = delimiter.join(array)
        return result


class StringReplace:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Replaces occurrences of a substring in a string with another substring"
    )

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "old": {
                "kind": "string",
                "name": "old",
                "widget": {"kind": "string", "name": "old", "default": ""},
            },
            "new": {
                "kind": "string",
                "name": "new",
                "widget": {"kind": "string", "name": "new", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        old = node_inputs.get("required_inputs", {}).get("old", {}).get("values", "")
        new = node_inputs.get("required_inputs", {}).get("new", {}).get("values", "")

        result = string.replace(old, new)
        return result


class StringToUpper:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to uppercase"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.upper()
        return result


class StringToLower:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to lowercase"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.lower()
        return result


class StringCapitalize:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Capitalizes the first character of a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.capitalize()
        return result


class StringTitleCase:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to title case"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.title()
        return result


class StringStrip:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes leading and trailing whitespace from a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.strip()
        return result


class StringLStrip:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes leading whitespace from a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.lstrip()
        return result


class StringRStrip:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes trailing whitespace from a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        }
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.rstrip()
        return result


class StringFind:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Finds the first occurrence of a substring in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "substring": {
                "kind": "string",
                "name": "substring",
                "widget": {"kind": "string", "name": "substring", "default": ""},
            },
        },
        "optional_inputs": {
            "start": {
                "kind": "number",
                "name": "start",
                "widget": {"kind": "number", "name": "start", "default": 0},
            },
            "end": {
                "kind": "number",
                "name": "end",
                "widget": {"kind": "number", "name": "end", "default": None},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        substring = (
            node_inputs.get("required_inputs", {})
            .get("substring", {})
            .get("values", "")
        )
        start = node_inputs.get("optional_inputs", {}).get("start", {}).get("values", 0)
        end = node_inputs.get("optional_inputs", {}).get("end", {}).get("values", None)

        result = string.find(substring, start, end)
        return result


class StringRFind:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Finds the last occurrence of a substring in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "substring": {
                "kind": "string",
                "name": "substring",
                "widget": {"kind": "string", "name": "substring", "default": ""},
            },
        },
        "optional_inputs": {
            "start": {
                "kind": "number",
                "name": "start",
                "widget": {"kind": "number", "name": "start", "default": 0},
            },
            "end": {
                "kind": "number",
                "name": "end",
                "widget": {"kind": "number", "name": "end", "default": None},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        substring = (
            node_inputs.get("required_inputs", {})
            .get("substring", {})
            .get("values", "")
        )
        start = node_inputs.get("optional_inputs", {}).get("start", {}).get("values", 0)
        end = node_inputs.get("optional_inputs", {}).get("end", {}).get("values", None)

        result = string.rfind(substring, start, end)
        return result


class StringCount:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Counts occurrences of a substring in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "substring": {
                "kind": "string",
                "name": "substring",
                "widget": {"kind": "string", "name": "substring", "default": ""},
            },
        },
        "optional_inputs": {
            "start": {
                "kind": "number",
                "name": "start",
                "widget": {"kind": "number", "name": "start", "default": 0},
            },
            "end": {
                "kind": "number",
                "name": "end",
                "widget": {"kind": "number", "name": "end", "default": None},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        substring = (
            node_inputs.get("required_inputs", {})
            .get("substring", {})
            .get("values", "")
        )
        start = node_inputs.get("optional_inputs", {}).get("start", {}).get("values", 0)
        end = node_inputs.get("optional_inputs", {}).get("end", {}).get("values", None)

        result = string.count(substring, start, end)
        return result


class StringIsDigit:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are digits"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isdigit()
        return result


class StringIsAlpha:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are alphabetic"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isalpha()
        return result


class StringIsAlnum:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are alphanumeric"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isalnum()
        return result


class StringIsSpace:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are whitespace"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isspace()
        return result


class StringIsNumeric:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are numeric"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isnumeric()
        return result


class StringIsDecimal:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if all characters in the string are decimal"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        result = string.isdecimal()
        return result


class StringEncode:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Encodes the input string using the specified encoding"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "encoding": {
                "kind": "string",
                "name": "encoding",
                "widget": {"kind": "string", "name": "encoding", "default": "utf-8"},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "encoded_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        encoding = (
            node_inputs.get("required_inputs", {})
            .get("encoding", {})
            .get("values", "utf-8")
        )
        try:
            result = string.encode(encoding)
            return result
        except Exception as e:
            return str(e)  # Return error message if encoding fails


class StringDecode:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes the input string using the specified encoding"

    INPUT = {
        "required_inputs": {
            "encoded_string": {
                "kind": "string",
                "name": "encoded_string",
                "widget": {"kind": "string", "name": "encoded_string", "default": ""},
            },
            "encoding": {
                "kind": "string",
                "name": "encoding",
                "widget": {"kind": "string", "name": "encoding", "default": "utf-8"},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "decoded_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        encoded_string = (
            node_inputs.get("required_inputs", {})
            .get("encoded_string", {})
            .get("values", "")
        )
        encoding = (
            node_inputs.get("required_inputs", {})
            .get("encoding", {})
            .get("values", "utf-8")
        )
        try:
            result = encoded_string.decode(encoding)
            return result
        except Exception as e:
            return str(e)  # Return error message if decoding fails


class StringZFill:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Pads the string with zeros on the left side to reach the specified width"
    )

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "width": {
                "kind": "number",
                "name": "width",
                "widget": {"kind": "number", "name": "width", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "padded_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        width = node_inputs.get("required_inputs", {}).get("width", {}).get("values", 0)

        try:
            result = string.zfill(width)
            return result
        except Exception as e:
            return str(e)  # Return error message if zfill fails


class StringCenter:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Centers the string within a field of a specified width"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "width": {
                "kind": "number",
                "name": "width",
                "widget": {"kind": "number", "name": "width", "default": 0},
            },
        },
        "optional_inputs": {
            "fillchar": {
                "kind": "string",
                "name": "fillchar",
                "widget": {"kind": "string", "name": "fillchar", "default": " "},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "centered_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        width = node_inputs.get("required_inputs", {}).get("width", {}).get("values", 0)
        fillchar = (
            node_inputs.get("optional_inputs", {})
            .get("fillchar", {})
            .get("values", " ")
        )

        try:
            result = string.center(width, fillchar)
            return result
        except Exception as e:
            return str(e)  # Return error message if centering fails


class StringLJustify:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Left-justifies the string within a field of a specified width"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "width": {
                "kind": "number",
                "name": "width",
                "widget": {"kind": "number", "name": "width", "default": 0},
            },
        },
        "optional_inputs": {
            "fillchar": {
                "kind": "string",
                "name": "fillchar",
                "widget": {"kind": "string", "name": "fillchar", "default": " "},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "left_justified_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        width = node_inputs.get("required_inputs", {}).get("width", {}).get("values", 0)
        fillchar = (
            node_inputs.get("optional_inputs", {})
            .get("fillchar", {})
            .get("values", " ")
        )

        try:
            result = string.ljust(width, fillchar)
            return result
        except Exception as e:
            return str(e)  # Return error message if left-justification fails


class StringRJustify:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Right-justifies the string within a field of a specified width"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "width": {
                "kind": "number",
                "name": "width",
                "widget": {"kind": "number", "name": "width", "default": 0},
            },
        },
        "optional_inputs": {
            "fillchar": {
                "kind": "string",
                "name": "fillchar",
                "widget": {"kind": "string", "name": "fillchar", "default": " "},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "right_justified_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        width = node_inputs.get("required_inputs", {}).get("width", {}).get("values", 0)
        fillchar = (
            node_inputs.get("optional_inputs", {})
            .get("fillchar", {})
            .get("values", " ")
        )

        try:
            result = string.rjust(width, fillchar)
            return result
        except Exception as e:
            return str(e)  # Return error message if right-justification fails


class StringExpandtabs:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Expands tabs in a string to spaces"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "tabsize": {
                "kind": "number",
                "name": "tabsize",
                "widget": {"kind": "number", "name": "tabsize", "default": 8},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "expanded_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        tabsize = (
            node_inputs.get("required_inputs", {}).get("tabsize", {}).get("values", 8)
        )

        try:
            expanded = string.expandtabs(tabsize)
            return expanded
        except Exception as e:
            return str(e)  # Return error message if expandtabs fails


class StringSwapcase:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Swaps the case of all characters in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "swapped_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            swapped = string.swapcase()
            return swapped
        except Exception as e:
            return str(e)  # Return error message if swapcase fails


class StringCasefold:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "In Python, the `casefold()` method is used to achieve this. It is similar to `lower()`, but it is more comprehensive and is intended for caseless matching. This is especially useful for comparing strings in a way that is insensitive to case differences, including those that arise from different alphabets or scripts."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "casefolded_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            casefolded = string.casefold()
            return casefolded
        except Exception as e:
            return str(e)  # Return error message if casefold fails


class StringStartswithAny:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if a string starts with any of the given prefixes"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "prefixes": {
                "kind": "array",
                "name": "prefixes",
                "widget": {"kind": "array", "name": "prefixes", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "starts_with_any",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        prefixes = (
            node_inputs.get("required_inputs", {}).get("prefixes", {}).get("values", [])
        )

        try:
            return any(string.startswith(prefix) for prefix in prefixes)
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringEndswithAny:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if a string ends with any of the given suffixes"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "suffixes": {
                "kind": "array",
                "name": "suffixes",
                "widget": {"kind": "array", "name": "suffixes", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "ends_with_any",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        suffixes = (
            node_inputs.get("required_inputs", {}).get("suffixes", {}).get("values", [])
        )

        try:
            return any(string.endswith(suffix) for suffix in suffixes)
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringReplaceAll:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Replaces all occurrences of a substring in a string with another substring"
    )

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "old": {
                "kind": "string",
                "name": "old",
                "widget": {"kind": "string", "name": "old", "default": ""},
            },
            "new": {
                "kind": "string",
                "name": "new",
                "widget": {"kind": "string", "name": "new", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "replaced_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        old = node_inputs.get("required_inputs", {}).get("old", {}).get("values", "")
        new = node_inputs.get("required_inputs", {}).get("new", {}).get("values", "")

        try:
            return string.replace(old, new)
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexMatch:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Matches a string against a regular expression pattern"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "match_result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            return bool(re.match(pattern, string, flags))
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexSearch:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Searches a string for a match to a regular expression pattern"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "search_result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            match = re.search(pattern, string, flags)
            return match.group() if match else ""
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexSub:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Substitutes occurrences of a pattern in a string with a replacement"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "repl": {
                "kind": "string",
                "name": "replacement",
                "widget": {"kind": "string", "name": "replacement", "default": ""},
            },
        },
        "optional_inputs": {
            "count": {
                "kind": "number",
                "name": "count",
                "widget": {"kind": "number", "name": "count", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        repl = node_inputs.get("required_inputs", {}).get("repl", {}).get("values", "")
        count = node_inputs.get("optional_inputs", {}).get("count", {}).get("values", 0)
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            result = re.sub(pattern, repl, string, count=count, flags=flags)
            return result
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexFindAll:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Finds all non-overlapping matches of a pattern in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "matches",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            matches = re.findall(pattern, string, flags=flags)
            return matches
        except Exception as e:
            return [
                str(e)
            ]  # Return error message as a single-item list if operation fails


class StringRegexSplit:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Splits a string by the occurrences of a pattern"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "maxsplit": {
                "kind": "number",
                "name": "maxsplit",
                "widget": {"kind": "number", "name": "maxsplit", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "split_result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        maxsplit = (
            node_inputs.get("optional_inputs", {}).get("maxsplit", {}).get("values", 0)
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            result = re.split(pattern, string, maxsplit=maxsplit, flags=flags)
            return result
        except Exception as e:
            return [
                str(e)
            ]  # Return error message as a single-item list if operation fails


class StringRegexCompile:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Compiles a regular expression pattern into a regex object"

    INPUT = {
        "required_inputs": {
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "regex_object",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            regex_object = re.compile(pattern, flags=flags)
            return regex_object
        except Exception as e:
            return str(e)  # Return error message if compilation fails


class StringRegexGroup:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Retrieves a specific group from a regex match"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "group": {
                "kind": "number",
                "name": "group",
                "widget": {"kind": "number", "name": "group", "default": 0},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "group_match",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        group = node_inputs.get("required_inputs", {}).get("group", {}).get("values", 0)
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            match = re.search(pattern, string, flags=flags)
            if match:
                return match.group(group)
            else:
                return ""
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexGroups:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Returns all groups from a regex match in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "groups",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            match = re.search(pattern, string, flags=flags)
            if match:
                return list(match.groups())
            else:
                return []
        except Exception as e:
            return [
                str(e)
            ]  # Return error message as a single-item list if operation fails


class StringRegexNamedGroups:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Returns all named groups from a regex match in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "named_groups",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            match = re.search(pattern, string, flags=flags)
            if match:
                return match.groupdict()
            else:
                return {}
        except Exception as e:
            return {
                "error": str(e)
            }  # Return error message as a dictionary if operation fails


class StringRegexFindIter:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Returns an iterator yielding match objects for all non-overlapping matches of a pattern in a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "matches",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            matches = list(re.finditer(pattern, string, flags=flags))
            return [
                match.groupdict() if match.groupdict() else match.group()
                for match in matches
            ]
        except Exception as e:
            return [
                {"error": str(e)}
            ]  # Return error message as a single-item list if operation fails


class StringRegexFullMatch:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Attempts to apply the pattern to all of the string, returning a match object if the whole string matches, or None if it doesn't"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "match",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            match = re.fullmatch(pattern, string, flags=flags)
            if match:
                return (
                    match.groupdict() if match.groupdict() else {"match": match.group()}
                )
            else:
                return None
        except Exception as e:
            return {
                "error": str(e)
            }  # Return error message as a dictionary if operation fails


class StringRegexEscape:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Escapes special characters in a string to be used as a literal string in a regex pattern"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "escaped_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            escaped_string = re.escape(string)
            return escaped_string
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexUnescape:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Unescapes special characters in a string that were previously escaped for regex patterns"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "unescaped_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            # Custom unescape function since Python doesn't have a built-in regex unescape
            def unescape(s):
                return re.sub(r"\\(.)", r"\1", s)

            unescaped_string = unescape(string)
            return unescaped_string
        except Exception as e:
            return str(e)  # Return error message if operation fails


class StringRegexSubstitutionNumber:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Substitutes occurrences of a pattern in a string with a replacement and returns the new string and the number of substitutions made"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "repl": {
                "kind": "string",
                "name": "replacement",
                "widget": {"kind": "string", "name": "replacement", "default": ""},
            },
        },
        "optional_inputs": {
            "count": {
                "kind": "number",
                "name": "count",
                "widget": {"kind": "number", "name": "count", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        repl = node_inputs.get("required_inputs", {}).get("repl", {}).get("values", "")
        count = node_inputs.get("optional_inputs", {}).get("count", {}).get("values", 0)
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            new_string, n = re.subn(pattern, repl, string, count=count, flags=flags)
            return [new_string, n]
        except Exception as e:
            return [
                str(e),
                0,
            ]  # Return error message and 0 substitutions if operation fails


class StringRegexSubWithFunction:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Substitutes occurrences of a pattern in a string using a function for replacement"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "repl_function": {
                "kind": "function",
                "name": "replacement_function",
                "widget": {"kind": "function", "name": "replacement_function"},
            },
        },
        "optional_inputs": {
            "count": {
                "kind": "number",
                "name": "count",
                "widget": {"kind": "number", "name": "count", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        repl_function = (
            node_inputs.get("required_inputs", {})
            .get("repl_function", {})
            .get("values")
        )
        count = node_inputs.get("optional_inputs", {}).get("count", {}).get("values", 0)
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            new_string, n = re.subn(
                pattern, repl_function, string, count=count, flags=flags
            )
            return [new_string, n]
        except Exception as e:
            return [
                str(e),
                0,
            ]  # Return error message and 0 substitutions if operation fails


class StringRegexSplitWithFunction:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Splits a string by the occurrences of a pattern and applies a function to each split part"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "function": {
                "kind": "function",
                "name": "function",
                "widget": {"kind": "function", "name": "function"},
            },
        },
        "optional_inputs": {
            "maxsplit": {
                "kind": "number",
                "name": "maxsplit",
                "widget": {"kind": "number", "name": "maxsplit", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        function = (
            node_inputs.get("required_inputs", {}).get("function", {}).get("values")
        )
        maxsplit = (
            node_inputs.get("optional_inputs", {}).get("maxsplit", {}).get("values", 0)
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            split_parts = re.split(pattern, string, maxsplit=maxsplit, flags=flags)
            result = [function(part) for part in split_parts]
            return result
        except Exception as e:
            return [
                str(e)
            ]  # Return error message as a single-item list if operation fails


class StringRegexSubWithFlags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Performs regex substitution on a string with specified flags"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
            "repl": {
                "kind": "string",
                "name": "repl",
                "widget": {"kind": "string", "name": "repl", "default": ""},
            },
        },
        "optional_inputs": {
            "count": {
                "kind": "number",
                "name": "count",
                "widget": {"kind": "number", "name": "count", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        repl = node_inputs.get("required_inputs", {}).get("repl", {}).get("values", "")
        count = node_inputs.get("optional_inputs", {}).get("count", {}).get("values", 0)
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            result = re.sub(pattern, repl, string, count=count, flags=flags)
            return {
                "result": result,
                "substitutions_made": count if count > 0 else string.count(pattern),
            }
        except Exception as e:
            return {"error": str(e)}  # Return error message if operation fails


class StringRegexSplitWithFlags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Splits a string by the occurrences of a pattern and returns the result with the count of splits"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "maxsplit": {
                "kind": "number",
                "name": "maxsplit",
                "widget": {"kind": "number", "name": "maxsplit", "default": 0},
            },
            "flags": {
                "kind": "number",
                "name": "flags",
                "widget": {"kind": "number", "name": "flags", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        import re

        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        maxsplit = (
            node_inputs.get("optional_inputs", {}).get("maxsplit", {}).get("values", 0)
        )
        flags = node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", 0)

        try:
            result = re.split(pattern, string, maxsplit=maxsplit, flags=flags)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}  # Return error message if operation fails


class StringSlice:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Slices a string"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "start": {
                "kind": "number",
                "name": "start",
                "widget": {"kind": "number", "name": "start", "default": 0},
            },
        },
        "optional_inputs": {
            "end": {
                "kind": "number",
                "name": "end",
                "widget": {"kind": "number", "name": "end", "default": None},
            },
            "step": {
                "kind": "number",
                "name": "step",
                "widget": {"kind": "number", "name": "step", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        start = node_inputs.get("required_inputs", {}).get("start", {}).get("values", 0)
        end = node_inputs.get("optional_inputs", {}).get("end", {}).get("values", None)
        step = node_inputs.get("optional_inputs", {}).get("step", {}).get("values", 1)

        try:
            result = string[start:end:step]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringPad:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Pads a string to a specified length"

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "length": {
                "kind": "number",
                "name": "length",
                "widget": {"kind": "number", "name": "length", "default": 10},
            },
        },
        "optional_inputs": {
            "fill_char": {
                "kind": "string",
                "name": "fill_char",
                "widget": {"kind": "string", "name": "fill_char", "default": " "},
            },
            "side": {
                "kind": "string",
                "name": "side",
                "widget": {
                    "kind": "dropdown",
                    "name": "side",
                    "default": "right",
                    "options": ["left", "right", "both"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        length = (
            node_inputs.get("required_inputs", {}).get("length", {}).get("values", 10)
        )
        fill_char = (
            node_inputs.get("optional_inputs", {})
            .get("fill_char", {})
            .get("values", " ")
        )
        side = (
            node_inputs.get("optional_inputs", {})
            .get("side", {})
            .get("values", "right")
        )

        try:
            if side == "left":
                result = string.rjust(length, fill_char)
            elif side == "right":
                result = string.ljust(length, fill_char)
            elif side == "both":
                result = string.center(length, fill_char)
            else:
                raise ValueError(
                    "Invalid side option. Choose 'left', 'right', or 'both'."
                )

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringRemovePunctuation:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes all punctuation characters from a string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import string as string_module

            translator = str.maketrans("", "", string_module.punctuation)
            result = string.translate(translator)

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveWhitespace:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes all whitespace characters from a string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            result = "".join(string.split())
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveDigits:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes all digit characters from a string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            result = "".join(char for char in string if not char.isdigit())
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveSpecialCharacters:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes all special characters from a string, leaving only alphanumeric characters and spaces."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            result = "".join(
                char for char in string if char.isalnum() or char.isspace()
            )
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractNumbers:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all numbers from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            result = re.findall(r"\d+(?:\.\d+)?", string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractWords:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all words from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            result = re.findall(r"\b\w+\b", string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractSentences:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all sentences from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            result = re.findall(r"[A-Z].*?[.!?]", string, re.DOTALL)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractParagraphs:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all paragraphs from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            result = re.split(r"\n\s*\n", string)
            result = [para.strip() for para in result if para.strip()]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractEmails:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all email addresses from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            result = re.findall(email_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractUrls:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all URLs from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            url_pattern = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            result = re.findall(url_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractHashtags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all hashtags from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            hashtag_pattern = r"#\w+"
            result = re.findall(hashtag_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractMentions:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all mentions (@username) from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            mention_pattern = r"@\w+"
            result = re.findall(mention_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractDates:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all dates from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches common date formats (e.g., YYYY-MM-DD, MM/DD/YYYY, DD.MM.YYYY)
            date_pattern = r"\b(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}|\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})\b"
            result = re.findall(date_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractTimes:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all times from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches common time formats (e.g., HH:MM, HH:MM:SS, HH:MM AM/PM)
            time_pattern = r"\b(?:(?:(?:0?[1-9]|1[0-2]):[0-5]\d(?::[0-5]\d)?(?:\s?[APap][Mm])?)|(?:(?:0?\d|1\d|2[0-3]):[0-5]\d(?::[0-5]\d)?))\b"
            result = re.findall(time_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCurrency:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all currency values from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches common currency formats (e.g., $10.99, €20, £30.50)
            currency_pattern = r"\b(?:[$€£¥]|USD|EUR|GBP|JPY)\s?(?:\d{1,3}(?:,\d{3})*|\d+)(?:\.\d{1,2})?\b"
            result = re.findall(currency_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractPhoneNumbers:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all phone numbers from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches common phone number formats
            phone_pattern = r"\b(?:\+?1[-.\s]?)?(?:\(?[2-9]\d{2}\)?[-.\s]?)?[2-9]\d{2}[-.\s]?\d{4}\b"
            result = re.findall(phone_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractIpAddresses:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all IP addresses from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches both IPv4 and IPv6 addresses
            ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b|(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}"
            result = re.findall(ip_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractHtmlTags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all HTML tags from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches HTML tags
            html_tag_pattern = r"<[^>]+>"
            result = re.findall(html_tag_pattern, string)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractJsonKeys:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all JSON keys from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import json
            import re

            # This pattern matches JSON-like key-value pairs
            json_key_pattern = r'"([^"]+)"\s*:'

            # Find all potential JSON keys
            potential_keys = re.findall(json_key_pattern, string)

            # Validate if the string is a valid JSON
            try:
                json_obj = json.loads(string)
                # If it's a valid JSON, return all top-level keys
                result = list(json_obj.keys())
            except json.JSONDecodeError:
                # If it's not a valid JSON, return all potential keys found by regex
                result = potential_keys

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractXmlTags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts all XML tags from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # This pattern matches XML tags
            xml_tag_pattern = r"<([^\s>]+)(?:\s+[^>]*)?>"

            # Find all XML tags
            xml_tags = re.findall(xml_tag_pattern, string)

            # Remove duplicates and sort
            result = sorted(set(xml_tags))

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCsvColumns:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts column names from a CSV string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
        "optional_inputs": {
            "delimiter": {
                "kind": "string",
                "name": "delimiter",
                "widget": {"kind": "string", "name": "delimiter", "default": ","},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        delimiter = (
            node_inputs.get("optional_inputs", {})
            .get("delimiter", {})
            .get("values", ",")
        )

        try:
            import csv
            from io import StringIO

            # Read the first line of the CSV string
            csv_reader = csv.reader(StringIO(string), delimiter=delimiter)
            headers = next(csv_reader, [])

            # Remove any leading/trailing whitespace from column names
            result = [header.strip() for header in headers]

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractMarkdownHeaders:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts headers from a Markdown-formatted string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        markdown_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # Regular expression to match Markdown headers
            header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

            # Find all headers in the Markdown string
            headers = header_pattern.findall(markdown_string)

            # Format the results as a list of tuples (level, header_text)
            result = [(len(level), text.strip()) for level, text in headers]

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCodeBlocks:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts code blocks from a Markdown-formatted string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        markdown_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # Regular expression to match code blocks
            code_block_pattern = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)

            # Find all code blocks in the Markdown string
            code_blocks = code_block_pattern.findall(markdown_string)

            # Strip leading and trailing whitespace from each code block
            result = [block.strip() for block in code_blocks]

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts comments from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "c", "cpp", "java"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define regex patterns for different comment types
            patterns = {
                "python": r'(#.*?$|\'\'\'[\s\S]*?\'\'\'|"""[\s\S]*?""")',
                "javascript": r"(//.*?$|/\*[\s\S]*?\*/)",
                "c": r"(//.*?$|/\*[\s\S]*?\*/)",
                "cpp": r"(//.*?$|/\*[\s\S]*?\*/)",
                "java": r"(//.*?$|/\*[\s\S]*?\*/)",
            }

            pattern = patterns.get(language, patterns["python"])
            comments = re.findall(pattern, code_string, re.MULTILINE)

            # Clean up the extracted comments
            result = [comment.strip() for comment in comments if comment.strip()]

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractFunctions:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts function names from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "c", "cpp", "java"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define function patterns for different languages
            function_patterns = {
                "python": r"\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
                "javascript": r"\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(|\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*function\s*\(",
                "c": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*{",
                "cpp": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(const)?\s*{",
                "java": r"\b(public|private|protected)?\s*(static)?\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(",
            }

            # Get the function pattern for the specified language
            function_pattern = function_patterns.get(
                language, function_patterns["python"]
            )

            # Extract function names from the code string
            if language == "java":
                result = sorted(
                    set(re.findall(function_pattern, code_string, re.MULTILINE))
                )
                result = [
                    func[2] for func in result if func[2]
                ]  # Extract the function name (third group)
            elif language == "javascript":
                matches = re.findall(function_pattern, code_string, re.MULTILINE)
                result = sorted(set(match[0] or match[1] for match in matches))
            else:
                result = sorted(
                    set(re.findall(function_pattern, code_string, re.MULTILINE))
                )

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractClasses:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts class names from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "java", "cpp"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define class patterns for different languages
            class_patterns = {
                "python": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                "javascript": r"\bclass\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",
                "java": r"\bclass\s+([a-zA-Z_$][a-zA-Z0-9_$]*)",
                "cpp": r"\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)",
            }

            # Get the class pattern for the specified language
            class_pattern = class_patterns.get(language, class_patterns["python"])

            # Extract class names from the code string
            result = sorted(set(re.findall(class_pattern, code_string, re.MULTILINE)))

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractModules:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts module names from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "java"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define module patterns for different languages
            module_patterns = {
                "python": r"\bimport\s+(\w+)|\bfrom\s+(\w+)\s+import",
                "javascript": r'\bimport\s+.*\s+from\s+[\'"](.+?)[\'"]|\brequire\s*\([\'"](.+?)[\'"]\)',
                "java": r"\bimport\s+([\w.]+)(?:\s*;\s*|\s+)",
            }

            # Get the module pattern for the specified language
            module_pattern = module_patterns.get(language, module_patterns["python"])

            # Extract module names from the code string
            matches = re.findall(module_pattern, code_string, re.MULTILINE)

            # Flatten the list of tuples and remove empty strings
            result = sorted(set(filter(None, sum(matches, ()))))

            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StringExtractImports:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts imports from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "java"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define import patterns for different languages
            import_patterns = {
                "python": r"^\s*(?:from\s+(\w+(?:\.\w+)*)\s+)?import\s+(\w+(?:\s*,\s*\w+)*|\*)",
                "javascript": r'(?:import\s+(?:\*\s+as\s+\w+|\{\s*[\w\s,]+\}\s*|\w+)\s+from\s+["\']([^"\']+)["\']|require\(["\']([^"\']+)["\']\))',
                "java": r"^\s*import\s+([\w.]+(?:\.\*)?)\s*;",
            }

            # Get the import pattern for the specified language
            import_pattern = import_patterns.get(language, import_patterns["python"])

            # Extract imports from the code string
            matches = re.findall(import_pattern, code_string, re.MULTILINE)

            # Process matches based on language
            if language == "python":
                result = [m[0] or m[1] for m in matches]
            elif language == "javascript":
                result = [m[0] or m[1] for m in matches if m[0] or m[1]]
            else:  # Java
                result = matches

            return {"result": sorted(set(result))}
        except Exception as e:
            return {"error": str(e)}


class StringExtractExports:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts exports from a given string of code."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
            "language": {
                "kind": "string",
                "name": "language",
                "widget": {
                    "kind": "dropdown",
                    "name": "language",
                    "default": "python",
                    "options": ["python", "javascript", "java"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        code_string = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )
        language = (
            node_inputs.get("required_inputs", {})
            .get("language", {})
            .get("values", "python")
        )

        try:
            import re

            # Define export patterns for different languages
            export_patterns = {
                "python": r"^\s*(?:def|class)\s+(\w+)(?:\s*\(.*\)\s*:|\s*:)",
                "javascript": r"(?:export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)|module\.exports\s*=\s*(?:{[^}]*}|\w+))",
                "java": r"(?:public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(?:\{?|[^;])",
            }

            # Get the export pattern for the specified language
            export_pattern = export_patterns.get(language, export_patterns["python"])

            # Extract exports from the code string
            matches = re.findall(export_pattern, code_string, re.MULTILINE)

            # Process matches
            result = list(set(matches))

            return {"result": sorted(result)}
        except Exception as e:
            return {"error": str(e)}


class StringExtractExtensions:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts file extensions from a given string."

    INPUT = {
        "required_inputs": {
            "string": {
                "kind": "string",
                "name": "string",
                "widget": {"kind": "string", "name": "string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = (
            node_inputs.get("required_inputs", {}).get("string", {}).get("values", "")
        )

        try:
            import re

            # Regular expression pattern for file extensions
            extension_pattern = r"\.([a-zA-Z0-9]+)(?=\s|$)"

            # Extract extensions from the text
            extensions = re.findall(extension_pattern, text)

            return {"result": sorted(set(extensions))}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveDuplicates:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes duplicate words from the input text."

    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "string",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
        },
        "optional_inputs": {
            "case_sensitive": {
                "kind": "boolean",
                "name": "case_sensitive",
                "widget": {
                    "kind": "checkbox",
                    "name": "case_sensitive",
                    "default": False,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "deduplicated_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = node_inputs.get("required_inputs", {}).get("text", {}).get("values", "")
        case_sensitive = (
            node_inputs.get("optional_inputs", {})
            .get("case_sensitive", {})
            .get("values", False)
        )

        try:
            words = text.split()
            if case_sensitive:
                unique_words = []
                seen = set()
                for word in words:
                    if word not in seen:
                        seen.add(word)
                        unique_words.append(word)
            else:
                unique_words = []
                seen = set()
                for word in words:
                    lower_word = word.lower()
                    if lower_word not in seen:
                        seen.add(lower_word)
                        unique_words.append(word)

            deduplicated_text = " ".join(unique_words)
            return {"deduplicated_text": deduplicated_text}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveHtmlEntities:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes HTML entities from the input text."

    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "string",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "cleaned_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = node_inputs.get("required_inputs", {}).get("text", {}).get("values", "")

        try:
            import html

            cleaned_text = html.unescape(text)
            return {"cleaned_text": cleaned_text}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveXmlEntities:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes XML entities from the input text."

    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "string",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "cleaned_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = node_inputs.get("required_inputs", {}).get("text", {}).get("values", "")

        try:
            import xml.sax.saxutils as saxutils

            cleaned_text = saxutils.unescape(text)
            return {"cleaned_text": cleaned_text}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveUnicode:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Removes Unicode characters from the input text, keeping only ASCII characters."
    )

    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "string",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "ascii_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = node_inputs.get("required_inputs", {}).get("text", {}).get("values", "")

        try:
            ascii_text = text.encode("ascii", "ignore").decode("ascii")
            return {"ascii_text": ascii_text}
        except Exception as e:
            return {"error": str(e)}


class StringNormalizeUnicode:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Normalizes Unicode characters in the input text."

    INPUT = {
        "required_inputs": {
            "text": {
                "kind": "string",
                "name": "text",
                "widget": {"kind": "string", "name": "text", "default": ""},
            },
            "form": {
                "kind": "string",
                "name": "form",
                "widget": {
                    "kind": "dropdown",
                    "name": "form",
                    "default": "NFKC",
                    "options": ["NFC", "NFKC", "NFD", "NFKD"],
                },
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "normalized_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        text = node_inputs.get("required_inputs", {}).get("text", {}).get("values", "")
        form = (
            node_inputs.get("required_inputs", {}).get("form", {}).get("values", "NFKC")
        )

        try:
            import unicodedata

            normalized_text = unicodedata.normalize(form, text)
            return {"normalized_text": normalized_text}
        except Exception as e:
            return {"error": str(e)}


class StringMatchCase:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Matches the case of the input text to the target text."

    INPUT = {
        "required_inputs": {
            "input_text": {
                "kind": "string",
                "name": "input_text",
                "widget": {"kind": "string", "name": "input_text", "default": ""},
            },
            "target_text": {
                "kind": "string",
                "name": "target_text",
                "widget": {"kind": "string", "name": "target_text", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "matched_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_text = (
            node_inputs.get("required_inputs", {})
            .get("input_text", {})
            .get("values", "")
        )
        target_text = (
            node_inputs.get("required_inputs", {})
            .get("target_text", {})
            .get("values", "")
        )

        try:
            if target_text.isupper():
                matched_text = input_text.upper()
            elif target_text.islower():
                matched_text = input_text.lower()
            elif target_text.istitle():
                matched_text = input_text.title()
            else:
                matched_text = input_text  # Keep original case if target case is mixed

            return {"matched_text": matched_text}
        except Exception as e:
            return {"error": str(e)}


class StringMatchLength:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Matches the length of the input text to the target length."

    INPUT = {
        "required_inputs": {
            "input_text": {
                "kind": "string",
                "name": "input_text",
                "widget": {"kind": "string", "name": "input_text", "default": ""},
            },
            "target_length": {
                "kind": "number",
                "name": "target_length",
                "widget": {
                    "kind": "number",
                    "name": "target_length",
                    "default": 10,
                    "min": 0,
                },
            },
        },
        "optional_inputs": {
            "fill_char": {
                "kind": "string",
                "name": "fill_char",
                "widget": {"kind": "string", "name": "fill_char", "default": " "},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "matched_text",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_text = (
            node_inputs.get("required_inputs", {})
            .get("input_text", {})
            .get("values", "")
        )
        target_length = (
            node_inputs.get("required_inputs", {})
            .get("target_length", {})
            .get("values", 10)
        )
        fill_char = (
            node_inputs.get("optional_inputs", {})
            .get("fill_char", {})
            .get("values", " ")
        )

        try:
            if len(fill_char) != 1:
                raise ValueError("Fill character must be a single character.")

            if len(input_text) > target_length:
                matched_text = input_text[:target_length]
            else:
                matched_text = input_text.ljust(target_length, fill_char)

            return {"matched_text": matched_text}
        except Exception as e:
            return {"error": str(e)}


class StringMatchPattern:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = (
        "Matches the input text against a specified pattern using regular expressions."
    )

    INPUT = {
        "required_inputs": {
            "input_text": {
                "kind": "string",
                "name": "input_text",
                "widget": {"kind": "string", "name": "input_text", "default": ""},
            },
            "pattern": {
                "kind": "string",
                "name": "pattern",
                "widget": {"kind": "string", "name": "pattern", "default": ""},
            },
        },
        "optional_inputs": {
            "flags": {
                "kind": "string",
                "name": "flags",
                "widget": {"kind": "string", "name": "flags", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "match_result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_text = (
            node_inputs.get("required_inputs", {})
            .get("input_text", {})
            .get("values", "")
        )
        pattern = (
            node_inputs.get("required_inputs", {}).get("pattern", {}).get("values", "")
        )
        flags = (
            node_inputs.get("optional_inputs", {}).get("flags", {}).get("values", "")
        )

        try:
            import re

            # Parse flags
            regex_flags = 0
            if "i" in flags:
                regex_flags |= re.IGNORECASE
            if "m" in flags:
                regex_flags |= re.MULTILINE
            if "s" in flags:
                regex_flags |= re.DOTALL

            # Perform pattern matching
            match_result = bool(re.match(pattern, input_text, regex_flags))

            return {"match_result": match_result}
        except Exception as e:
            return {"error": str(e)}


class StringMatchNone:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Checks if the input string matches none of the specified patterns."

    INPUT = {
        "required_inputs": {
            "input_text": {
                "kind": "string",
                "name": "input_text",
                "widget": {"kind": "string", "name": "input_text", "default": ""},
            },
            "patterns": {
                "kind": "array",
                "name": "patterns",
                "widget": {"kind": "array", "name": "patterns", "default": []},
            },
        },
        "optional_inputs": {
            "case_sensitive": {
                "kind": "boolean",
                "name": "case_sensitive",
                "widget": {
                    "kind": "checkbox",
                    "name": "case_sensitive",
                    "default": True,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "matches_none",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_text = (
            node_inputs.get("required_inputs", {})
            .get("input_text", {})
            .get("values", "")
        )
        patterns = (
            node_inputs.get("required_inputs", {}).get("patterns", {}).get("values", [])
        )
        case_sensitive = (
            node_inputs.get("optional_inputs", {})
            .get("case_sensitive", {})
            .get("values", True)
        )

        try:
            if not case_sensitive:
                input_text = input_text.lower()
                patterns = [pattern.lower() for pattern in patterns]

            matches_none = all(pattern not in input_text for pattern in patterns)

            return {"matches_none": matches_none}
        except Exception as e:
            return {"error": str(e)}


class StringMatchFuzzy:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Performs fuzzy string matching between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {
            "threshold": {
                "kind": "number",
                "name": "threshold",
                "widget": {
                    "kind": "number",
                    "name": "threshold",
                    "default": 0.6,
                    "min": 0.0,
                    "max": 1.0,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "fuzzy_match_result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )
        threshold = (
            node_inputs.get("optional_inputs", {})
            .get("threshold", {})
            .get("values", 0.6)
        )

        try:
            from fuzzywuzzy import fuzz

            ratio = fuzz.ratio(string1, string2) / 100.0
            partial_ratio = fuzz.partial_ratio(string1, string2) / 100.0
            token_sort_ratio = fuzz.token_sort_ratio(string1, string2) / 100.0
            token_set_ratio = fuzz.token_set_ratio(string1, string2) / 100.0

            is_match = (
                any([ratio, partial_ratio, token_sort_ratio, token_set_ratio])
                >= threshold
            )

            return {
                "fuzzy_match_result": {
                    "is_match": is_match,
                    "ratio": ratio,
                    "partial_ratio": partial_ratio,
                    "token_sort_ratio": token_sort_ratio,
                    "token_set_ratio": token_set_ratio,
                }
            }
        except Exception as e:
            return {"error": str(e)}


class StringMatchSimilarity:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the similarity between two strings using various metrics."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {
            "metric": {
                "kind": "string",
                "name": "metric",
                "widget": {
                    "kind": "dropdown",
                    "name": "metric",
                    "default": "cosine",
                    "options": ["cosine", "jaccard", "levenshtein", "jaro_winkler"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )
        metric = (
            node_inputs.get("optional_inputs", {})
            .get("metric", {})
            .get("values", "cosine")
        )

        try:
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            from Levenshtein import ratio
            from jellyfish import jaro_winkler_similarity

            if metric == "cosine":
                vectorizer = CountVectorizer().fit_transform([string1, string2])
                similarity = cosine_similarity(vectorizer)[0][1]
            elif metric == "jaccard":
                set1 = set(string1.split())
                set2 = set(string2.split())
                similarity = len(set1.intersection(set2)) / len(set1.union(set2))
            elif metric == "levenshtein":
                similarity = ratio(string1, string2)
            elif metric == "jaro_winkler":
                similarity = jaro_winkler_similarity(string1, string2)
            else:
                return {"error": "Invalid metric specified"}

            return {"similarity": similarity}
        except Exception as e:
            return {"error": str(e)}


class StringMatchCosine:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the cosine similarity between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = CountVectorizer().fit_transform([string1, string2])
            similarity = cosine_similarity(vectorizer)[0][1]
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringMatchLevenshtein:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the Levenshtein distance between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            import Levenshtein

            distance = Levenshtein.distance(string1, string2)
            max_length = max(len(string1), len(string2))
            similarity = 1 - (distance / max_length)
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringMatchHamming:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the Hamming distance between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            from Levenshtein import hamming

            distance = hamming(string1, string2)
            max_length = max(len(string1), len(string2))
            similarity = 1 - (distance / max_length)
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringMatchJaro:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the Jaro similarity between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            from jellyfish import jaro_similarity

            similarity = jaro_similarity(string1, string2)
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringMatchJaroWinkler:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the Jaro-Winkler similarity between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            from jellyfish import jaro_winkler_similarity

            similarity = jaro_winkler_similarity(string1, string2)
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringMatchTfIdf:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Calculates the TF-IDF similarity between two strings."

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": ""},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": ""},
            },
        },
        "optional_inputs": {},
    }

    OUTPUT = {
        "kind": "number",
        "name": "similarity",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {}).get("string1", {}).get("values", "")
        )
        string2 = (
            node_inputs.get("required_inputs", {}).get("string2", {}).get("values", "")
        )

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([string1, string2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return {"similarity": float(similarity)}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveAccentedCharacters:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes accented characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import unicodedata

            normalized = unicodedata.normalize("NFKD", input_string)
            output_string = "".join(
                [c for c in normalized if not unicodedata.combining(c)]
            )

            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveEmojis:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes emojis from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            emoji_pattern = re.compile(
                "["
                "\U0001f600-\U0001f64f"  # emoticons
                "\U0001f300-\U0001f5ff"  # symbols & pictographs
                "\U0001f680-\U0001f6ff"  # transport & map symbols
                "\U0001f1e0-\U0001f1ff"  # flags (iOS)
                "\U00002702-\U000027b0"
                "\U000024c2-\U0001f251"
                "]+",
                flags=re.UNICODE,
            )

            output_string = emoji_pattern.sub(r"", input_string)

            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveUrls:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes URLs from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            url_pattern = re.compile(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            )
            output_string = url_pattern.sub("", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveEmails:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes email addresses from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            email_pattern = re.compile(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            )
            output_string = email_pattern.sub("", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveMentions:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes mentions (e.g., @username) from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            mention_pattern = re.compile(r"@\w+")
            output_string = mention_pattern.sub("", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveHashtags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes hashtags from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            hashtag_pattern = re.compile(r"#\w+")
            output_string = hashtag_pattern.sub("", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveHtmlTags:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes HTML tags from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            html_pattern = re.compile("<.*?>")
            output_string = html_pattern.sub("", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonAscii:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-ASCII characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = "".join(char for char in input_string if ord(char) < 128)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonPrintable:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-printable characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = "".join(char for char in input_string if char.isprintable())
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonAlphanumeric:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-alphanumeric characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = "".join(char for char in input_string if char.isalnum())
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonLetters:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-letter characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = "".join(char for char in input_string if char.isalpha())
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonDigits:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-digit characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = "".join(char for char in input_string if char.isdigit())
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonWords:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-word characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            output_string = re.sub(r"\W+", "", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonSentences:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-sentence text from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            sentences = re.findall(r"\w+[^.!?]*[.!?]", input_string)
            output_string = " ".join(sentences)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonParagraphs:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-paragraph text from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            paragraphs = re.split(r"\n\s*\n", input_string)
            output_string = "\n\n".join(
                paragraph.strip() for paragraph in paragraphs if paragraph.strip()
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonSymbols:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-symbol characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import string

            output_string = "".join(
                char for char in input_string if char in string.punctuation
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveNonOperators:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes non-operator characters from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            operators = set("+-*/=%<>&|^~!")
            output_string = "".join(char for char in input_string if char in operators)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToUtf16:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to UTF-16."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = input_string.encode("utf-16").decode("utf-16")
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToUtf32:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to UTF-32."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = input_string.encode("utf-32").decode("utf-32")
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToBase64:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to Base64."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import base64

            output_string = base64.b64encode(input_string.encode()).decode()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeBase64:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes a Base64 string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import base64

            output_string = base64.b64decode(input_string).decode()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToHex:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to hexadecimal."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = input_string.encode().hex()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeHex:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes a hexadecimal string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = bytes.fromhex(input_string).decode()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToBinary:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to binary."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = " ".join(format(ord(char), "08b") for char in input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeBinary:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes a binary string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            binary_values = input_string.split()
            output_string = "".join(chr(int(binary, 2)) for binary in binary_values)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToOctal:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to octal."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            output_string = " ".join(format(ord(char), "03o") for char in input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeOctal:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes an octal string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            octal_values = input_string.split()
            output_string = "".join(chr(int(octal, 8)) for octal in octal_values)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToHtmlEntities:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to HTML entities."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import html

            output_string = html.escape(input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeHtmlEntities:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes HTML entities in a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import html

            output_string = html.unescape(input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToUrlEncoding:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to URL encoding."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import urllib.parse

            output_string = urllib.parse.quote(input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDecodeUrlEncoding:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Decodes a URL-encoded string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import urllib.parse

            output_string = urllib.parse.unquote(input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringParseJson:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses a JSON string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import json

            parsed_json = json.loads(input_string)
            output_string = json.dumps(parsed_json, indent=2)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringParseXml:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses an XML string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import xml.etree.ElementTree as ET
            import xml.dom.minidom as minidom

            root = ET.fromstring(input_string)
            xml_string = ET.tostring(root, encoding="unicode")
            pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
            return {"output_string": pretty_xml}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToCsv:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to CSV format."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)
            for row in input_string.split("\n"):
                writer.writerow(row.split(","))
            return {"output_string": output.getvalue()}
        except Exception as e:
            return {"error": str(e)}


class StringParseCsv:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses a CSV string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import csv
            import io

            output = []
            reader = csv.reader(io.StringIO(input_string))
            for row in reader:
                output.append(row)
            return {"output_string": str(output)}
        except Exception as e:
            return {"error": str(e)}


class StringParseYaml:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses a YAML string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import yaml

            data = yaml.safe_load(input_string)
            output_string = yaml.dump(data, default_flow_style=False)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringParseIni:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses an INI string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import configparser
            import json

            config = configparser.ConfigParser()
            config.read_string(input_string)

            output_dict = {
                section: dict(config[section]) for section in config.sections()
            }
            output_string = json.dumps(output_dict, indent=2)

            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringParseRtf:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Parses an RTF string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import re

            # This is a very basic RTF parser. For complex RTF, you might need a more robust solution.
            plain_text = re.sub(
                r"\\[a-z]{1,32}(-?\d{1,10})?[ ]?|\\'[0-9a-f]{2}|\\([^a-z])|([{}])|[\r\n]+|(.)",
                lambda match: match.group(3) or match.group(4) or match.group(5) or "",
                input_string,
            )
            return {"output_string": plain_text}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToMd5:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to MD5 hash."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import hashlib

            output_string = hashlib.md5(input_string.encode()).hexdigest()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToSha1:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to SHA1 hash."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import hashlib

            output_string = hashlib.sha1(input_string.encode()).hexdigest()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToSha256:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to SHA256 hash."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import hashlib

            output_string = hashlib.sha256(input_string.encode()).hexdigest()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringConvertToSha512:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Converts a string to SHA512 hash."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )

        try:
            import hashlib

            output_string = hashlib.sha512(input_string.encode()).hexdigest()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringHashString:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Hashes a string using a specified algorithm."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
            "algorithm": {
                "kind": "string",
                "name": "algorithm",
                "widget": {
                    "kind": "dropdown",
                    "name": "algorithm",
                    "default": "sha256",
                    "options": ["md5", "sha1", "sha256", "sha512"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        algorithm = (
            node_inputs.get("required_inputs", {})
            .get("algorithm", {})
            .get("values", "sha256")
        )

        try:
            import hashlib

            hash_function = getattr(hashlib, algorithm)
            output_string = hash_function(input_string.encode()).hexdigest()
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringVerifyHash:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Verifies a hash against a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
            "hash": {
                "kind": "string",
                "name": "hash",
                "widget": {"kind": "string", "name": "hash", "default": ""},
            },
            "algorithm": {
                "kind": "string",
                "name": "algorithm",
                "widget": {
                    "kind": "dropdown",
                    "name": "algorithm",
                    "default": "sha256",
                    "options": ["md5", "sha1", "sha256", "sha512"],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "is_valid",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        hash_to_verify = (
            node_inputs.get("required_inputs", {}).get("hash", {}).get("values", "")
        )
        algorithm = (
            node_inputs.get("required_inputs", {})
            .get("algorithm", {})
            .get("values", "sha256")
        )

        try:
            import hashlib

            hash_function = getattr(hashlib, algorithm)
            computed_hash = hash_function(input_string.encode()).hexdigest()
            is_valid = computed_hash == hash_to_verify
            return {"is_valid": is_valid}
        except Exception as e:
            return {"error": str(e)}


class StringGenerateUuid:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Generates a UUID."

    INPUT = {  # type: ignore
        "required_inputs": {},
    }

    OUTPUT = {
        "kind": "string",
        "name": "uuid",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        try:
            import uuid

            generated_uuid = str(uuid.uuid4())
            return {"uuid": generated_uuid}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveHtmlComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes HTML comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(r"<!--[\s\S]*?-->", "", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveXmlComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes XML comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(r"<!--[\s\S]*?-->", "", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveJsonComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes JSON comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(
                r"(//.*?$|/\*[\s\S]*?\*/)", "", input_string, flags=re.MULTILINE
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveCssComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes CSS comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(r"/\*[\s\S]*?\*/", "", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveJsComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes JavaScript comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(
                r"(//.*?$|/\*[\s\S]*?\*/)", "", input_string, flags=re.MULTILINE
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveMultilineComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes multiline comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(r"/\*[\s\S]*?\*/", "", input_string)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringRemoveSinglelineComments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Removes single-line comments from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            output_string = re.sub(r"//.*?$", "", input_string, flags=re.MULTILINE)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractHtmlAttributes:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts HTML attributes from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            attributes = re.findall(r'(\w+)=["\']([^"\']*)["\']', input_string)
            output_string = "\n".join(
                [f"{attr}: {value}" for attr, value in attributes]
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractXmlAttributes:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts XML attributes from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            attributes = re.findall(r'(\w+)=["\']([^"\']*)["\']', input_string)
            output_string = "\n".join(
                [f"{attr}: {value}" for attr, value in attributes]
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCssSelectors:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts CSS selectors from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            selectors = re.findall(r"([^\{\}]+)\{", input_string)
            output_string = "\n".join(selector.strip() for selector in selectors)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractHtmlDataAttributes:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts HTML data attributes from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            data_attrs = re.findall(r'data-[\w-]+=["\']([^"\']+)["\']', input_string)
            output_string = "\n".join(set(data_attrs))
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractXmlNamespaces:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts XML namespaces from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            namespaces = re.findall(r'xmlns:(\w+)=["\']([^"\']+)["\']', input_string)
            output_string = "\n".join(
                [f"{prefix}: {uri}" for prefix, uri in namespaces]
            )
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCsvRows:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts CSV rows from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import csv
            from io import StringIO

            csv_file = StringIO(input_string)
            csv_reader = csv.reader(csv_file)
            rows = list(csv_reader)
            output_string = "\n".join([",".join(row) for row in rows])
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCsvHeaders:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts CSV headers from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import csv
            from io import StringIO

            csv_file = StringIO(input_string)
            csv_reader = csv.reader(csv_file)
            headers = next(csv_reader, None)
            output_string = ",".join(headers) if headers else ""
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractCsvCells:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts CSV cells from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import csv
            from io import StringIO

            csv_file = StringIO(input_string)
            csv_reader = csv.reader(csv_file)
            cells = [cell for row in csv_reader for cell in row]
            output_string = "\n".join(cells)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractYamlDocuments:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts YAML documents from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import yaml

            documents = list(yaml.safe_load_all(input_string))
            output_string = "\n---\n".join(yaml.dump(doc) for doc in documents)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractYamlKeys:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts YAML keys from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import yaml

            data = yaml.safe_load(input_string)
            keys = self.extract_keys(data)
            output_string = "\n".join(keys)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}

    def extract_keys(self, obj, prefix=""):
        keys = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                keys.append(f"{prefix}{k}")
                keys.extend(self.extract_keys(v, f"{prefix}{k}."))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                keys.extend(self.extract_keys(item, f"{prefix}[{i}]."))
        return keys


class StringExtractYamlValues:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts YAML values from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import yaml

            data = yaml.safe_load(input_string)
            values = self.extract_values(data)
            output_string = "\n".join(map(str, values))
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}

    def extract_values(self, obj):
        values = []
        if isinstance(obj, dict):
            for v in obj.values():
                values.extend(self.extract_values(v))
        elif isinstance(obj, list):
            for item in obj:
                values.extend(self.extract_values(item))
        else:
            values.append(obj)
        return values


class StringExtractMarkdownLinks:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts Markdown links from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", input_string)
            output_string = "\n".join([f"{text}: {url}" for text, url in links])
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractMarkdownImages:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts Markdown images from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            images = re.findall(r"!\[([^\]]*)\]\(([^\)]+)\)", input_string)
            output_string = "\n".join([f"{alt}: {url}" for alt, url in images])
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractMarkdownCodeBlocks:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts Markdown code blocks from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        import re

        code_blocks = re.findall(r"```[\s\S]*?```", input_string)
        output_string = "\n\n".join(code_blocks)
        return {"output_string": output_string}


class StringExtractMarkdownLists:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts Markdown lists from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            lists = re.findall(
                r"((?:^\s*[-*+]\s+.+(?:\n|$))+)", input_string, re.MULTILINE
            )
            output_string = "\n\n".join(lists)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringExtractMarkdownTables:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Extracts Markdown tables from a string."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import re

            tables = re.findall(r"(\|.+\|[\s\S]*?\n)(?:\n|$)", input_string)
            output_string = "\n\n".join(tables)
            return {"output_string": output_string}
        except Exception as e:
            return {"error": str(e)}


class StringDependencyParsing:
    CATEGORY = "utilities"
    SUBCATEGORY = "string"
    DESCRIPTION = "Performs dependency parsing on the input text."

    INPUT = {
        "required_inputs": {
            "input_string": {
                "kind": "string",
                "name": "input_string",
                "widget": {"kind": "string", "name": "input_string", "default": ""},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "output_string",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input_string = (
            node_inputs.get("required_inputs", {})
            .get("input_string", {})
            .get("values", "")
        )
        try:
            import spacy

            nlp = spacy.load("en_core_web_sm")
            doc = nlp(input_string)
            result = [
                f"{token.text} -> {token.dep_} -> {token.head.text}" for token in doc
            ]
            return {"output_string": "\n".join(result)}
        except Exception as e:
            return {"error": str(e)}


class Modulus:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the remainder of division between two numbers."

    INPUT = {
        "required_inputs": {
            "dividend": {
                "kind": "number",
                "name": "dividend",
                "widget": {"kind": "number", "name": "dividend", "default": 0},
            },
            "divisor": {
                "kind": "number",
                "name": "divisor",
                "widget": {"kind": "number", "name": "divisor", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        dividend = (
            node_inputs.get("required_inputs", {}).get("dividend", {}).get("values", 0)
        )
        divisor = (
            node_inputs.get("required_inputs", {}).get("divisor", {}).get("values", 1)
        )
        try:
            result = dividend % divisor
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FloorDivision:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Performs floor division between two numbers."

    INPUT = {
        "required_inputs": {
            "dividend": {
                "kind": "number",
                "name": "dividend",
                "widget": {"kind": "number", "name": "dividend", "default": 0},
            },
            "divisor": {
                "kind": "number",
                "name": "divisor",
                "widget": {"kind": "number", "name": "divisor", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        dividend = (
            node_inputs.get("required_inputs", {}).get("dividend", {}).get("values", 0)
        )
        divisor = (
            node_inputs.get("required_inputs", {}).get("divisor", {}).get("values", 1)
        )
        try:
            result = dividend // divisor
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SquareRoot:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the square root of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.sqrt(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class AbsoluteValue:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the absolute value of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            result = abs(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Logarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm of a number with a specified base."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        base = node_inputs.get("required_inputs", {}).get("base", {}).get("values", 10)
        try:
            import math

            result = math.log(number, base)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Power:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Raises a number to the power of another number."

    INPUT = {
        "required_inputs": {
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 1},
            },
            "exponent": {
                "kind": "number",
                "name": "exponent",
                "widget": {"kind": "number", "name": "exponent", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        base = node_inputs.get("required_inputs", {}).get("base", {}).get("values", 1)
        exponent = (
            node_inputs.get("required_inputs", {}).get("exponent", {}).get("values", 1)
        )
        try:
            result = base**exponent
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Round:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Rounds a number to a specified number of decimal places."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
            "decimal_places": {
                "kind": "number",
                "name": "decimal_places",
                "widget": {"kind": "number", "name": "decimal_places", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        decimal_places = (
            node_inputs.get("required_inputs", {})
            .get("decimal_places", {})
            .get("values", 0)
        )
        try:
            result = round(number, decimal_places)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Ceil:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the ceiling of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.ceil(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Floor:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the floor of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.floor(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Truncate:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Truncates a number to an integer by removing the fractional part."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            result = int(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Mean:
    CATEGORY = "numerics"
    SUBCATEGORY = "statistics"
    DESCRIPTION = "Computes the average of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if not numbers:
                raise ValueError("Input list is empty")
            result = sum(numbers) / len(numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Median:
    CATEGORY = "numerics"
    SUBCATEGORY = "statistics"
    DESCRIPTION = "Finds the median value from a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if not numbers:
                raise ValueError("Input list is empty")
            sorted_numbers = sorted(numbers)
            n = len(sorted_numbers)
            if n % 2 == 0:
                result = (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
            else:
                result = sorted_numbers[n // 2]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Mode:
    CATEGORY = "numerics"
    SUBCATEGORY = "statistics"
    DESCRIPTION = "Determines the most frequently occurring number in a list."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if not numbers:
                raise ValueError("Input list is empty")
            from statistics import mode

            result = mode(numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Variance:
    CATEGORY = "numerics"
    SUBCATEGORY = "statistics"
    DESCRIPTION = "Calculates the variance of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if len(numbers) < 2:
                raise ValueError(
                    "At least two numbers are required to calculate variance"
                )
            mean = sum(numbers) / len(numbers)
            variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
            return {"result": variance}
        except Exception as e:
            return {"error": str(e)}


class StandardDeviation:
    CATEGORY = "numerics"
    SUBCATEGORY = "statistics"
    DESCRIPTION = "Computes the standard deviation of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if len(numbers) < 2:
                raise ValueError(
                    "At least two numbers are required to calculate standard deviation"
                )
            mean = sum(numbers) / len(numbers)
            variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
            std_dev = variance**0.5
            return {"result": std_dev}
        except Exception as e:
            return {"error": str(e)}


class GCD:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the greatest common divisor of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)
        try:
            import math

            result = math.gcd(a, b)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LCM:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the least common multiple of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)
        try:
            import math

            result = abs(a * b) // math.gcd(a, b)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Factorial:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Computes the factorial of a non-negative integer."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            if number < 0:
                raise ValueError("Factorial is not defined for negative numbers")
            result = math.factorial(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Sign:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Determines the sign of a number (positive, negative, or zero)."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            if number > 0:
                result = 1
            elif number < 0:
                result = -1
            else:
                result = 0
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Clamp:
    CATEGORY = "numerics"
    SUBCATEGORY = "basic"
    DESCRIPTION = "Restricts a number to be within a specified range."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
            "min_value": {
                "kind": "number",
                "name": "min_value",
                "widget": {"kind": "number", "name": "min_value", "default": 0},
            },
            "max_value": {
                "kind": "number",
                "name": "max_value",
                "widget": {"kind": "number", "name": "max_value", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        min_value = (
            node_inputs.get("required_inputs", {}).get("min_value", {}).get("values", 0)
        )
        max_value = (
            node_inputs.get("required_inputs", {}).get("max_value", {}).get("values", 1)
        )
        try:
            result = max(min_value, min(number, max_value))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HarmonicMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the harmonic mean of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if not numbers:
                raise ValueError("Input list is empty")
            harmonic_mean = len(numbers) / sum(1 / x for x in numbers if x != 0)
            return {"result": harmonic_mean}
        except Exception as e:
            return {"error": str(e)}


class GeometricMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the geometric mean of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            if not numbers:
                raise ValueError("Input list is empty")
            product = 1
            for num in numbers:
                product *= num
            geometric_mean = product ** (1 / len(numbers))
            return {"result": geometric_mean}
        except Exception as e:
            return {"error": str(e)}


class CubicRoot:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cubic root of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            result = number ** (1 / 3)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogBase10:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the base-10 logarithm of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log10(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogBase2:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the base-2 logarithm of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log2(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HyperbolicSine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic sine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.sinh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HyperbolicCosine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic cosine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.cosh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HyperbolicTangent:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic tangent of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.tanh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseSine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse sine (arcsin) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.asin(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseCosine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse cosine (arccos) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.acos(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseTangent:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse tangent (arctan) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.atan(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseHyperbolicSine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic sine (arcsinh) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.asinh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseHyperbolicCosine:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic cosine (arccosh) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.acosh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InverseHyperbolicTangent:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic tangent (arctanh) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.atanh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Exponential:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the exponential (e^x) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.exp(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class NaturalLogarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the natural logarithm (ln) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Base10Logarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the base-10 logarithm (log10) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log10(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Base2Logarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the base-2 logarithm (log2) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log2(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmBaseE:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm base e (ln) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmBase10:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm base 10 (log10) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log10(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmBase2:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm base 2 (log2) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.log2(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmBaseN:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm base n (logn) of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        base = node_inputs.get("required_inputs", {}).get("base", {}).get("values", 2)
        try:
            import math

            result = math.log(number, base)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class RationalApproximation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the rational approximation of a real number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
            "max_denominator": {
                "kind": "number",
                "name": "max_denominator",
                "widget": {
                    "kind": "number",
                    "name": "max_denominator",
                    "default": 1000,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        max_denominator = (
            node_inputs.get("required_inputs", {})
            .get("max_denominator", {})
            .get("values", 1000)
        )
        try:
            from fractions import Fraction

            rational = Fraction(number).limit_denominator(max_denominator)
            return {"result": [rational.numerator, rational.denominator]}
        except Exception as e:
            return {"error": str(e)}


class ComplexConjugate:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the complex conjugate of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 0)
        try:
            complex_num = complex(real, imag)
            conjugate = complex_num.conjugate()
            return {"result": [conjugate.real, conjugate.imag]}
        except Exception as e:
            return {"error": str(e)}


class PolarToCartesian:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts polar coordinates to Cartesian coordinates."

    INPUT = {
        "required_inputs": {
            "r": {
                "kind": "number",
                "name": "r",
                "widget": {"kind": "number", "name": "r", "default": 1},
            },
            "theta": {
                "kind": "number",
                "name": "theta",
                "widget": {"kind": "number", "name": "theta", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        r = node_inputs.get("required_inputs", {}).get("r", {}).get("values", 1)
        theta = node_inputs.get("required_inputs", {}).get("theta", {}).get("values", 0)
        try:
            import math

            x = r * math.cos(theta)
            y = r * math.sin(theta)
            return {"result": [x, y]}
        except Exception as e:
            return {"error": str(e)}


class CartesianToPolar:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts Cartesian coordinates to polar coordinates."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0},
            },
            "y": {
                "kind": "number",
                "name": "y",
                "widget": {"kind": "number", "name": "y", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0)
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", 0)
        try:
            import math

            r = math.sqrt(x**2 + y**2)
            theta = math.atan2(y, x)
            return {"result": [r, theta]}
        except Exception as e:
            return {"error": str(e)}


class MatrixDeterminant:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the determinant of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 0], [0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 0], [0, 1]])
        )
        try:
            import numpy as np

            det = np.linalg.det(matrix)
            return {"result": det}
        except Exception as e:
            return {"error": str(e)}


class MatrixInverse:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 0], [0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 0], [0, 1]])
        )
        try:
            import numpy as np

            inv = np.linalg.inv(matrix)
            return {"result": inv.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixTranspose:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the transpose of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            transpose = np.array(matrix).T
            return {"result": transpose.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Eigenvalues:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the eigenvalues of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 0], [0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 0], [0, 1]])
        )
        try:
            import numpy as np

            eigenvalues = np.linalg.eigvals(matrix)
            return {"result": eigenvalues.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Eigenvectors:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the eigenvectors of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 0], [0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 0], [0, 1]])
        )
        try:
            import numpy as np

            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            return {"result": eigenvectors.tolist()}
        except Exception as e:
            return {"error": str(e)}


class FourierTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Fourier transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {"kind": "array", "name": "signal", "default": [0, 1, 0, -1]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [0, 1, 0, -1])
        )
        try:
            import numpy as np

            fft = np.fft.fft(signal)
            return {"result": fft.tolist()}
        except Exception as e:
            return {"error": str(e)}


class InverseFourierTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse Fourier transform of a signal."

    INPUT = {
        "required_inputs": {
            "fft": {
                "kind": "array",
                "name": "fft",
                "widget": {"kind": "array", "name": "fft", "default": [0, 1, 0, -1]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        fft = (
            node_inputs.get("required_inputs", {})
            .get("fft", {})
            .get("values", [0, 1, 0, -1])
        )
        try:
            import numpy as np

            signal = np.fft.ifft(fft)
            return {"result": signal.real.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Cosh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic cosine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.cosh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Sinh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic sine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.sinh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Tanh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperbolic tangent of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.tanh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Arccosh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic cosine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            import math

            result = math.acosh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Arcsinh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic sine of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.asinh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Arctanh:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse hyperbolic tangent of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.atanh(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Log1p:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the natural logarithm of 1 plus a number (log(1 + x))."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.log1p(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Expm1:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes e raised to the power of a number minus 1 (e^x - 1)."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 0)
        )
        try:
            import math

            result = math.expm1(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Hypot:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Euclidean norm, sqrt(x^2 + y^2), for two numbers."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0},
            },
            "y": {
                "kind": "number",
                "name": "y",
                "widget": {"kind": "number", "name": "y", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0)
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", 0)
        try:
            import math

            result = math.hypot(x, y)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DegreesToRadians:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts an angle from degrees to radians."

    INPUT = {
        "required_inputs": {
            "degrees": {
                "kind": "number",
                "name": "degrees",
                "widget": {"kind": "number", "name": "degrees", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        degrees = (
            node_inputs.get("required_inputs", {}).get("degrees", {}).get("values", 0)
        )
        try:
            import math

            result = math.radians(degrees)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class RadiansToDegrees:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts an angle from radians to degrees."

    INPUT = {
        "required_inputs": {
            "radians": {
                "kind": "number",
                "name": "radians",
                "widget": {"kind": "number", "name": "radians", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        radians = (
            node_inputs.get("required_inputs", {}).get("radians", {}).get("values", 0)
        )
        try:
            import math

            result = math.degrees(radians)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogSumExp:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the log of the sum of exponentials of input elements, useful for numerical stability."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.log(np.sum(np.exp(numbers)))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class RootMeanSquare:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the root mean square of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.sqrt(np.mean(np.array(numbers) ** 2))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class HarmonicSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the harmonic sum of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            result = sum(1 / x for x in numbers if x != 0)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GeometricSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the geometric sum of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.prod(numbers)
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class ArithmeticMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the arithmetic mean of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            result = sum(numbers) / len(numbers) if numbers else 0
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuadraticMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the quadratic mean (or RMS) of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.sqrt(np.mean(np.array(numbers) ** 2))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class WeightedAverage:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the weighted average of a list of numbers with given weights."
    )

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
            "weights": {
                "kind": "array",
                "name": "weights",
                "widget": {"kind": "array", "name": "weights", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        weights = (
            node_inputs.get("required_inputs", {}).get("weights", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.average(numbers, weights=weights)
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class CumulativeSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cumulative sum of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.cumsum(numbers).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CumulativeProduct:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cumulative product of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.cumprod(numbers).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Percentile:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth percentile of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 50},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 50)
        try:
            import numpy as np

            result = np.percentile(numbers, n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InterquartileRange:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the interquartile range of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            q75, q25 = np.percentile(numbers, [75, 25])
            iqr = q75 - q25
            return {"result": iqr}
        except Exception as e:
            return {"error": str(e)}


class ZScore:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the z-score of a number in a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
            "value": {
                "kind": "number",
                "name": "value",
                "widget": {"kind": "number", "name": "value", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        value = node_inputs.get("required_inputs", {}).get("value", {}).get("values", 0)
        try:
            import numpy as np

            mean = np.mean(numbers)
            std = np.std(numbers)
            z_score = (value - mean) / std
            return {"result": z_score}
        except Exception as e:
            return {"error": str(e)}


class Covariance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the covariance between two lists of numbers."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "array",
                "name": "x",
                "widget": {"kind": "array", "name": "x", "default": []},
            },
            "y": {
                "kind": "array",
                "name": "y",
                "widget": {"kind": "array", "name": "y", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", [])
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", [])
        try:
            import numpy as np

            covariance = np.cov(x, y)[0][1]
            return {"result": covariance}
        except Exception as e:
            return {"error": str(e)}


class CorrelationCoefficient:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the Pearson correlation coefficient between two lists of numbers."
    )

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "array",
                "name": "x",
                "widget": {"kind": "array", "name": "x", "default": []},
            },
            "y": {
                "kind": "array",
                "name": "y",
                "widget": {"kind": "array", "name": "y", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", [])
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", [])
        try:
            import numpy as np

            correlation = np.corrcoef(x, y)[0][1]
            return {"result": correlation}
        except Exception as e:
            return {"error": str(e)}


class Skewness:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the skewness of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import scipy.stats as stats

            skewness = stats.skew(numbers)
            return {"result": skewness}
        except Exception as e:
            return {"error": str(e)}


class Kurtosis:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the kurtosis of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import scipy.stats as stats

            kurtosis = stats.kurtosis(numbers)
            return {"result": kurtosis}
        except Exception as e:
            return {"error": str(e)}


class Entropy:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the entropy of a probability distribution."

    INPUT = {
        "required_inputs": {
            "probabilities": {
                "kind": "array",
                "name": "probabilities",
                "widget": {"kind": "array", "name": "probabilities", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        probabilities = (
            node_inputs.get("required_inputs", {})
            .get("probabilities", {})
            .get("values", [])
        )
        try:
            import scipy.stats as stats

            entropy = stats.entropy(probabilities)
            return {"result": entropy}
        except Exception as e:
            return {"error": str(e)}


class Fibonacci:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Fibonacci number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 0)
        try:

            def fibonacci(n):
                if n <= 1:
                    return n
                else:
                    return fibonacci(n - 1) + fibonacci(n - 2)

            result = fibonacci(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PrimeCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is prime."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 2)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            result = is_prime(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GreatestCommonDivisor:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the greatest common divisor of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)
        try:
            import math

            result = math.gcd(a, b)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LeastCommonMultiple:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the least common multiple of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0)
        try:
            import math

            result = abs(a * b) // math.gcd(a, b)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class BinomialCoefficient:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the binomial coefficient (n choose k)."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 0},
            },
            "k": {
                "kind": "number",
                "name": "k",
                "widget": {"kind": "number", "name": "k", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 0)
        k = node_inputs.get("required_inputs", {}).get("k", {}).get("values", 0)
        try:
            import math

            result = math.comb(n, k)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DecimalToBinary:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a decimal number to its binary representation."

    INPUT = {
        "required_inputs": {
            "decimal": {
                "kind": "number",
                "name": "decimal",
                "widget": {"kind": "number", "name": "decimal", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        decimal = (
            node_inputs.get("required_inputs", {}).get("decimal", {}).get("values", 0)
        )
        try:
            result = bin(decimal)[2:]  # Remove '0b' prefix
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class BinaryToDecimal:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a binary number to its decimal representation."

    INPUT = {
        "required_inputs": {
            "binary": {
                "kind": "string",
                "name": "binary",
                "widget": {"kind": "string", "name": "binary", "default": "0"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        binary = (
            node_inputs.get("required_inputs", {}).get("binary", {}).get("values", "0")
        )
        try:
            result = int(binary, 2)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HexToDecimal:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a hexadecimal number to its decimal representation."

    INPUT = {
        "required_inputs": {
            "hex": {
                "kind": "string",
                "name": "hex",
                "widget": {"kind": "string", "name": "hex", "default": "0"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        hex_value = (
            node_inputs.get("required_inputs", {}).get("hex", {}).get("values", "0")
        )
        try:
            result = int(hex_value, 16)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DecimalToHex:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a decimal number to its hexadecimal representation."

    INPUT = {
        "required_inputs": {
            "decimal": {
                "kind": "number",
                "name": "decimal",
                "widget": {"kind": "number", "name": "decimal", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        decimal = (
            node_inputs.get("required_inputs", {}).get("decimal", {}).get("values", 0)
        )
        try:
            result = hex(decimal)[2:]  # Remove '0x' prefix
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PolarToRectangular:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts polar coordinates to rectangular (Cartesian) coordinates."

    INPUT = {
        "required_inputs": {
            "r": {
                "kind": "number",
                "name": "r",
                "widget": {"kind": "number", "name": "r", "default": 0},
            },
            "theta": {
                "kind": "number",
                "name": "theta",
                "widget": {"kind": "number", "name": "theta", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        r = node_inputs.get("required_inputs", {}).get("r", {}).get("values", 0)
        theta = node_inputs.get("required_inputs", {}).get("theta", {}).get("values", 0)
        try:
            import math

            x = r * math.cos(theta)
            y = r * math.sin(theta)
            return {"result": [x, y]}
        except Exception as e:
            return {"error": str(e)}


class RectangularToPolar:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts rectangular (Cartesian) coordinates to polar coordinates."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0},
            },
            "y": {
                "kind": "number",
                "name": "y",
                "widget": {"kind": "number", "name": "y", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0)
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", 0)
        try:
            import math

            r = math.sqrt(x**2 + y**2)
            theta = math.atan2(y, x)
            return {"result": [r, theta]}
        except Exception as e:
            return {"error": str(e)}


class MatrixAddition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Adds two matrices."

    INPUT = {
        "required_inputs": {
            "matrix1": {
                "kind": "array",
                "name": "matrix1",
                "widget": {"kind": "array", "name": "matrix1", "default": [[]]},
            },
            "matrix2": {
                "kind": "array",
                "name": "matrix2",
                "widget": {"kind": "array", "name": "matrix2", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix1 = (
            node_inputs.get("required_inputs", {})
            .get("matrix1", {})
            .get("values", [[]])
        )
        matrix2 = (
            node_inputs.get("required_inputs", {})
            .get("matrix2", {})
            .get("values", [[]])
        )
        try:
            import numpy as np

            result = np.add(matrix1, matrix2).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MatrixSubtraction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Subtracts two matrices."

    INPUT = {
        "required_inputs": {
            "matrix1": {
                "kind": "array",
                "name": "matrix1",
                "widget": {"kind": "array", "name": "matrix1", "default": [[]]},
            },
            "matrix2": {
                "kind": "array",
                "name": "matrix2",
                "widget": {"kind": "array", "name": "matrix2", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix1 = (
            node_inputs.get("required_inputs", {})
            .get("matrix1", {})
            .get("values", [[]])
        )
        matrix2 = (
            node_inputs.get("required_inputs", {})
            .get("matrix2", {})
            .get("values", [[]])
        )
        try:
            import numpy as np

            result = np.subtract(matrix1, matrix2).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MatrixMultiplication:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Multiplies two matrices."

    INPUT = {
        "required_inputs": {
            "matrix1": {
                "kind": "array",
                "name": "matrix1",
                "widget": {"kind": "array", "name": "matrix1", "default": [[]]},
            },
            "matrix2": {
                "kind": "array",
                "name": "matrix2",
                "widget": {"kind": "array", "name": "matrix2", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix1 = (
            node_inputs.get("required_inputs", {})
            .get("matrix1", {})
            .get("values", [[]])
        )
        matrix2 = (
            node_inputs.get("required_inputs", {})
            .get("matrix2", {})
            .get("values", [[]])
        )
        try:
            import numpy as np

            result = np.matmul(matrix1, matrix2).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MatrixRank:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the rank of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {"kind": "array", "name": "matrix", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {}).get("matrix", {}).get("values", [[]])
        )
        try:
            import numpy as np

            result = np.linalg.matrix_rank(matrix)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CholeskyDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Cholesky decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {"kind": "array", "name": "matrix", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {}).get("matrix", {}).get("values", [[]])
        )
        try:
            import numpy as np

            result = np.linalg.cholesky(matrix).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LUDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the LU decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {"kind": "array", "name": "matrix", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {}).get("matrix", {}).get("values", [[]])
        )
        try:
            from scipy import linalg

            P, L, U = linalg.lu(matrix)
            result = [P.tolist(), L.tolist(), U.tolist()]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QRDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the QR decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {"kind": "array", "name": "matrix", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {}).get("matrix", {}).get("values", [[]])
        )
        try:
            import numpy as np

            Q, R = np.linalg.qr(matrix)
            result = [Q.tolist(), R.tolist()]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SingularValueDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the singular value decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {"kind": "array", "name": "matrix", "default": [[]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {}).get("matrix", {}).get("values", [[]])
        )
        try:
            import numpy as np

            U, s, Vt = np.linalg.svd(matrix)
            result = [U.tolist(), s.tolist(), Vt.tolist()]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ComplexMagnitude:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the magnitude of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 0)
        try:
            result = abs(complex(real, imag))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ComplexPhase:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the phase (angle) of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 0)
        try:
            import cmath

            result = cmath.phase(complex(real, imag))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmicMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithmic mean of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 1},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 1)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1)
        try:
            import math

            if a <= 0 or b <= 0:
                raise ValueError("Inputs must be positive")
            result = (b - a) / (math.log(b) - math.log(a))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ArithmeticGeometricMean:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the arithmetic-geometric mean of two numbers."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 1},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 1)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1)
        try:
            import math

            while abs(a - b) > 1e-15:
                a, b = (a + b) / 2, math.sqrt(a * b)
            return {"result": a}  # or b, they're equal at this point
        except Exception as e:
            return {"error": str(e)}


class HaversineDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the distance between two points on a sphere given their longitudes and latitudes."

    INPUT = {
        "required_inputs": {
            "lat1": {
                "kind": "number",
                "name": "lat1",
                "widget": {"kind": "number", "name": "lat1", "default": 0},
            },
            "lon1": {
                "kind": "number",
                "name": "lon1",
                "widget": {"kind": "number", "name": "lon1", "default": 0},
            },
            "lat2": {
                "kind": "number",
                "name": "lat2",
                "widget": {"kind": "number", "name": "lat2", "default": 0},
            },
            "lon2": {
                "kind": "number",
                "name": "lon2",
                "widget": {"kind": "number", "name": "lon2", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        lat1 = node_inputs.get("required_inputs", {}).get("lat1", {}).get("values", 0)
        lon1 = node_inputs.get("required_inputs", {}).get("lon1", {}).get("values", 0)
        lat2 = node_inputs.get("required_inputs", {}).get("lat2", {}).get("values", 0)
        lon2 = node_inputs.get("required_inputs", {}).get("lon2", {}).get("values", 0)
        try:
            import math

            R = 6371  # Earth's radius in kilometers

            def haversine(lat1, lon1, lat2, lon2):
                lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
                )
                c = 2 * math.asin(math.sqrt(a))
                return R * c

            result = haversine(lat1, lon1, lat2, lon2)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DecimalToOctal:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a decimal number to its octal representation."

    INPUT = {
        "required_inputs": {
            "decimal": {
                "kind": "number",
                "name": "decimal",
                "widget": {"kind": "number", "name": "decimal", "default": 0},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        decimal = (
            node_inputs.get("required_inputs", {}).get("decimal", {}).get("values", 0)
        )
        try:
            result = oct(decimal)[2:]  # [2:] to remove the '0o' prefix
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class OctalToDecimal:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts an octal number to its decimal representation."

    INPUT = {
        "required_inputs": {
            "octal": {
                "kind": "string",
                "name": "octal",
                "widget": {"kind": "string", "name": "octal", "default": "0"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        octal = (
            node_inputs.get("required_inputs", {}).get("octal", {}).get("values", "0")
        )
        try:
            result = int(octal, 8)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ModularExponentiation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the result of raising a number to a power modulo a number."

    INPUT = {
        "required_inputs": {
            "base": {
                "kind": "number",
                "name": "base",
                "widget": {"kind": "number", "name": "base", "default": 2},
            },
            "exponent": {
                "kind": "number",
                "name": "exponent",
                "widget": {"kind": "number", "name": "exponent", "default": 3},
            },
            "modulus": {
                "kind": "number",
                "name": "modulus",
                "widget": {"kind": "number", "name": "modulus", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        base = node_inputs.get("required_inputs", {}).get("base", {}).get("values", 2)
        exponent = (
            node_inputs.get("required_inputs", {}).get("exponent", {}).get("values", 3)
        )
        modulus = (
            node_inputs.get("required_inputs", {}).get("modulus", {}).get("values", 5)
        )
        try:
            result = pow(base, exponent, modulus)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FibonacciSequence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates a list of Fibonacci numbers up to a specified count."

    INPUT = {
        "required_inputs": {
            "count": {
                "kind": "number",
                "name": "count",
                "widget": {"kind": "number", "name": "count", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        count = (
            node_inputs.get("required_inputs", {}).get("count", {}).get("values", 10)
        )
        try:

            def fibonacci(n):
                a, b = 0, 1
                for _ in range(n):
                    yield a
                    a, b = b, a + b

            result = list(fibonacci(count))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PrimeFactorization:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the prime factorization of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def prime_factors(n):
                factors = []
                d = 2
                while n > 1:
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                    d += 1
                    if d * d > n:
                        if n > 1:
                            factors.append(n)
                        break
                return factors

            result = prime_factors(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CumulativeMax:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cumulative maximum of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.maximum.accumulate(numbers).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CumulativeMin:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cumulative minimum of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import numpy as np

            result = np.minimum.accumulate(numbers).tolist()
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DecimalToRoman:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a decimal number to its Roman numeral representation."

    INPUT = {
        "required_inputs": {
            "decimal": {
                "kind": "number",
                "name": "decimal",
                "widget": {"kind": "number", "name": "decimal", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "string",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        decimal = (
            node_inputs.get("required_inputs", {}).get("decimal", {}).get("values", 1)
        )
        try:

            def decimal_to_roman(num):
                val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
                syb = [
                    "M",
                    "CM",
                    "D",
                    "CD",
                    "C",
                    "XC",
                    "L",
                    "XL",
                    "X",
                    "IX",
                    "V",
                    "IV",
                    "I",
                ]
                roman_num = ""
                i = 0
                while num > 0:
                    for _ in range(num // val[i]):
                        roman_num += syb[i]
                        num -= val[i]
                    i += 1
                return roman_num

            result = decimal_to_roman(decimal)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class RomanToDecimal:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts a Roman numeral to its decimal representation."

    INPUT = {
        "required_inputs": {
            "roman": {
                "kind": "string",
                "name": "roman",
                "widget": {"kind": "string", "name": "roman", "default": "I"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        roman = (
            node_inputs.get("required_inputs", {}).get("roman", {}).get("values", "I")
        )
        try:

            def roman_to_decimal(s):
                roman_values = {
                    "I": 1,
                    "V": 5,
                    "X": 10,
                    "L": 50,
                    "C": 100,
                    "D": 500,
                    "M": 1000,
                }
                total = 0
                prev_value = 0
                for char in reversed(s):
                    current_value = roman_values[char]
                    if current_value >= prev_value:
                        total += current_value
                    else:
                        total -= current_value
                    prev_value = current_value
                return total

            result = roman_to_decimal(roman)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GreatestPrimeFactor:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the greatest prime factor of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def greatest_prime_factor(n):
                largest_factor = 1
                i = 2
                while i * i <= n:
                    if n % i:
                        i += 1
                    else:
                        n //= i
                        largest_factor = i
                if n > 1:
                    largest_factor = n
                return largest_factor

            result = greatest_prime_factor(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LeastPrimeFactor:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the least prime factor of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def least_prime_factor(n):
                if n <= 1:
                    return n
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return i
                return n

            result = least_prime_factor(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SumOfDivisors:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of all divisors of a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def sum_of_divisors(n):
                return sum(i for i in range(1, n + 1) if n % i == 0)

            result = sum_of_divisors(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PerfectSquareCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a perfect square."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 16},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 16)
        )
        try:
            import math

            result = math.isqrt(number) ** 2 == number
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PerfectCubeCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a perfect cube."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 27},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 27)
        )
        try:
            result = round(number ** (1 / 3)) ** 3 == number
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class IsEven:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is even."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 2)
        )
        try:
            result = number % 2 == 0
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class IsOdd:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is odd."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 1},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 1)
        )
        try:
            result = number % 2 != 0
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class IsPrime:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a prime number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 2)
        )
        try:
            if number < 2:
                return {"result": False}
            for i in range(2, int(number**0.5) + 1):
                if number % i == 0:
                    return {"result": False}
            return {"result": True}
        except Exception as e:
            return {"error": str(e)}


class NextPrime:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the next prime number greater than a given number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 2)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            next_num = number + 1
            while not is_prime(next_num):
                next_num += 1
            return {"result": next_num}
        except Exception as e:
            return {"error": str(e)}


class PreviousPrime:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the previous prime number less than a given number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 3},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 3)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            prev_num = number - 1
            while prev_num > 1 and not is_prime(prev_num):
                prev_num -= 1
            return {"result": prev_num if prev_num > 1 else None}
        except Exception as e:
            return {"error": str(e)}


class LCMArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the least common multiple of an array of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import math
            from functools import reduce

            def lcm(a, b):
                return abs(a * b) // math.gcd(a, b)

            result = reduce(lcm, numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GCDArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the greatest common divisor of an array of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import math
            from functools import reduce

            result = reduce(math.gcd, numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FactorialArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the factorial for each number in an array."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import math

            result = [math.factorial(n) for n in numbers]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PrimeFactorsList:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Returns a list of prime factors for a given number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def prime_factors(n):
                factors = []
                d = 2
                while n > 1:
                    while n % d == 0:
                        factors.append(d)
                        n //= d
                    d += 1
                    if d * d > n:
                        if n > 1:
                            factors.append(n)
                        break
                return factors

            result = prime_factors(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class IsPerfectNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a perfect number (equal to the sum of its proper divisors)."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 6},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 6)
        )
        try:

            def sum_of_proper_divisors(n):
                return sum(i for i in range(1, n) if n % i == 0)

            result = sum_of_proper_divisors(number) == number
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class IsArmstrongNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is an Armstrong number (narcissistic number)."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 153},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 153)
        )
        try:
            num_str = str(number)
            power = len(num_str)
            result = sum(int(digit) ** power for digit in num_str) == number
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GreatestCommonDivisorArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the greatest common divisor of multiple numbers in an array."
    )

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import math

            result = math.gcd(*numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LeastCommonMultipleArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the least common multiple of multiple numbers in an array."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            import math
            from functools import reduce

            def lcm(a, b):
                return abs(a * b) // math.gcd(a, b)

            result = reduce(lcm, numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SumOfSquares:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of squares of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            result = sum(x**2 for x in numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ProductOfArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the product of all elements in an array."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": []},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {}).get("numbers", {}).get("values", [])
        )
        try:
            from functools import reduce
            import operator

            result = reduce(operator.mul, numbers, 1)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ArithmeticProgressionSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of an arithmetic progression given the first term, common difference, and number of terms."

    INPUT = {
        "required_inputs": {
            "first_term": {
                "kind": "number",
                "name": "first_term",
                "widget": {"kind": "number", "name": "first_term", "default": 1},
            },
            "common_difference": {
                "kind": "number",
                "name": "common_difference",
                "widget": {"kind": "number", "name": "common_difference", "default": 1},
            },
            "num_terms": {
                "kind": "number",
                "name": "num_terms",
                "widget": {"kind": "number", "name": "num_terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = (
            node_inputs.get("required_inputs", {})
            .get("first_term", {})
            .get("values", 1)
        )
        d = (
            node_inputs.get("required_inputs", {})
            .get("common_difference", {})
            .get("values", 1)
        )
        n = (
            node_inputs.get("required_inputs", {})
            .get("num_terms", {})
            .get("values", 10)
        )
        try:
            result = (n / 2) * (2 * a + (n - 1) * d)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GeometricProgressionSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of a geometric progression given the first term, common ratio, and number of terms."

    INPUT = {
        "required_inputs": {
            "first_term": {
                "kind": "number",
                "name": "first_term",
                "widget": {"kind": "number", "name": "first_term", "default": 1},
            },
            "common_ratio": {
                "kind": "number",
                "name": "common_ratio",
                "widget": {"kind": "number", "name": "common_ratio", "default": 2},
            },
            "num_terms": {
                "kind": "number",
                "name": "num_terms",
                "widget": {"kind": "number", "name": "num_terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = (
            node_inputs.get("required_inputs", {})
            .get("first_term", {})
            .get("values", 1)
        )
        r = (
            node_inputs.get("required_inputs", {})
            .get("common_ratio", {})
            .get("values", 2)
        )
        n = (
            node_inputs.get("required_inputs", {})
            .get("num_terms", {})
            .get("values", 10)
        )
        try:
            if r == 1:
                result = a * n
            else:
                result = a * (1 - r**n) / (1 - r)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HarmonicProgressionSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of a harmonic progression given the first term and number of terms."

    INPUT = {
        "required_inputs": {
            "first_term": {
                "kind": "number",
                "name": "first_term",
                "widget": {"kind": "number", "name": "first_term", "default": 1},
            },
            "num_terms": {
                "kind": "number",
                "name": "num_terms",
                "widget": {"kind": "number", "name": "num_terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = (
            node_inputs.get("required_inputs", {})
            .get("first_term", {})
            .get("values", 1)
        )
        n = (
            node_inputs.get("required_inputs", {})
            .get("num_terms", {})
            .get("values", 10)
        )
        try:
            result = sum(1 / (a + i) for i in range(n))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CatalanNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Catalan number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            import math

            result = math.comb(2 * n, n) // (n + 1)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class BellNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Bell number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:

            def bell(n):
                bell_numbers = [1]
                import math

                for i in range(1, n + 1):
                    next_bell = sum(
                        math.comb(i - 1, k) * bell_numbers[k] for k in range(i)
                    )
                    bell_numbers.append(next_bell)
                return bell_numbers[n]

            result = bell(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StirlingNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Stirling number of the second kind for given n and k."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
            "k": {
                "kind": "number",
                "name": "k",
                "widget": {"kind": "number", "name": "k", "default": 3},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        k = node_inputs.get("required_inputs", {}).get("k", {}).get("values", 3)
        try:

            def stirling2(n, k):
                if k == 1 or k == n:
                    return 1
                if k > n or k < 1:
                    return 0
                return k * stirling2(n - 1, k) + stirling2(n - 1, k - 1)

            result = stirling2(n, k)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FibonacciNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Fibonacci number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def fibonacci(n):
                if n <= 1:
                    return n
                return fibonacci(n - 1) + fibonacci(n - 2)

            result = fibonacci(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LucasNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Lucas number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def lucas(n):
                if n == 0:
                    return 2
                if n == 1:
                    return 1
                return lucas(n - 1) + lucas(n - 2)

            result = lucas(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class TriangularNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth triangular number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            result = (n * (n + 1)) // 2
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PentagonalNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth pentagonal number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            result = (n * (3 * n - 1)) // 2
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HexagonalNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth hexagonal number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            result = n * (2 * n - 1)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PerfectNumberCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a perfect number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 28},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 28)
        )
        try:

            def sum_of_proper_divisors(n):
                return sum(i for i in range(1, n) if n % i == 0)

            result = sum_of_proper_divisors(number) == number
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class AmicableNumbersCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if two numbers are amicable."

    INPUT = {
        "required_inputs": {
            "number1": {
                "kind": "number",
                "name": "number1",
                "widget": {"kind": "number", "name": "number1", "default": 220},
            },
            "number2": {
                "kind": "number",
                "name": "number2",
                "widget": {"kind": "number", "name": "number2", "default": 284},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number1 = (
            node_inputs.get("required_inputs", {}).get("number1", {}).get("values", 220)
        )
        number2 = (
            node_inputs.get("required_inputs", {}).get("number2", {}).get("values", 284)
        )
        try:

            def sum_of_proper_divisors(n):
                return sum(i for i in range(1, n) if n % i == 0)

            result = (
                sum_of_proper_divisors(number1) == number2
                and sum_of_proper_divisors(number2) == number1
            )
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MersennePrimeCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a Mersenne prime."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 31},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 31)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            def is_mersenne_prime(p):
                mersenne = 2**p - 1
                return is_prime(mersenne)

            result = is_mersenne_prime(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class EulerTotientFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Euler's totient function for a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 10)
        )
        try:

            def gcd(a, b):
                while b:
                    a, b = b, a % b
                return a

            def euler_totient(n):
                result = n
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        while n % i == 0:
                            n //= i
                        result *= 1 - 1 / i
                if n > 1:
                    result *= 1 - 1 / n
                return int(result)

            result = euler_totient(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MobiusFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Möbius function for a number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 10)
        )
        try:

            def mobius(n):
                if n == 1:
                    return 1
                p = 0
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        if n % (i * i) == 0:
                            return 0
                        p += 1
                        n //= i
                        while n % i == 0:
                            n //= i
                if n > 1:
                    p += 1
                return (-1) ** p if p > 0 else 1

            result = mobius(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class AckermannFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Ackermann function for given inputs."

    INPUT = {
        "required_inputs": {
            "m": {
                "kind": "number",
                "name": "m",
                "widget": {"kind": "number", "name": "m", "default": 3},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        m = node_inputs.get("required_inputs", {}).get("m", {}).get("values", 3)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 2)
        try:

            def ackermann(m, n):
                if m == 0:
                    return n + 1
                elif n == 0:
                    return ackermann(m - 1, 1)
                else:
                    return ackermann(m - 1, ackermann(m, n - 1))

            result = ackermann(m, n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CollatzSequence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates the Collatz sequence for a given starting number."

    INPUT = {
        "required_inputs": {
            "start": {
                "kind": "number",
                "name": "start",
                "widget": {"kind": "number", "name": "start", "default": 13},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        start = (
            node_inputs.get("required_inputs", {}).get("start", {}).get("values", 13)
        )
        try:

            def collatz(n):
                sequence = [n]
                while n != 1:
                    if n % 2 == 0:
                        n = n // 2
                    else:
                        n = 3 * n + 1
                    sequence.append(n)
                return sequence

            result = collatz(start)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PascalTriangleRow:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes a specific row of Pascal's triangle."

    INPUT = {
        "required_inputs": {
            "row": {
                "kind": "number",
                "name": "row",
                "widget": {"kind": "number", "name": "row", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        row = node_inputs.get("required_inputs", {}).get("row", {}).get("values", 5)
        try:

            def pascal_row(n):
                row = [1]
                for k in range(1, n + 1):
                    row.append(row[k - 1] * (n - k + 1) // k)
                return row

            result = pascal_row(row)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FermatNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Fermat number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 4},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 4)
        try:
            result = 2 ** (2**n) + 1
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CarmichaelFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Carmichael function for a given number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 12},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 12)
        )
        try:

            def gcd(a, b):
                while b:
                    a, b = b, a % b
                return a

            def lcm(a, b):
                return a * b // gcd(a, b)

            def carmichael(n):
                if n < 1:
                    return 0
                if n == 1:
                    return 1

                factors = []
                d = 2
                while d * d <= n:
                    if n % d == 0:
                        factors.append(d)
                        n //= d
                    else:
                        d += 1
                if n > 1:
                    factors.append(n)

                result = 1
                for p in set(factors):
                    if p == 2:
                        e = factors.count(2)
                        if e > 2:
                            result = lcm(result, 2 ** (e - 2))
                        else:
                            result = lcm(result, 1)
                    else:
                        e = factors.count(p)
                        result = lcm(result, (p - 1) * p ** (e - 1))

                return result

            result = carmichael(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SophieGermainPrimeCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a Sophie Germain prime."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 11},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 11)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            result = is_prime(number) and is_prime(2 * number + 1)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class KaprekarNumberCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a Kaprekar number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 9},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 9)
        )
        try:

            def is_kaprekar(n):
                if n == 1:
                    return True
                square = n * n
                str_square = str(square)
                for i in range(1, len(str_square)):
                    left = int(str_square[:i]) if str_square[:i] else 0
                    right = int(str_square[i:])
                    if right > 0 and left + right == n:
                        return True
                return False

            result = is_kaprekar(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class AutomorphicNumberCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is an automorphic number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 25},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 25)
        )
        try:
            square = number * number
            str_number = str(number)
            str_square = str(square)
            result = str_square.endswith(str_number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HarshadNumberCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a Harshad (or Niven) number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 18},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 18)
        )
        try:
            digit_sum = sum(int(digit) for digit in str(number))
            result = number % digit_sum == 0
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HappyNumberCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if a number is a happy number."

    INPUT = {
        "required_inputs": {
            "number": {
                "kind": "number",
                "name": "number",
                "widget": {"kind": "number", "name": "number", "default": 7},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        number = (
            node_inputs.get("required_inputs", {}).get("number", {}).get("values", 7)
        )
        try:

            def sum_of_squares(n):
                return sum(int(digit) ** 2 for digit in str(n))

            def is_happy(n):
                seen = set()
                while n != 1:
                    n = sum_of_squares(n)
                    if n in seen:
                        return False
                    seen.add(n)
                return True

            result = is_happy(number)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class EulerNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the value of Euler's number (e) to a specified precision."

    INPUT = {
        "required_inputs": {
            "precision": {
                "kind": "number",
                "name": "precision",
                "widget": {"kind": "number", "name": "precision", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        precision = (
            node_inputs.get("required_inputs", {})
            .get("precision", {})
            .get("values", 10)
        )
        try:
            import math

            result = round(math.e, precision)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GoldenRatio:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the value of the golden ratio to a specified precision."

    INPUT = {
        "required_inputs": {
            "precision": {
                "kind": "number",
                "name": "precision",
                "widget": {"kind": "number", "name": "precision", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        precision = (
            node_inputs.get("required_inputs", {})
            .get("precision", {})
            .get("values", 10)
        )
        try:
            import math

            result = round((1 + math.sqrt(5)) / 2, precision)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CatalanConstant:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the value of the Catalan constant to a specified precision."

    INPUT = {
        "required_inputs": {
            "precision": {
                "kind": "number",
                "name": "precision",
                "widget": {"kind": "number", "name": "precision", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        precision = (
            node_inputs.get("required_inputs", {})
            .get("precision", {})
            .get("values", 10)
        )
        try:
            result = round(
                sum((-1) ** n / (2 * n + 1) ** 2 for n in range(10000)), precision
            )
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class BernoulliNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Bernoulli number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            from fractions import Fraction

            def bernoulli(n):
                A = [0] * (n + 1)
                for m in range(n + 1):
                    A[m] = Fraction(1, m + 1)
                    for j in range(m, 0, -1):
                        A[j - 1] = j * (A[j - 1] - A[j])
                return A[0]

            result = float(bernoulli(n))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class EulerNumberSequence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates a sequence of Euler numbers."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:

            def euler_numbers(n):
                E = [1]
                for m in range(1, n + 1):
                    E.append(0)
                    for k in range(m):
                        E[m] += (-1) ** k * (m + 1 - k) ** m * E[k] / (k + 1)
                return E

            result = euler_numbers(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PartitionFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the number of ways to partition a number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def partition(n):
                p = [0] * (n + 1)
                p[0] = 1
                for i in range(1, n + 1):
                    k = 1
                    while (k * (3 * k - 1)) // 2 <= i:
                        p[i] += (-1) ** (k - 1) * p[i - (k * (3 * k - 1)) // 2]
                        if k > 0:
                            p[i] += (-1) ** (k - 1) * p[i - (k * (3 * k + 1)) // 2]
                        k += 1
                return p[n]

            result = partition(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class RamanujanTauFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Ramanujan tau function for a given number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def ramanujan_tau(n):
                if n == 1:
                    return -24
                if n == 2:
                    return 252
                if n == 3:
                    return -1472
                if n == 4:
                    return 4830
                if n == 5:
                    return -6048
                # For larger n, we would need to implement more complex algorithms
                return 0  # Placeholder for larger n

            result = ramanujan_tau(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DedekindEtaFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Dedekind eta function for a given complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 0.0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 1.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 0.0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 1.0)
        try:
            import cmath

            def dedekind_eta(tau):
                q = cmath.exp(2j * cmath.pi * tau)
                eta = q ** (1 / 24)
                for n in range(1, 100):  # Truncate the infinite product
                    eta *= 1 - q**n
                return eta

            tau = complex(real, imag)
            result = dedekind_eta(tau)
            return {"result": [result.real, result.imag]}
        except Exception as e:
            return {"error": str(e)}


class LiouvilleFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Liouville function for a given number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def liouville(n):
                if n == 1:
                    return 1
                factors = 0
                for i in range(2, int(n**0.5) + 1):
                    while n % i == 0:
                        factors += 1
                        n //= i
                if n > 1:
                    factors += 1
                return -1 if factors % 2 else 1

            result = liouville(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class RiemannZetaFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Riemann zeta function for a given complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 2.0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 2.0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 0.0)
        try:

            def riemann_zeta(s, terms=1000):
                zeta = 0
                for n in range(1, terms + 1):
                    zeta += 1 / n**s
                return zeta

            s = complex(real, imag)
            result = riemann_zeta(s)
            return {"result": [result.real, result.imag]}
        except Exception as e:
            return {"error": str(e)}


class BinetFormula:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Fibonacci number using Binet's formula."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:
            import math

            phi = (1 + math.sqrt(5)) / 2
            result = round((phi**n - (-1 / phi) ** n) / math.sqrt(5))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PellNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth Pell number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        try:

            def pell(n):
                if n == 0:
                    return 0
                elif n == 1:
                    return 1
                else:
                    a, b = 0, 1
                    for _ in range(2, n + 1):
                        a, b = b, 2 * b + a
                    return b

            result = pell(n)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Superfactorial:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the superfactorial of a number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            import math

            result = 1
            for i in range(1, n + 1):
                result *= math.factorial(i)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Hyperfactorial:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the hyperfactorial of a number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 5)
        try:
            result = 1
            for i in range(1, n + 1):
                result *= i**i
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class DoubleFactorial:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the double factorial of a number."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 7},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 7)
        try:
            result = 1
            for i in range(n, 0, -2):
                result *= i
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class CoprimeCheck:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Checks if two numbers are coprime."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 15},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 28},
            },
        },
    }

    OUTPUT = {
        "kind": "boolean",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 15)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 28)
        try:
            import math

            result = math.gcd(a, b) == 1
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class EulerMascheroniConstant:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Euler-Mascheroni constant to a specified precision."

    INPUT = {
        "required_inputs": {
            "precision": {
                "kind": "number",
                "name": "precision",
                "widget": {"kind": "number", "name": "precision", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        precision = (
            node_inputs.get("required_inputs", {})
            .get("precision", {})
            .get("values", 10)
        )
        try:
            euler_mascheroni = 0.57721566490153286060651209008240243104215933593992
            result = round(euler_mascheroni, precision)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ApérysConstant:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes Apéry's constant to a specified precision."

    INPUT = {
        "required_inputs": {
            "precision": {
                "kind": "number",
                "name": "precision",
                "widget": {"kind": "number", "name": "precision", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        precision = (
            node_inputs.get("required_inputs", {})
            .get("precision", {})
            .get("values", 10)
        )
        try:
            apery_constant = (
                1.2020569031595942853997381615114499907649862923404988817922
            )
            result = round(apery_constant, precision)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ConwaySequence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates the Conway sequence (look-and-say sequence) for a given number of terms."

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 5)
        try:

            def next_term(s):
                result = []
                i, j = 0, 0
                while i < len(s):
                    while j < len(s) and s[j] == s[i]:
                        j += 1
                    result.append(str(j - i))
                    result.append(s[i])
                    i = j
                return "".join(result)

            sequence = ["1"]
            for _ in range(terms - 1):
                sequence.append(next_term(sequence[-1]))

            return {"result": sequence}
        except Exception as e:
            return {"error": str(e)}


class SylvesterSequence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates the Sylvester sequence for a given number of terms."

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 5)
        try:
            sequence = [2]
            for _ in range(terms - 1):
                next_term = sequence[-1] * (sequence[-1] - 1) + 1
                sequence.append(next_term)
            return {"result": sequence}
        except Exception as e:
            return {"error": str(e)}


class FibonacciSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates the Fibonacci series up to a specified number of terms."

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = (
            node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 10)
        )
        try:

            def fibonacci():
                a, b = 0, 1
                while True:
                    yield a
                    a, b = b, a + b

            fib = fibonacci()
            result = [next(fib) for _ in range(terms)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LucasSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates the Lucas series up to a specified number of terms."

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = (
            node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 10)
        )
        try:

            def lucas():
                a, b = 2, 1
                while True:
                    yield a
                    a, b = b, a + b

            luc = lucas()
            result = [next(luc) for _ in range(terms)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class TriangularSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Generates the series of triangular numbers up to a specified number of terms."
    )

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = (
            node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 10)
        )
        try:
            result = [n * (n + 1) // 2 for n in range(1, terms + 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PentagonalSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Generates the series of pentagonal numbers up to a specified number of terms."
    )

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = (
            node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 10)
        )
        try:
            result = [n * (3 * n - 1) // 2 for n in range(1, terms + 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HexagonalSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Generates the series of hexagonal numbers up to a specified number of terms."
    )

    INPUT = {
        "required_inputs": {
            "terms": {
                "kind": "number",
                "name": "terms",
                "widget": {"kind": "number", "name": "terms", "default": 10},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        terms = (
            node_inputs.get("required_inputs", {}).get("terms", {}).get("values", 10)
        )
        try:
            result = [n * (2 * n - 1) for n in range(1, terms + 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class PerfectNumberSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates a series of perfect numbers up to a specified limit."

    INPUT = {
        "required_inputs": {
            "limit": {
                "kind": "number",
                "name": "limit",
                "widget": {"kind": "number", "name": "limit", "default": 10000},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        limit = (
            node_inputs.get("required_inputs", {}).get("limit", {}).get("values", 10000)
        )
        try:

            def is_perfect(n):
                return sum(i for i in range(1, n) if n % i == 0) == n

            result = [n for n in range(2, limit + 1) if is_perfect(n)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class AmicablePairs:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds amicable number pairs up to a specified limit."

    INPUT = {
        "required_inputs": {
            "limit": {
                "kind": "number",
                "name": "limit",
                "widget": {"kind": "number", "name": "limit", "default": 10000},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        limit = (
            node_inputs.get("required_inputs", {}).get("limit", {}).get("values", 10000)
        )
        try:

            def sum_of_divisors(n):
                return sum(i for i in range(1, n) if n % i == 0)

            result = []
            for a in range(2, limit):
                b = sum_of_divisors(a)
                if a < b <= limit and sum_of_divisors(b) == a:
                    result.append((a, b))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MersennePrimes:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates Mersenne primes up to a specified limit."

    INPUT = {
        "required_inputs": {
            "limit": {
                "kind": "number",
                "name": "limit",
                "widget": {"kind": "number", "name": "limit", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        limit = (
            node_inputs.get("required_inputs", {}).get("limit", {}).get("values", 100)
        )
        try:

            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True

            result = [2**p - 1 for p in range(2, limit) if is_prime(2**p - 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class EulerTotientSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Euler's totient function for a series of numbers."

    INPUT = {
        "required_inputs": {
            "limit": {
                "kind": "number",
                "name": "limit",
                "widget": {"kind": "number", "name": "limit", "default": 20},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        limit = (
            node_inputs.get("required_inputs", {}).get("limit", {}).get("values", 20)
        )
        try:

            def euler_totient(n):
                result = n
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        while n % i == 0:
                            n //= i
                        result *= 1 - 1 / i
                if n > 1:
                    result *= 1 - 1 / n
                return int(result)

            result = [euler_totient(n) for n in range(1, limit + 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MobiusSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Möbius function for a series of numbers."

    INPUT = {
        "required_inputs": {
            "limit": {
                "kind": "number",
                "name": "limit",
                "widget": {"kind": "number", "name": "limit", "default": 20},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        limit = (
            node_inputs.get("required_inputs", {}).get("limit", {}).get("values", 20)
        )
        try:

            def mobius(n):
                if n == 1:
                    return 1
                p = 0
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        if n % (i * i) == 0:
                            return 0
                        p += 1
                        n //= i
                        while n % i == 0:
                            n //= i
                if n > 1:
                    p += 1
                return (-1) ** p if p > 0 else 1

            result = [mobius(n) for n in range(1, limit + 1)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SumOfCubes:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the sum of cubes of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {"kind": "array", "name": "numbers", "default": [1, 2, 3]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {})
            .get("numbers", {})
            .get("values", [1, 2, 3])
        )
        try:
            result = sum(num**3 for num in numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ArithmeticMeanArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the arithmetic mean for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:
            result = [sum(sub_array) / len(sub_array) for sub_array in arrays]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GeometricMeanArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the geometric mean for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:
            import math

            result = [
                math.prod(sub_array) ** (1 / len(sub_array)) for sub_array in arrays
            ]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class HarmonicMeanArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the harmonic mean for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:
            result = [
                len(sub_array) / sum(1 / x for x in sub_array) for sub_array in arrays
            ]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class MedianArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the median for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:

            def median(arr):
                sorted_arr = sorted(arr)
                n = len(sorted_arr)
                if n % 2 == 0:
                    return (sorted_arr[n // 2 - 1] + sorted_arr[n // 2]) / 2
                else:
                    return sorted_arr[n // 2]

            result = [median(sub_array) for sub_array in arrays]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ModeArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the mode for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 2, 3], [4, 5, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 2, 3], [4, 5, 5, 6]])
        )
        try:
            from statistics import mode

            result = [mode(sub_array) for sub_array in arrays]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class StandardDeviationArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the standard deviation for each sub-array in a list of arrays."
    )

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:
            import statistics

            result = [statistics.stdev(sub_array) for sub_array in arrays]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class VarianceArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the variance for each sub-array in a list of arrays."

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3], [4, 5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3], [4, 5, 6]])
        )
        try:
            import statistics

            result = [statistics.variance(sub_array) for sub_array in arrays]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class Range:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the range (max - min) of a list of numbers."

    INPUT = {
        "required_inputs": {
            "numbers": {
                "kind": "array",
                "name": "numbers",
                "widget": {
                    "kind": "array",
                    "name": "numbers",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        numbers = (
            node_inputs.get("required_inputs", {})
            .get("numbers", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            result = max(numbers) - min(numbers)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class InterquartileRangeArray:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the interquartile range for each sub-array in a list of arrays."
    )

    INPUT = {
        "required_inputs": {
            "arrays": {
                "kind": "array",
                "name": "arrays",
                "widget": {
                    "kind": "array",
                    "name": "arrays",
                    "default": [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        arrays = (
            node_inputs.get("required_inputs", {})
            .get("arrays", {})
            .get("values", [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]])
        )
        try:
            import numpy as np

            result = [
                np.percentile(sub_array, 75) - np.percentile(sub_array, 25)
                for sub_array in arrays
            ]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class LogarithmicSpiral:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes points on a logarithmic spiral given parameters."

    INPUT = {
        "required_inputs": {
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 1.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 0.1},
            },
            "t_range": {
                "kind": "array",
                "name": "t_range",
                "widget": {"kind": "array", "name": "t_range", "default": [0, 10, 100]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 1.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 0.1)
        t_range = (
            node_inputs.get("required_inputs", {})
            .get("t_range", {})
            .get("values", [0, 10, 100])
        )
        try:
            import numpy as np

            t = np.linspace(t_range[0], t_range[1], int(t_range[2]))
            r = a * np.exp(b * t)
            x = r * np.cos(t)
            y = r * np.sin(t)
            result = list(zip(x.tolist(), y.tolist()))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FibonacciSpiral:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Generates points on a Fibonacci spiral."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 10},
            },
            "scale": {
                "kind": "number",
                "name": "scale",
                "widget": {"kind": "number", "name": "scale", "default": 1.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 10)
        scale = (
            node_inputs.get("required_inputs", {}).get("scale", {}).get("values", 1.0)
        )
        try:
            import math

            phi = (1 + math.sqrt(5)) / 2
            result = []
            for i in range(n):
                theta = 2 * math.pi * i / phi
                r = math.sqrt(i) * scale
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                result.append((x, y))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class GoldenSpiral:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes points on a golden spiral."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 100},
            },
            "scale": {
                "kind": "number",
                "name": "scale",
                "widget": {"kind": "number", "name": "scale", "default": 1.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 100)
        scale = (
            node_inputs.get("required_inputs", {}).get("scale", {}).get("values", 1.0)
        )
        try:
            import math

            golden_ratio = (1 + math.sqrt(5)) / 2
            result = []
            for i in range(n):
                theta = i * 2 * math.pi / golden_ratio
                r = math.sqrt(i) * scale
                x = r * math.cos(theta)
                y = r * math.sin(theta)
                result.append((x, y))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class ComplexExponential:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the exponential of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 0.0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 1.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 0.0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 1.0)
        try:
            import cmath

            z = complex(real, imag)
            result = cmath.exp(z)
            return {"result": [result.real, result.imag]}
        except Exception as e:
            return {"error": str(e)}


class ComplexLogarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 1.0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 1.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 1.0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 1.0)
        try:
            import cmath

            z = complex(real, imag)
            result = cmath.log(z)
            return {"result": [result.real, result.imag]}
        except Exception as e:
            return {"error": str(e)}


class ComplexPower:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Raises a complex number to a given power."

    INPUT = {
        "required_inputs": {
            "base_real": {
                "kind": "number",
                "name": "base_real",
                "widget": {"kind": "number", "name": "base_real", "default": 1.0},
            },
            "base_imag": {
                "kind": "number",
                "name": "base_imag",
                "widget": {"kind": "number", "name": "base_imag", "default": 1.0},
            },
            "exponent_real": {
                "kind": "number",
                "name": "exponent_real",
                "widget": {"kind": "number", "name": "exponent_real", "default": 2.0},
            },
            "exponent_imag": {
                "kind": "number",
                "name": "exponent_imag",
                "widget": {"kind": "number", "name": "exponent_imag", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        base_real = (
            node_inputs.get("required_inputs", {})
            .get("base_real", {})
            .get("values", 1.0)
        )
        base_imag = (
            node_inputs.get("required_inputs", {})
            .get("base_imag", {})
            .get("values", 1.0)
        )
        exponent_real = (
            node_inputs.get("required_inputs", {})
            .get("exponent_real", {})
            .get("values", 2.0)
        )
        exponent_imag = (
            node_inputs.get("required_inputs", {})
            .get("exponent_imag", {})
            .get("values", 0.0)
        )
        try:
            base = complex(base_real, base_imag)
            exponent = complex(exponent_real, exponent_imag)
            result = base**exponent
            return {"result": [result.real, result.imag]}
        except Exception as e:
            return {"error": str(e)}


class ComplexRoots:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the nth roots of a complex number."

    INPUT = {
        "required_inputs": {
            "real": {
                "kind": "number",
                "name": "real",
                "widget": {"kind": "number", "name": "real", "default": 1.0},
            },
            "imag": {
                "kind": "number",
                "name": "imag",
                "widget": {"kind": "number", "name": "imag", "default": 1.0},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        real = node_inputs.get("required_inputs", {}).get("real", {}).get("values", 1.0)
        imag = node_inputs.get("required_inputs", {}).get("imag", {}).get("values", 1.0)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 2)
        try:
            import cmath

            z = complex(real, imag)
            r = abs(z) ** (1 / n)
            theta = cmath.phase(z)
            roots = []
            for k in range(n):
                angle = (theta + 2 * cmath.pi * k) / n
                root = r * (cmath.cos(angle) + 1j * cmath.sin(angle))
                roots.append([root.real, root.imag])
            return {"result": roots}
        except Exception as e:
            return {"error": str(e)}


class QuaternionAddition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Adds two quaternions."

    INPUT = {
        "required_inputs": {
            "q1": {
                "kind": "array",
                "name": "q1",
                "widget": {"kind": "array", "name": "q1", "default": [1, 0, 0, 0]},
            },
            "q2": {
                "kind": "array",
                "name": "q2",
                "widget": {"kind": "array", "name": "q2", "default": [0, 1, 0, 0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q1 = (
            node_inputs.get("required_inputs", {})
            .get("q1", {})
            .get("values", [1, 0, 0, 0])
        )
        q2 = (
            node_inputs.get("required_inputs", {})
            .get("q2", {})
            .get("values", [0, 1, 0, 0])
        )
        try:
            result = [q1[i] + q2[i] for i in range(4)]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuaternionMultiplication:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Multiplies two quaternions."

    INPUT = {
        "required_inputs": {
            "q1": {
                "kind": "array",
                "name": "q1",
                "widget": {"kind": "array", "name": "q1", "default": [1, 0, 0, 0]},
            },
            "q2": {
                "kind": "array",
                "name": "q2",
                "widget": {"kind": "array", "name": "q2", "default": [0, 1, 0, 0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q1 = (
            node_inputs.get("required_inputs", {})
            .get("q1", {})
            .get("values", [1, 0, 0, 0])
        )
        q2 = (
            node_inputs.get("required_inputs", {})
            .get("q2", {})
            .get("values", [0, 1, 0, 0])
        )
        try:
            a1, b1, c1, d1 = q1
            a2, b2, c2, d2 = q2
            result = [
                a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2,
                a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
                a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2,
                a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2,
            ]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuaternionConjugate:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the conjugate of a quaternion."

    INPUT = {
        "required_inputs": {
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [1, 2, 3, 4]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [1, 2, 3, 4])
        )
        try:
            result = [q[0], -q[1], -q[2], -q[3]]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuaternionNorm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the norm of a quaternion."

    INPUT = {
        "required_inputs": {
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [1, 0, 0, 0]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [1, 0, 0, 0])
        )
        try:
            import math

            result = math.sqrt(sum(x * x for x in q))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuaternionInverse:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse of a quaternion."

    INPUT = {
        "required_inputs": {
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [1, 0, 0, 0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [1, 0, 0, 0])
        )
        try:
            norm_sq = sum(x * x for x in q)
            if norm_sq == 0:
                raise ValueError("Cannot compute inverse of zero quaternion")
            result = [q[0] / norm_sq, -q[1] / norm_sq, -q[2] / norm_sq, -q[3] / norm_sq]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class QuaternionRotation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Applies a quaternion rotation to a 3D vector."

    INPUT = {
        "required_inputs": {
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [1, 0, 0, 0]},
            },
            "v": {
                "kind": "array",
                "name": "v",
                "widget": {"kind": "array", "name": "v", "default": [1, 0, 0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [1, 0, 0, 0])
        )
        v = node_inputs.get("required_inputs", {}).get("v", {}).get("values", [1, 0, 0])
        try:

            def quaternion_multiply(q1, q2):
                w1, x1, y1, z1 = q1
                w2, x2, y2, z2 = q2
                return [
                    w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                    w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                    w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                    w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
                ]

            v_quat = [0] + v
            q_conj = [q[0], -q[1], -q[2], -q[3]]
            rotated = quaternion_multiply(quaternion_multiply(q, v_quat), q_conj)
            result = rotated[1:]
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SphericalToCartesian:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts spherical coordinates to Cartesian coordinates."

    INPUT = {
        "required_inputs": {
            "r": {
                "kind": "number",
                "name": "r",
                "widget": {"kind": "number", "name": "r", "default": 1.0},
            },
            "theta": {
                "kind": "number",
                "name": "theta",
                "widget": {"kind": "number", "name": "theta", "default": 0.0},
            },
            "phi": {
                "kind": "number",
                "name": "phi",
                "widget": {"kind": "number", "name": "phi", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        r = node_inputs.get("required_inputs", {}).get("r", {}).get("values", 1.0)
        theta = (
            node_inputs.get("required_inputs", {}).get("theta", {}).get("values", 0.0)
        )
        phi = node_inputs.get("required_inputs", {}).get("phi", {}).get("values", 0.0)
        try:
            import math

            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            return {"result": [x, y, z]}
        except Exception as e:
            return {"error": str(e)}


class CartesianToSpherical:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Converts Cartesian coordinates to spherical coordinates."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 1.0},
            },
            "y": {
                "kind": "number",
                "name": "y",
                "widget": {"kind": "number", "name": "y", "default": 0.0},
            },
            "z": {
                "kind": "number",
                "name": "z",
                "widget": {"kind": "number", "name": "z", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 1.0)
        y = node_inputs.get("required_inputs", {}).get("y", {}).get("values", 0.0)
        z = node_inputs.get("required_inputs", {}).get("z", {}).get("values", 0.0)
        try:
            import math

            r = math.sqrt(x**2 + y**2 + z**2)
            theta = math.acos(z / r) if r != 0 else 0
            phi = math.atan2(y, x)
            return {"result": [r, theta, phi]}
        except Exception as e:
            return {"error": str(e)}


class EllipticIntegralThirdKind:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the complete elliptic integral of the third kind for a given parameter."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 0.5},
            },
            "m": {
                "kind": "number",
                "name": "m",
                "widget": {"kind": "number", "name": "m", "default": 0.5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 0.5)
        m = node_inputs.get("required_inputs", {}).get("m", {}).get("values", 0.5)
        try:
            from scipy import special

            result = special.ellipkinc(n, m)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class JacobiEllipticFunctions:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Jacobi elliptic functions for given parameters."

    INPUT = {
        "required_inputs": {
            "u": {
                "kind": "number",
                "name": "u",
                "widget": {"kind": "number", "name": "u", "default": 1.0},
            },
            "m": {
                "kind": "number",
                "name": "m",
                "widget": {"kind": "number", "name": "m", "default": 0.5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        u = node_inputs.get("required_inputs", {}).get("u", {}).get("values", 1.0)
        m = node_inputs.get("required_inputs", {}).get("m", {}).get("values", 0.5)
        try:
            from scipy import special

            sn, cn, dn, ph = special.ellipj(u, m)
            return {"result": [sn, cn, dn, ph]}
        except Exception as e:
            return {"error": str(e)}


class LambertConformalConicProjection:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Lambert conformal conic projection for given geographic coordinates."

    INPUT = {
        "required_inputs": {
            "lat": {
                "kind": "number",
                "name": "lat",
                "widget": {"kind": "number", "name": "lat", "default": 0.0},
            },
            "lon": {
                "kind": "number",
                "name": "lon",
                "widget": {"kind": "number", "name": "lon", "default": 0.0},
            },
            "std_parallel1": {
                "kind": "number",
                "name": "std_parallel1",
                "widget": {"kind": "number", "name": "std_parallel1", "default": 30.0},
            },
            "std_parallel2": {
                "kind": "number",
                "name": "std_parallel2",
                "widget": {"kind": "number", "name": "std_parallel2", "default": 60.0},
            },
            "central_meridian": {
                "kind": "number",
                "name": "central_meridian",
                "widget": {
                    "kind": "number",
                    "name": "central_meridian",
                    "default": 0.0,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        lat = node_inputs.get("required_inputs", {}).get("lat", {}).get("values", 0.0)
        lon = node_inputs.get("required_inputs", {}).get("lon", {}).get("values", 0.0)
        std_parallel1 = (
            node_inputs.get("required_inputs", {})
            .get("std_parallel1", {})
            .get("values", 30.0)
        )
        std_parallel2 = (
            node_inputs.get("required_inputs", {})
            .get("std_parallel2", {})
            .get("values", 60.0)
        )
        central_meridian = (
            node_inputs.get("required_inputs", {})
            .get("central_meridian", {})
            .get("values", 0.0)
        )
        try:
            import math

            def to_radians(angle):
                return angle * math.pi / 180.0

            lat, lon = map(to_radians, (lat, lon))
            std_parallel1, std_parallel2, central_meridian = map(
                to_radians, (std_parallel1, std_parallel2, central_meridian)
            )

            n = math.log(math.cos(std_parallel1) / math.cos(std_parallel2)) / math.log(
                math.tan(math.pi / 4 + std_parallel2 / 2)
                / math.tan(math.pi / 4 + std_parallel1 / 2)
            )
            F = (
                math.cos(std_parallel1)
                * math.tan(math.pi / 4 + std_parallel1 / 2) ** n
                / n
            )
            rho = F / math.tan(math.pi / 4 + lat / 2) ** n

            x = rho * math.sin(n * (lon - central_meridian))
            y = F - rho * math.cos(n * (lon - central_meridian))

            return {"result": [x, y]}
        except Exception as e:
            return {"error": str(e)}


class MercatorProjection:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Mercator projection for given geographic coordinates."

    INPUT = {
        "required_inputs": {
            "lat": {
                "kind": "number",
                "name": "lat",
                "widget": {"kind": "number", "name": "lat", "default": 0.0},
            },
            "lon": {
                "kind": "number",
                "name": "lon",
                "widget": {"kind": "number", "name": "lon", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        lat = node_inputs.get("required_inputs", {}).get("lat", {}).get("values", 0.0)
        lon = node_inputs.get("required_inputs", {}).get("lon", {}).get("values", 0.0)
        try:
            import math

            def to_radians(angle):
                return angle * math.pi / 180.0

            lat, lon = map(to_radians, (lat, lon))

            x = lon
            y = math.log(math.tan(math.pi / 4 + lat / 2))

            return {"result": [x, y]}
        except Exception as e:
            return {"error": str(e)}


class HaversineFormula:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the great-circle distance between two points on a sphere using the Haversine formula."

    INPUT = {
        "required_inputs": {
            "lat1": {
                "kind": "number",
                "name": "lat1",
                "widget": {"kind": "number", "name": "lat1", "default": 0.0},
            },
            "lon1": {
                "kind": "number",
                "name": "lon1",
                "widget": {"kind": "number", "name": "lon1", "default": 0.0},
            },
            "lat2": {
                "kind": "number",
                "name": "lat2",
                "widget": {"kind": "number", "name": "lat2", "default": 0.0},
            },
            "lon2": {
                "kind": "number",
                "name": "lon2",
                "widget": {"kind": "number", "name": "lon2", "default": 0.0},
            },
            "radius": {
                "kind": "number",
                "name": "radius",
                "widget": {"kind": "number", "name": "radius", "default": 6371.0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        lat1 = node_inputs.get("required_inputs", {}).get("lat1", {}).get("values", 0.0)
        lon1 = node_inputs.get("required_inputs", {}).get("lon1", {}).get("values", 0.0)
        lat2 = node_inputs.get("required_inputs", {}).get("lat2", {}).get("values", 0.0)
        lon2 = node_inputs.get("required_inputs", {}).get("lon2", {}).get("values", 0.0)
        radius = (
            node_inputs.get("required_inputs", {})
            .get("radius", {})
            .get("values", 6371.0)
        )
        try:
            import math

            def to_radians(angle):
                return angle * math.pi / 180.0

            lat1, lon1, lat2, lon2 = map(to_radians, (lat1, lon1, lat2, lon2))

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = (
                math.sin(dlat / 2) ** 2
                + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

            distance = radius * c

            return {"result": distance}
        except Exception as e:
            return {"error": str(e)}


class BarycentricCoordinates:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the barycentric coordinates for a point within a triangle."

    INPUT = {
        "required_inputs": {
            "point": {
                "kind": "array",
                "name": "point",
                "widget": {"kind": "array", "name": "point", "default": [0, 0]},
            },
            "triangle": {
                "kind": "array",
                "name": "triangle",
                "widget": {
                    "kind": "array",
                    "name": "triangle",
                    "default": [[0, 0], [1, 0], [0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        point = (
            node_inputs.get("required_inputs", {})
            .get("point", {})
            .get("values", [0, 0])
        )
        triangle = (
            node_inputs.get("required_inputs", {})
            .get("triangle", {})
            .get("values", [[0, 0], [1, 0], [0, 1]])
        )
        try:
            import numpy as np

            A, B, C = np.array(triangle)
            P = np.array(point)

            v0 = C - A
            v1 = B - A
            v2 = P - A

            d00 = np.dot(v0, v0)
            d01 = np.dot(v0, v1)
            d11 = np.dot(v1, v1)
            d20 = np.dot(v2, v0)
            d21 = np.dot(v2, v1)

            denom = d00 * d11 - d01 * d01
            v = (d11 * d20 - d01 * d21) / denom
            w = (d00 * d21 - d01 * d20) / denom
            u = 1.0 - v - w

            return {"result": [u, v, w]}
        except Exception as e:
            return {"error": str(e)}


class BezierCurve:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes points on a Bezier curve given control points."

    INPUT = {
        "required_inputs": {
            "control_points": {
                "kind": "array",
                "name": "control_points",
                "widget": {
                    "kind": "array",
                    "name": "control_points",
                    "default": [[0, 0], [1, 1], [2, 0], [3, 1]],
                },
            },
            "num_points": {
                "kind": "number",
                "name": "num_points",
                "widget": {"kind": "number", "name": "num_points", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        control_points = (
            node_inputs.get("required_inputs", {})
            .get("control_points", {})
            .get("values", [[0, 0], [1, 1], [2, 0], [3, 1]])
        )
        num_points = (
            node_inputs.get("required_inputs", {})
            .get("num_points", {})
            .get("values", 100)
        )
        try:
            import numpy as np

            def bezier_curve(t, control_points):
                n = len(control_points) - 1
                return sum(
                    comb(n, i) * t**i * (1 - t) ** (n - i) * np.array(control_points[i])
                    for i in range(n + 1)
                )

            def comb(n, k):
                return np.math.factorial(n) // (
                    np.math.factorial(k) * np.math.factorial(n - k)
                )

            t = np.linspace(0, 1, num_points)
            curve_points = [bezier_curve(ti, control_points) for ti in t]

            return {"result": curve_points}
        except Exception as e:
            return {"error": str(e)}


class CatmullRomSpline:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes points on a Catmull-Rom spline given control points."

    INPUT = {
        "required_inputs": {
            "control_points": {
                "kind": "array",
                "name": "control_points",
                "widget": {
                    "kind": "array",
                    "name": "control_points",
                    "default": [[0, 0], [1, 1], [2, 0], [3, 1]],
                },
            },
            "num_points": {
                "kind": "number",
                "name": "num_points",
                "widget": {"kind": "number", "name": "num_points", "default": 100},
            },
            "alpha": {
                "kind": "number",
                "name": "alpha",
                "widget": {"kind": "number", "name": "alpha", "default": 0.5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        control_points = (
            node_inputs.get("required_inputs", {})
            .get("control_points", {})
            .get("values", [[0, 0], [1, 1], [2, 0], [3, 1]])
        )
        num_points = (
            node_inputs.get("required_inputs", {})
            .get("num_points", {})
            .get("values", 100)
        )
        alpha = (
            node_inputs.get("required_inputs", {}).get("alpha", {}).get("values", 0.5)
        )
        try:
            import numpy as np

            def catmull_rom_spline(t, p0, p1, p2, p3, alpha):
                t0 = 0
                t1 = t0 + np.linalg.norm(p1 - p0) ** alpha
                t2 = t1 + np.linalg.norm(p2 - p1) ** alpha
                t3 = t2 + np.linalg.norm(p3 - p2) ** alpha

                t = t1 + t * (t2 - t1)

                A1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
                A2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
                A3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3

                B1 = (t2 - t) / (t2 - t0) * A1 + (t - t0) / (t2 - t0) * A2
                B2 = (t3 - t) / (t3 - t1) * A2 + (t - t1) / (t3 - t1) * A3

                C = (t2 - t) / (t2 - t1) * B1 + (t - t1) / (t2 - t1) * B2

                return C

            control_points = np.array(control_points)
            t = np.linspace(0, 1, num_points)
            spline_points = []

            for i in range(len(control_points) - 3):
                p0, p1, p2, p3 = control_points[i : i + 4]
                spline_points.extend(
                    [catmull_rom_spline(ti, p0, p1, p2, p3, alpha) for ti in t]
                )

            return {"result": spline_points}
        except Exception as e:
            return {"error": str(e)}


class HermiteSpline:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes points on a Hermite spline given control points and tangents."
    )

    INPUT = {
        "required_inputs": {
            "control_points": {
                "kind": "array",
                "name": "control_points",
                "widget": {
                    "kind": "array",
                    "name": "control_points",
                    "default": [[0, 0], [1, 1]],
                },
            },
            "tangents": {
                "kind": "array",
                "name": "tangents",
                "widget": {
                    "kind": "array",
                    "name": "tangents",
                    "default": [[1, 0], [1, 0]],
                },
            },
            "num_points": {
                "kind": "number",
                "name": "num_points",
                "widget": {"kind": "number", "name": "num_points", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        control_points = (
            node_inputs.get("required_inputs", {})
            .get("control_points", {})
            .get("values", [[0, 0], [1, 1]])
        )
        tangents = (
            node_inputs.get("required_inputs", {})
            .get("tangents", {})
            .get("values", [[1, 0], [1, 0]])
        )
        num_points = (
            node_inputs.get("required_inputs", {})
            .get("num_points", {})
            .get("values", 100)
        )
        try:
            import numpy as np

            def hermite_spline(t, p0, p1, m0, m1):
                t2 = t * t
                t3 = t2 * t
                h00 = 2 * t3 - 3 * t2 + 1
                h10 = t3 - 2 * t2 + t
                h01 = -2 * t3 + 3 * t2
                h11 = t3 - t2
                return h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1

            control_points = np.array(control_points)
            tangents = np.array(tangents)
            t = np.linspace(0, 1, num_points)
            spline_points = []

            for i in range(len(control_points) - 1):
                p0, p1 = control_points[i : i + 2]
                m0, m1 = tangents[i : i + 2]
                spline_points.extend([hermite_spline(ti, p0, p1, m0, m1) for ti in t])

            return {"result": spline_points}
        except Exception as e:
            return {"error": str(e)}


class LagrangeInterpolation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Lagrange polynomial interpolation for a set of points."

    INPUT = {
        "required_inputs": {
            "x_points": {
                "kind": "array",
                "name": "x_points",
                "widget": {
                    "kind": "array",
                    "name": "x_points",
                    "default": [0, 1, 2, 3],
                },
            },
            "y_points": {
                "kind": "array",
                "name": "y_points",
                "widget": {
                    "kind": "array",
                    "name": "y_points",
                    "default": [1, 2, 4, 8],
                },
            },
            "x_eval": {
                "kind": "number",
                "name": "x_eval",
                "widget": {"kind": "number", "name": "x_eval", "default": 1.5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x_points = (
            node_inputs.get("required_inputs", {})
            .get("x_points", {})
            .get("values", [0, 1, 2, 3])
        )
        y_points = (
            node_inputs.get("required_inputs", {})
            .get("y_points", {})
            .get("values", [1, 2, 4, 8])
        )
        x_eval = (
            node_inputs.get("required_inputs", {}).get("x_eval", {}).get("values", 1.5)
        )
        try:

            def lagrange_interpolation(x, x_points, y_points):
                n = len(x_points)
                result = 0
                for i in range(n):
                    term = y_points[i]
                    for j in range(n):
                        if i != j:
                            term *= (x - x_points[j]) / (x_points[i] - x_points[j])
                    result += term
                return result

            result = lagrange_interpolation(x_eval, x_points, y_points)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class NewtonInterpolation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Newton polynomial interpolation for a set of points."

    INPUT = {
        "required_inputs": {
            "x_points": {
                "kind": "array",
                "name": "x_points",
                "widget": {
                    "kind": "array",
                    "name": "x_points",
                    "default": [0, 1, 2, 3],
                },
            },
            "y_points": {
                "kind": "array",
                "name": "y_points",
                "widget": {
                    "kind": "array",
                    "name": "y_points",
                    "default": [1, 2, 4, 8],
                },
            },
            "x_eval": {
                "kind": "number",
                "name": "x_eval",
                "widget": {"kind": "number", "name": "x_eval", "default": 1.5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x_points = (
            node_inputs.get("required_inputs", {})
            .get("x_points", {})
            .get("values", [0, 1, 2, 3])
        )
        y_points = (
            node_inputs.get("required_inputs", {})
            .get("y_points", {})
            .get("values", [1, 2, 4, 8])
        )
        x_eval = (
            node_inputs.get("required_inputs", {}).get("x_eval", {}).get("values", 1.5)
        )
        try:

            def divided_differences(x, y):
                n = len(y)
                coef = [y[i] for i in range(n)]
                for j in range(1, n):
                    for i in range(n - 1, j - 1, -1):
                        coef[i] = (coef[i] - coef[i - 1]) / (x[i] - x[i - j])
                return coef

            def newton_interpolation(x, x_points, coef):
                n = len(x_points) - 1
                p = coef[n]
                for k in range(1, n + 1):
                    p = coef[n - k] + (x - x_points[n - k]) * p
                return p

            coef = divided_differences(x_points, y_points)
            result = newton_interpolation(x_eval, x_points, coef)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SplineInterpolation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes a spline interpolation for a set of points."

    INPUT = {
        "required_inputs": {
            "x_points": {
                "kind": "array",
                "name": "x_points",
                "widget": {
                    "kind": "array",
                    "name": "x_points",
                    "default": [0, 1, 2, 3],
                },
            },
            "y_points": {
                "kind": "array",
                "name": "y_points",
                "widget": {
                    "kind": "array",
                    "name": "y_points",
                    "default": [1, 2, 4, 8],
                },
            },
            "x_eval": {
                "kind": "number",
                "name": "x_eval",
                "widget": {"kind": "number", "name": "x_eval", "default": 1.5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x_points = (
            node_inputs.get("required_inputs", {})
            .get("x_points", {})
            .get("values", [0, 1, 2, 3])
        )
        y_points = (
            node_inputs.get("required_inputs", {})
            .get("y_points", {})
            .get("values", [1, 2, 4, 8])
        )
        x_eval = (
            node_inputs.get("required_inputs", {}).get("x_eval", {}).get("values", 1.5)
        )
        try:
            from scipy import interpolate

            f = interpolate.interp1d(x_points, y_points, kind="cubic")
            result = float(f(x_eval))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class FourierSeries:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Fourier series coefficients for a periodic function."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x",
                },
            },
            "period": {
                "kind": "number",
                "name": "period",
                "widget": {"kind": "number", "name": "period", "default": 2 * 3.14159},
            },
            "num_terms": {
                "kind": "number",
                "name": "num_terms",
                "widget": {"kind": "number", "name": "num_terms", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x")
        )
        period = (
            node_inputs.get("required_inputs", {})
            .get("period", {})
            .get("values", 2 * 3.14159)
        )
        num_terms = (
            node_inputs.get("required_inputs", {}).get("num_terms", {}).get("values", 5)
        )
        try:
            import numpy as np
            from scipy import integrate

            function = eval(function_str)
            omega = 2 * np.pi / period

            def a_n(n):
                return (2 / period) * integrate.quad(
                    lambda x: function(x) * np.cos(n * omega * x), 0, period
                )[0]

            def b_n(n):
                return (2 / period) * integrate.quad(
                    lambda x: function(x) * np.sin(n * omega * x), 0, period
                )[0]

            a0 = (1 / period) * integrate.quad(function, 0, period)[0]
            coeffs = [a0] + [complex(a_n(n), b_n(n)) for n in range(1, num_terms + 1)]

            return {"result": coeffs}
        except Exception as e:
            return {"error": str(e)}


class ZTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Z-transform of a discrete-time signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "z": {
                "kind": "complex",
                "name": "z",
                "widget": {"kind": "complex", "name": "z"},
            },
        },
    }

    OUTPUT = {
        "kind": "complex",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        z = node_inputs.get("required_inputs", {}).get("z", {}).get("values", 1 + 0j)
        try:
            result = sum(x * z ** (-n) for n, x in enumerate(signal))
            return {"result": complex(result)}
        except Exception as e:
            return {"error": str(e)}


class HilbertTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Hilbert transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            from scipy import signal as sig

            analytic_signal = sig.hilbert(signal)
            hilbert_transform = analytic_signal.imag
            return {"result": hilbert_transform.tolist()}
        except Exception as e:
            return {"error": str(e)}


class DiscreteCosineTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the discrete cosine transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            from scipy.fftpack import dct

            dct_result = dct(signal, type=2, norm="ortho")
            return {"result": dct_result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class DiscreteSineTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the discrete sine transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            from scipy.fftpack import dst

            dst_result = dst(signal, type=2, norm="ortho")
            return {"result": dst_result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class FastFourierTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the fast Fourier transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            fft_result = np.fft.fft(signal)
            return {"result": fft_result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class InverseFastFourierTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the inverse fast Fourier transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1 + 0j, 2 + 0j, 3 + 0j, 4 + 0j, 5 + 0j])
        )
        try:
            import numpy as np

            ifft_result = np.fft.ifft(signal)
            return {"result": ifft_result.real.tolist()}
        except Exception as e:
            return {"error": str(e)}


class PowerSpectralDensity:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the power spectral density of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            from scipy import signal as sig

            f, Pxx = sig.periodogram(signal)
            return {"result": Pxx.tolist()}
        except Exception as e:
            return {"error": str(e)}


class CrossCorrelation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cross-correlation between two signals."

    INPUT = {
        "required_inputs": {
            "signal1": {
                "kind": "array",
                "name": "signal1",
                "widget": {
                    "kind": "array",
                    "name": "signal1",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "signal2": {
                "kind": "array",
                "name": "signal2",
                "widget": {
                    "kind": "array",
                    "name": "signal2",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal1 = (
            node_inputs.get("required_inputs", {})
            .get("signal1", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        signal2 = (
            node_inputs.get("required_inputs", {})
            .get("signal2", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            cross_corr = np.correlate(signal1, signal2, mode="full")
            return {"result": cross_corr.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Autocorrelation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the autocorrelation of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            autocorr = np.correlate(signal, signal, mode="full")
            return {"result": autocorr[len(signal) - 1 :].tolist()}
        except Exception as e:
            return {"error": str(e)}


class Convolution:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the convolution of two signals."

    INPUT = {
        "required_inputs": {
            "signal1": {
                "kind": "array",
                "name": "signal1",
                "widget": {
                    "kind": "array",
                    "name": "signal1",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "signal2": {
                "kind": "array",
                "name": "signal2",
                "widget": {
                    "kind": "array",
                    "name": "signal2",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal1 = (
            node_inputs.get("required_inputs", {})
            .get("signal1", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        signal2 = (
            node_inputs.get("required_inputs", {})
            .get("signal2", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            conv_result = np.convolve(signal1, signal2, mode="full")
            return {"result": conv_result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Deconvolution:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the deconvolution of two signals."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "kernel": {
                "kind": "array",
                "name": "kernel",
                "widget": {"kind": "array", "name": "kernel", "default": [1, 2, 3]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        kernel = (
            node_inputs.get("required_inputs", {})
            .get("kernel", {})
            .get("values", [1, 2, 3])
        )
        try:
            from scipy import signal as sig

            deconv_result, _ = sig.deconvolve(signal, kernel)
            return {"result": deconv_result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class RiemannSum:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the Riemann sum for approximating the integral of a function."
    )

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1.0},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1.0)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 100)
        try:
            import numpy as np

            f = eval(function_str)
            x = np.linspace(a, b, n + 1)
            dx = (b - a) / n
            result = np.sum(f(x[:-1]) * dx)
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class MonteCarloIntegration:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Performs numerical integration using the Monte Carlo method."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1.0},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 100000},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1.0)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 100000)
        try:
            import numpy as np

            f = eval(function_str)
            x = np.random.uniform(a, b, n)
            result = (b - a) * np.mean(f(x))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class SimpsonRule:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the integral of a function using Simpson's rule."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1.0},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1.0)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 100)
        try:
            import numpy as np

            f = eval(function_str)
            x = np.linspace(a, b, n + 1)
            y = f(x)
            dx = (b - a) / n
            result = dx / 3 * np.sum(y[0:-1:2] + 4 * y[1::2] + y[2::2])
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class TrapezoidalRule:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the integral of a function using the trapezoidal rule."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 1.0},
            },
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 1.0)
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 100)
        try:
            import numpy as np

            f = eval(function_str)
            x = np.linspace(a, b, n + 1)
            y = f(x)
            dx = (b - a) / n
            result = dx * (np.sum(y) - 0.5 * (y[0] + y[-1]))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class BisectionMethod:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the root of a function using the bisection method."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2 - 2",
                },
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.0},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 2.0},
            },
            "tol": {
                "kind": "number",
                "name": "tol",
                "widget": {"kind": "number", "name": "tol", "default": 1e-6},
            },
            "max_iter": {
                "kind": "number",
                "name": "max_iter",
                "widget": {"kind": "number", "name": "max_iter", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2 - 2")
        )
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.0)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 2.0)
        tol = node_inputs.get("required_inputs", {}).get("tol", {}).get("values", 1e-6)
        max_iter = (
            node_inputs.get("required_inputs", {})
            .get("max_iter", {})
            .get("values", 100)
        )
        try:
            f = eval(function_str)
            for _ in range(max_iter):
                c = (a + b) / 2
                if abs(f(c)) < tol:
                    return {"result": float(c)}
                if f(c) * f(a) < 0:
                    b = c
                else:
                    a = c
            return {"error": "Maximum iterations reached without convergence"}
        except Exception as e:
            return {"error": str(e)}


class NewtonRaphsonMethod:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the root of a function using the Newton-Raphson method."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2 - 2",
                },
            },
            "derivative": {
                "kind": "string",
                "name": "derivative",
                "widget": {
                    "kind": "string",
                    "name": "derivative",
                    "default": "lambda x: 2*x",
                },
            },
            "x0": {
                "kind": "number",
                "name": "x0",
                "widget": {"kind": "number", "name": "x0", "default": 1.0},
            },
            "tol": {
                "kind": "number",
                "name": "tol",
                "widget": {"kind": "number", "name": "tol", "default": 1e-6},
            },
            "max_iter": {
                "kind": "number",
                "name": "max_iter",
                "widget": {"kind": "number", "name": "max_iter", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2 - 2")
        )
        derivative_str = (
            node_inputs.get("required_inputs", {})
            .get("derivative", {})
            .get("values", "lambda x: 2*x")
        )
        x0 = node_inputs.get("required_inputs", {}).get("x0", {}).get("values", 1.0)
        tol = node_inputs.get("required_inputs", {}).get("tol", {}).get("values", 1e-6)
        max_iter = (
            node_inputs.get("required_inputs", {})
            .get("max_iter", {})
            .get("values", 100)
        )
        try:
            f = eval(function_str)
            df = eval(derivative_str)
            x = x0
            for _ in range(max_iter):
                fx = f(x)
                if abs(fx) < tol:
                    return {"result": float(x)}
                dfx = df(x)
                if dfx == 0:
                    return {"error": "Derivative is zero"}
                x = x - fx / dfx
            return {"error": "Maximum iterations reached without convergence"}
        except Exception as e:
            return {"error": str(e)}


class SecantMethod:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Finds the root of a function using the secant method."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2 - 2",
                },
            },
            "x0": {
                "kind": "number",
                "name": "x0",
                "widget": {"kind": "number", "name": "x0", "default": 1.0},
            },
            "x1": {
                "kind": "number",
                "name": "x1",
                "widget": {"kind": "number", "name": "x1", "default": 2.0},
            },
            "tol": {
                "kind": "number",
                "name": "tol",
                "widget": {"kind": "number", "name": "tol", "default": 1e-6},
            },
            "max_iter": {
                "kind": "number",
                "name": "max_iter",
                "widget": {"kind": "number", "name": "max_iter", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2 - 2")
        )
        x0 = node_inputs.get("required_inputs", {}).get("x0", {}).get("values", 1.0)
        x1 = node_inputs.get("required_inputs", {}).get("x1", {}).get("values", 2.0)
        tol = node_inputs.get("required_inputs", {}).get("tol", {}).get("values", 1e-6)
        max_iter = (
            node_inputs.get("required_inputs", {})
            .get("max_iter", {})
            .get("values", 100)
        )
        try:
            f = eval(function_str)
            for _ in range(max_iter):
                fx0 = f(x0)
                fx1 = f(x1)
                if abs(fx1) < tol:
                    return {"result": float(x1)}
                if fx0 == fx1:
                    return {"error": "Division by zero"}
                x = x1 - fx1 * (x1 - x0) / (fx1 - fx0)
                x0, x1 = x1, x
            return {"error": "Maximum iterations reached without convergence"}
        except Exception as e:
            return {"error": str(e)}


class GradientDescent:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Performs optimization using the gradient descent algorithm."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "initial_guess": {
                "kind": "number",
                "name": "initial_guess",
                "widget": {"kind": "number", "name": "initial_guess", "default": 1.0},
            },
            "learning_rate": {
                "kind": "number",
                "name": "learning_rate",
                "widget": {"kind": "number", "name": "learning_rate", "default": 0.1},
            },
            "max_iter": {
                "kind": "number",
                "name": "max_iter",
                "widget": {"kind": "number", "name": "max_iter", "default": 100},
            },
            "tolerance": {
                "kind": "number",
                "name": "tolerance",
                "widget": {"kind": "number", "name": "tolerance", "default": 1e-6},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        initial_guess = (
            node_inputs.get("required_inputs", {})
            .get("initial_guess", {})
            .get("values", 1.0)
        )
        learning_rate = (
            node_inputs.get("required_inputs", {})
            .get("learning_rate", {})
            .get("values", 0.1)
        )
        max_iter = (
            node_inputs.get("required_inputs", {})
            .get("max_iter", {})
            .get("values", 100)
        )
        tolerance = (
            node_inputs.get("required_inputs", {})
            .get("tolerance", {})
            .get("values", 1e-6)
        )
        try:
            f = eval(function_str)

            def gradient(f, x, h=1e-8):
                return (f(x + h) - f(x - h)) / (2 * h)

            x = initial_guess
            for _ in range(max_iter):
                grad = gradient(f, x)
                if abs(grad) < tolerance:
                    return {"result": float(x)}
                x = x - learning_rate * grad
            return {"result": float(x)}
        except Exception as e:
            return {"error": str(e)}


class ConjugateGradient:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Solves linear systems using the conjugate gradient method."

    INPUT = {
        "required_inputs": {
            "A": {
                "kind": "array",
                "name": "A",
                "widget": {"kind": "array", "name": "A", "default": [[4, 1], [1, 3]]},
            },
            "b": {
                "kind": "array",
                "name": "b",
                "widget": {"kind": "array", "name": "b", "default": [1, 2]},
            },
            "max_iter": {
                "kind": "number",
                "name": "max_iter",
                "widget": {"kind": "number", "name": "max_iter", "default": 100},
            },
            "tolerance": {
                "kind": "number",
                "name": "tolerance",
                "widget": {"kind": "number", "name": "tolerance", "default": 1e-6},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        A = (
            node_inputs.get("required_inputs", {})
            .get("A", {})
            .get("values", [[4, 1], [1, 3]])
        )
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", [1, 2])
        max_iter = (
            node_inputs.get("required_inputs", {})
            .get("max_iter", {})
            .get("values", 100)
        )
        tolerance = (
            node_inputs.get("required_inputs", {})
            .get("tolerance", {})
            .get("values", 1e-6)
        )
        try:
            import numpy as np

            A = np.array(A)
            b = np.array(b)
            x = np.zeros_like(b)
            r = b - np.dot(A, x)
            p = r.copy()
            for _ in range(max_iter):
                Ap = np.dot(A, p)
                alpha = np.dot(r, r) / np.dot(p, Ap)
                x += alpha * p
                r_new = r - alpha * Ap
                if np.linalg.norm(r_new) < tolerance:
                    return {"result": x.tolist()}
                beta = np.dot(r_new, r_new) / np.dot(r, r)
                p = r_new + beta * p
                r = r_new
            return {"result": x.tolist()}
        except Exception as e:
            return {"error": str(e)}


class LevenbergMarquardt:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Performs non-linear least squares optimization using the Levenberg-Marquardt algorithm."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x, t: x[0] * np.exp(-x[1] * t)",
                },
            },
            "x_data": {
                "kind": "array",
                "name": "x_data",
                "widget": {
                    "kind": "array",
                    "name": "x_data",
                    "default": [0, 1, 2, 3, 4],
                },
            },
            "y_data": {
                "kind": "array",
                "name": "y_data",
                "widget": {
                    "kind": "array",
                    "name": "y_data",
                    "default": [1.0, 0.5, 0.25, 0.125, 0.0625],
                },
            },
            "initial_guess": {
                "kind": "array",
                "name": "initial_guess",
                "widget": {
                    "kind": "array",
                    "name": "initial_guess",
                    "default": [1.0, 1.0],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x, t: x[0] * np.exp(-x[1] * t)")
        )
        x_data = (
            node_inputs.get("required_inputs", {})
            .get("x_data", {})
            .get("values", [0, 1, 2, 3, 4])
        )
        y_data = (
            node_inputs.get("required_inputs", {})
            .get("y_data", {})
            .get("values", [1.0, 0.5, 0.25, 0.125, 0.0625])
        )
        initial_guess = (
            node_inputs.get("required_inputs", {})
            .get("initial_guess", {})
            .get("values", [1.0, 1.0])
        )
        try:
            from scipy.optimize import curve_fit

            f = eval(function_str)
            popt, _ = curve_fit(f, x_data, y_data, p0=initial_guess, method="lm")
            return {"result": popt.tolist()}
        except Exception as e:
            return {"error": str(e)}


class JacobianMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Jacobian matrix of a vector-valued function."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: [x[0]**2, x[1]**2]",
                },
            },
            "point": {
                "kind": "array",
                "name": "point",
                "widget": {"kind": "array", "name": "point", "default": [1.0, 1.0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: [x[0]**2, x[1]**2]")
        )
        point = (
            node_inputs.get("required_inputs", {})
            .get("point", {})
            .get("values", [1.0, 1.0])
        )
        try:
            import numpy as np
            from scipy.misc import derivative

            f = eval(function_str)
            n = len(point)
            m = len(f(point))

            def partial_derivative(func, var=0):
                return lambda *args: derivative(
                    lambda x: func(*(list(args[:var]) + [x] + list(args[var + 1 :]))),
                    args[var],
                    dx=1e-6,
                )

            jacobian = np.zeros((m, n))
            for i in range(m):
                for j in range(n):
                    jacobian[i, j] = partial_derivative(lambda *x: f(x)[i], j)(*point)

            return {"result": jacobian.tolist()}
        except Exception as e:
            return {"error": str(e)}


class HessianMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Hessian matrix of a scalar-valued function."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x[0]**2 + x[1]**2",
                },
            },
            "point": {
                "kind": "array",
                "name": "point",
                "widget": {"kind": "array", "name": "point", "default": [1.0, 1.0]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x[0]**2 + x[1]**2")
        )
        point = (
            node_inputs.get("required_inputs", {})
            .get("point", {})
            .get("values", [1.0, 1.0])
        )
        try:
            import numpy as np
            from scipy.misc import derivative

            f = eval(function_str)
            n = len(point)

            def partial_derivative(func, var=0):
                return lambda *args: derivative(
                    lambda x: func(*(list(args[:var]) + [x] + list(args[var + 1 :]))),
                    args[var],
                    dx=1e-6,
                )

            hessian = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    hessian[i, j] = partial_derivative(partial_derivative(f, i), j)(
                        *point
                    )

            return {"result": hessian.tolist()}
        except Exception as e:
            return {"error": str(e)}


class Laplacian:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Laplacian of a scalar field."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x[0]**2 + x[1]**2",
                },
            },
            "point": {
                "kind": "array",
                "name": "point",
                "widget": {"kind": "array", "name": "point", "default": [1.0, 1.0]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x[0]**2 + x[1]**2")
        )
        point = (
            node_inputs.get("required_inputs", {})
            .get("point", {})
            .get("values", [1.0, 1.0])
        )
        try:
            from scipy.misc import derivative

            f = eval(function_str)
            n = len(point)

            def partial_derivative(func, var=0):
                return lambda *args: derivative(
                    lambda x: func(*(list(args[:var]) + [x] + list(args[var + 1 :]))),
                    args[var],
                    dx=1e-6,
                )

            laplacian = sum(
                partial_derivative(partial_derivative(f, i), i)(*point)
                for i in range(n)
            )

            return {"result": float(laplacian)}
        except Exception as e:
            return {"error": str(e)}


class CovarianceMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the covariance matrix for a set of data."

    INPUT = {
        "required_inputs": {
            "data": {
                "kind": "array",
                "name": "data",
                "widget": {
                    "kind": "array",
                    "name": "data",
                    "default": [[1, 2], [3, 4], [5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        data = (
            node_inputs.get("required_inputs", {})
            .get("data", {})
            .get("values", [[1, 2], [3, 4], [5, 6]])
        )
        try:
            import numpy as np

            cov_matrix = np.cov(np.array(data).T)
            return {"result": cov_matrix.tolist()}
        except Exception as e:
            return {"error": str(e)}


class CorrelationMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the correlation matrix for a set of data."

    INPUT = {
        "required_inputs": {
            "data": {
                "kind": "array",
                "name": "data",
                "widget": {
                    "kind": "array",
                    "name": "data",
                    "default": [[1, 2], [3, 4], [5, 6]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        data = (
            node_inputs.get("required_inputs", {})
            .get("data", {})
            .get("values", [[1, 2], [3, 4], [5, 6]])
        )
        try:
            import numpy as np

            corr_matrix = np.corrcoef(np.array(data).T)
            return {"result": corr_matrix.tolist()}
        except Exception as e:
            return {"error": str(e)}


class ChirpZTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Chirp Z-transform of a signal."

    INPUT = {
        "required_inputs": {
            "signal": {
                "kind": "array",
                "name": "signal",
                "widget": {
                    "kind": "array",
                    "name": "signal",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "M": {
                "kind": "number",
                "name": "M",
                "widget": {"kind": "number", "name": "M", "default": 100},
            },
            "W": {
                "kind": "complex",
                "name": "W",
                "widget": {"kind": "complex", "name": "W"},
            },
            "A": {
                "kind": "complex",
                "name": "A",
                "widget": {"kind": "complex", "name": "A"},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        signal = (
            node_inputs.get("required_inputs", {})
            .get("signal", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        M = node_inputs.get("required_inputs", {}).get("M", {}).get("values", 100)
        W = (
            node_inputs.get("required_inputs", {})
            .get("W", {})
            .get("values", 0.99 - 0.01j)
        )
        A = node_inputs.get("required_inputs", {}).get("A", {}).get("values", 1 + 0j)
        try:
            from scipy.signal import chirpz

            czt = chirpz(signal, M, W, A)
            return {"result": czt.tolist()}
        except Exception as e:
            return {"error": str(e)}


class KalmanFilter:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Implements a Kalman filter for state estimation."

    INPUT = {
        "required_inputs": {
            "measurements": {
                "kind": "array",
                "name": "measurements",
                "widget": {
                    "kind": "array",
                    "name": "measurements",
                    "default": [1, 2, 3, 4, 5],
                },
            },
            "initial_state": {
                "kind": "number",
                "name": "initial_state",
                "widget": {"kind": "number", "name": "initial_state", "default": 0.0},
            },
            "initial_estimate_error": {
                "kind": "number",
                "name": "initial_estimate_error",
                "widget": {
                    "kind": "number",
                    "name": "initial_estimate_error",
                    "default": 1.0,
                },
            },
            "process_variance": {
                "kind": "number",
                "name": "process_variance",
                "widget": {
                    "kind": "number",
                    "name": "process_variance",
                    "default": 0.01,
                },
            },
            "measurement_variance": {
                "kind": "number",
                "name": "measurement_variance",
                "widget": {
                    "kind": "number",
                    "name": "measurement_variance",
                    "default": 0.1,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        measurements = (
            node_inputs.get("required_inputs", {})
            .get("measurements", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        initial_state = (
            node_inputs.get("required_inputs", {})
            .get("initial_state", {})
            .get("values", 0.0)
        )
        initial_estimate_error = (
            node_inputs.get("required_inputs", {})
            .get("initial_estimate_error", {})
            .get("values", 1.0)
        )
        process_variance = (
            node_inputs.get("required_inputs", {})
            .get("process_variance", {})
            .get("values", 0.01)
        )
        measurement_variance = (
            node_inputs.get("required_inputs", {})
            .get("measurement_variance", {})
            .get("values", 0.1)
        )
        try:

            def kalman_filter(z, x0, P0, Q, R):
                x = x0
                P = P0
                estimates = []

                for z_k in z:
                    # Predict
                    x = x
                    P = P + Q

                    # Update
                    K = P / (P + R)
                    x = x + K * (z_k - x)
                    P = (1 - K) * P

                    estimates.append(x)

                return estimates

            filtered_states = kalman_filter(
                measurements,
                initial_state,
                initial_estimate_error,
                process_variance,
                measurement_variance,
            )
            return {"result": filtered_states}
        except Exception as e:
            return {"error": str(e)}


class ParticleFilter:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Implements a particle filter for state estimation."

    INPUT = {
        "required_inputs": {
            "observations": {
                "kind": "array",
                "name": "observations",
                "widget": {
                    "kind": "array",
                    "name": "observations",
                    "default": [1.0, 2.0, 3.0, 4.0, 5.0],
                },
            },
            "num_particles": {
                "kind": "number",
                "name": "num_particles",
                "widget": {"kind": "number", "name": "num_particles", "default": 100},
            },
            "process_noise": {
                "kind": "number",
                "name": "process_noise",
                "widget": {"kind": "number", "name": "process_noise", "default": 0.1},
            },
            "measurement_noise": {
                "kind": "number",
                "name": "measurement_noise",
                "widget": {
                    "kind": "number",
                    "name": "measurement_noise",
                    "default": 0.1,
                },
            },
            "initial_state_mean": {
                "kind": "number",
                "name": "initial_state_mean",
                "widget": {
                    "kind": "number",
                    "name": "initial_state_mean",
                    "default": 0.0,
                },
            },
            "initial_state_std": {
                "kind": "number",
                "name": "initial_state_std",
                "widget": {
                    "kind": "number",
                    "name": "initial_state_std",
                    "default": 1.0,
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        observations = (
            node_inputs.get("required_inputs", {})
            .get("observations", {})
            .get("values", [1.0, 2.0, 3.0, 4.0, 5.0])
        )
        num_particles = (
            node_inputs.get("required_inputs", {})
            .get("num_particles", {})
            .get("values", 100)
        )
        process_noise = (
            node_inputs.get("required_inputs", {})
            .get("process_noise", {})
            .get("values", 0.1)
        )
        measurement_noise = (
            node_inputs.get("required_inputs", {})
            .get("measurement_noise", {})
            .get("values", 0.1)
        )
        initial_state_mean = (
            node_inputs.get("required_inputs", {})
            .get("initial_state_mean", {})
            .get("values", 0.0)
        )
        initial_state_std = (
            node_inputs.get("required_inputs", {})
            .get("initial_state_std", {})
            .get("values", 1.0)
        )

        try:
            import numpy as np

            def particle_filter(
                observations,
                num_particles,
                process_noise,
                measurement_noise,
                initial_state_mean,
                initial_state_std,
            ):
                # Initialize particles
                particles = np.random.normal(
                    initial_state_mean, initial_state_std, num_particles
                )
                weights = np.ones(num_particles) / num_particles
                estimates = []

                for observation in observations:
                    # Predict
                    particles = particles + np.random.normal(
                        0, process_noise, num_particles
                    )

                    # Update weights
                    weights *= np.exp(
                        -0.5 * ((observation - particles) / measurement_noise) ** 2
                    )
                    weights /= np.sum(weights)

                    # Resample
                    if 1.0 / np.sum(weights**2) < num_particles / 2:
                        indices = np.random.choice(
                            num_particles, num_particles, p=weights
                        )
                        particles = particles[indices]
                        weights = np.ones(num_particles) / num_particles

                    # Estimate
                    estimate = np.sum(particles * weights)
                    estimates.append(estimate)

                return estimates

            result = particle_filter(
                observations,
                num_particles,
                process_noise,
                measurement_noise,
                initial_state_mean,
                initial_state_std,
            )
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


class SphericalHarmonics:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the spherical harmonics for given degree and order."

    INPUT = {
        "required_inputs": {
            "degree": {
                "kind": "number",
                "name": "degree",
                "widget": {"kind": "number", "name": "degree", "default": 2},
            },
            "order": {
                "kind": "number",
                "name": "order",
                "widget": {"kind": "number", "name": "order", "default": 1},
            },
            "theta": {
                "kind": "number",
                "name": "theta",
                "widget": {"kind": "number", "name": "theta", "default": 0.0},
            },
            "phi": {
                "kind": "number",
                "name": "phi",
                "widget": {"kind": "number", "name": "phi", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "complex",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        degree = (
            node_inputs.get("required_inputs", {}).get("degree", {}).get("values", 2)
        )
        order = node_inputs.get("required_inputs", {}).get("order", {}).get("values", 1)
        theta = (
            node_inputs.get("required_inputs", {}).get("theta", {}).get("values", 0.0)
        )
        phi = node_inputs.get("required_inputs", {}).get("phi", {}).get("values", 0.0)
        try:
            from scipy.special import sph_harm

            result = sph_harm(order, degree, phi, theta)
            return {"result": complex(result)}
        except Exception as e:
            return {"error": str(e)}


class LegendreTransform:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Legendre transform of a function."

    INPUT = {
        "required_inputs": {
            "function": {
                "kind": "string",
                "name": "function",
                "widget": {
                    "kind": "string",
                    "name": "function",
                    "default": "lambda x: x**2",
                },
            },
            "x_min": {
                "kind": "number",
                "name": "x_min",
                "widget": {"kind": "number", "name": "x_min", "default": -1.0},
            },
            "x_max": {
                "kind": "number",
                "name": "x_max",
                "widget": {"kind": "number", "name": "x_max", "default": 1.0},
            },
            "num_points": {
                "kind": "number",
                "name": "num_points",
                "widget": {"kind": "number", "name": "num_points", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        function_str = (
            node_inputs.get("required_inputs", {})
            .get("function", {})
            .get("values", "lambda x: x**2")
        )
        x_min = (
            node_inputs.get("required_inputs", {}).get("x_min", {}).get("values", -1.0)
        )
        x_max = (
            node_inputs.get("required_inputs", {}).get("x_max", {}).get("values", 1.0)
        )
        num_points = (
            node_inputs.get("required_inputs", {})
            .get("num_points", {})
            .get("values", 100)
        )
        try:
            import numpy as np
            from scipy.special import legendre

            f = eval(function_str)
            x = np.linspace(x_min, x_max, num_points)
            y = f(x)

            coeffs = np.zeros(num_points)
            for n in range(num_points):
                P = legendre(n)
                coeffs[n] = (
                    (2 * n + 1) / 2 * np.sum(y * P(x)) * (x_max - x_min) / num_points
                )

            return {"result": coeffs.tolist()}
        except Exception as e:
            return {"error": str(e)}


class BesselZeros:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the zeros of the Bessel function of the first kind."

    INPUT = {
        "required_inputs": {
            "order": {
                "kind": "number",
                "name": "order",
                "widget": {"kind": "number", "name": "order", "default": 0},
            },
            "num_zeros": {
                "kind": "number",
                "name": "num_zeros",
                "widget": {"kind": "number", "name": "num_zeros", "default": 5},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        order = node_inputs.get("required_inputs", {}).get("order", {}).get("values", 0)
        num_zeros = (
            node_inputs.get("required_inputs", {}).get("num_zeros", {}).get("values", 5)
        )
        try:
            from scipy.special import jn_zeros

            zeros = jn_zeros(order, num_zeros)
            return {"result": zeros.tolist()}
        except Exception as e:
            return {"error": str(e)}


class AiryFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Airy function for a given value."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0.0},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0.0)
        try:
            from scipy.special import airy

            ai, aip, bi, bip = airy(x)
            return {"result": [float(ai), float(aip), float(bi), float(bip)]}
        except Exception as e:
            return {"error": str(e)}


class WeierstrassFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Weierstrass function for a given value."

    INPUT = {
        "required_inputs": {
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0.0},
            },
            "a": {
                "kind": "number",
                "name": "a",
                "widget": {"kind": "number", "name": "a", "default": 0.5},
            },
            "b": {
                "kind": "number",
                "name": "b",
                "widget": {"kind": "number", "name": "b", "default": 3.0},
            },
            "n_terms": {
                "kind": "number",
                "name": "n_terms",
                "widget": {"kind": "number", "name": "n_terms", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0.0)
        a = node_inputs.get("required_inputs", {}).get("a", {}).get("values", 0.5)
        b = node_inputs.get("required_inputs", {}).get("b", {}).get("values", 3.0)
        n_terms = (
            node_inputs.get("required_inputs", {}).get("n_terms", {}).get("values", 100)
        )
        try:
            import numpy as np

            result = sum(a**n * np.cos(b**n * np.pi * x) for n in range(n_terms))
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class LaméFunction:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Lamé function for given parameters."

    INPUT = {
        "required_inputs": {
            "n": {
                "kind": "number",
                "name": "n",
                "widget": {"kind": "number", "name": "n", "default": 2},
            },
            "m": {
                "kind": "number",
                "name": "m",
                "widget": {"kind": "number", "name": "m", "default": 1},
            },
            "x": {
                "kind": "number",
                "name": "x",
                "widget": {"kind": "number", "name": "x", "default": 0.5},
            },
            "k": {
                "kind": "number",
                "name": "k",
                "widget": {"kind": "number", "name": "k", "default": 0.5},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        n = node_inputs.get("required_inputs", {}).get("n", {}).get("values", 2)
        m = node_inputs.get("required_inputs", {}).get("m", {}).get("values", 1)
        x = node_inputs.get("required_inputs", {}).get("x", {}).get("values", 0.5)
        k = node_inputs.get("required_inputs", {}).get("k", {}).get("values", 0.5)
        try:
            from scipy.special import ellipj

            sn, cn, dn, _ = ellipj(x, k**2)
            if m == 1:
                result = cn * dn ** (n - 1)
            elif m == 2:
                result = sn * dn ** (n - 1)
            elif m == 3:
                result = sn * cn * dn ** (n - 2)
            else:
                raise ValueError("m must be 1, 2, or 3")
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class MinkowskiDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the Minkowski distance between two points in a normed vector space."
    )

    INPUT = {
        "required_inputs": {
            "point1": {
                "kind": "array",
                "name": "point1",
                "widget": {"kind": "array", "name": "point1", "default": [0, 0, 0]},
            },
            "point2": {
                "kind": "array",
                "name": "point2",
                "widget": {"kind": "array", "name": "point2", "default": [1, 1, 1]},
            },
            "p": {
                "kind": "number",
                "name": "p",
                "widget": {"kind": "number", "name": "p", "default": 2.0},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        point1 = (
            node_inputs.get("required_inputs", {})
            .get("point1", {})
            .get("values", [0, 0, 0])
        )
        point2 = (
            node_inputs.get("required_inputs", {})
            .get("point2", {})
            .get("values", [1, 1, 1])
        )
        p = node_inputs.get("required_inputs", {}).get("p", {}).get("values", 2.0)
        try:
            import numpy as np

            distance = np.linalg.norm(np.array(point1) - np.array(point2), ord=p)
            return {"result": float(distance)}
        except Exception as e:
            return {"error": str(e)}


class ChebyshevDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Chebyshev distance between two points."

    INPUT = {
        "required_inputs": {
            "point1": {
                "kind": "array",
                "name": "point1",
                "widget": {"kind": "array", "name": "point1", "default": [0, 0, 0]},
            },
            "point2": {
                "kind": "array",
                "name": "point2",
                "widget": {"kind": "array", "name": "point2", "default": [1, 1, 1]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        point1 = (
            node_inputs.get("required_inputs", {})
            .get("point1", {})
            .get("values", [0, 0, 0])
        )
        point2 = (
            node_inputs.get("required_inputs", {})
            .get("point2", {})
            .get("values", [1, 1, 1])
        )
        try:
            import numpy as np

            distance = np.max(np.abs(np.array(point1) - np.array(point2)))
            return {"result": float(distance)}
        except Exception as e:
            return {"error": str(e)}


class MahalanobisDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the Mahalanobis distance between a point and a distribution."
    )

    INPUT = {
        "required_inputs": {
            "point": {
                "kind": "array",
                "name": "point",
                "widget": {"kind": "array", "name": "point", "default": [0, 0, 0]},
            },
            "mean": {
                "kind": "array",
                "name": "mean",
                "widget": {"kind": "array", "name": "mean", "default": [1, 1, 1]},
            },
            "cov": {
                "kind": "array",
                "name": "cov",
                "widget": {
                    "kind": "array",
                    "name": "cov",
                    "default": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        point = (
            node_inputs.get("required_inputs", {})
            .get("point", {})
            .get("values", [0, 0, 0])
        )
        mean = (
            node_inputs.get("required_inputs", {})
            .get("mean", {})
            .get("values", [1, 1, 1])
        )
        cov = (
            node_inputs.get("required_inputs", {})
            .get("cov", {})
            .get("values", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        )
        try:
            import numpy as np
            from scipy.spatial.distance import mahalanobis

            distance = mahalanobis(point, mean, np.linalg.inv(cov))
            return {"result": float(distance)}
        except Exception as e:
            return {"error": str(e)}


class JaccardIndex:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Jaccard index between two sets."

    INPUT = {
        "required_inputs": {
            "set1": {
                "kind": "array",
                "name": "set1",
                "widget": {"kind": "array", "name": "set1", "default": [1, 2, 3]},
            },
            "set2": {
                "kind": "array",
                "name": "set2",
                "widget": {"kind": "array", "name": "set2", "default": [2, 3, 4]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        set1 = (
            node_inputs.get("required_inputs", {})
            .get("set1", {})
            .get("values", [1, 2, 3])
        )
        set2 = (
            node_inputs.get("required_inputs", {})
            .get("set2", {})
            .get("values", [2, 3, 4])
        )
        try:
            set1 = set(set1)
            set2 = set(set2)
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            jaccard_index = intersection / union if union != 0 else 0
            return {"result": float(jaccard_index)}
        except Exception as e:
            return {"error": str(e)}


class CosineSimilarity:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cosine similarity between two vectors."

    INPUT = {
        "required_inputs": {
            "vector1": {
                "kind": "array",
                "name": "vector1",
                "widget": {"kind": "array", "name": "vector1", "default": [1, 2, 3]},
            },
            "vector2": {
                "kind": "array",
                "name": "vector2",
                "widget": {"kind": "array", "name": "vector2", "default": [4, 5, 6]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        vector1 = (
            node_inputs.get("required_inputs", {})
            .get("vector1", {})
            .get("values", [1, 2, 3])
        )
        vector2 = (
            node_inputs.get("required_inputs", {})
            .get("vector2", {})
            .get("values", [4, 5, 6])
        )
        try:
            import numpy as np

            cosine_similarity = np.dot(vector1, vector2) / (
                np.linalg.norm(vector1) * np.linalg.norm(vector2)
            )
            return {"result": float(cosine_similarity)}
        except Exception as e:
            return {"error": str(e)}


class HammingDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Hamming distance between two strings or vectors."

    INPUT = {
        "required_inputs": {
            "input1": {
                "kind": "string",
                "name": "input1",
                "widget": {"kind": "string", "name": "input1", "default": "hello"},
            },
            "input2": {
                "kind": "string",
                "name": "input2",
                "widget": {"kind": "string", "name": "input2", "default": "world"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        input1 = (
            node_inputs.get("required_inputs", {})
            .get("input1", {})
            .get("values", "hello")
        )
        input2 = (
            node_inputs.get("required_inputs", {})
            .get("input2", {})
            .get("values", "world")
        )
        try:
            if len(input1) != len(input2):
                raise ValueError("Inputs must have the same length")
            hamming_distance = sum(c1 != c2 for c1, c2 in zip(input1, input2))
            return {"result": int(hamming_distance)}
        except Exception as e:
            return {"error": str(e)}


class EditDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the edit distance (Levenshtein distance) between two strings."
    )

    INPUT = {
        "required_inputs": {
            "string1": {
                "kind": "string",
                "name": "string1",
                "widget": {"kind": "string", "name": "string1", "default": "kitten"},
            },
            "string2": {
                "kind": "string",
                "name": "string2",
                "widget": {"kind": "string", "name": "string2", "default": "sitting"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        string1 = (
            node_inputs.get("required_inputs", {})
            .get("string1", {})
            .get("values", "kitten")
        )
        string2 = (
            node_inputs.get("required_inputs", {})
            .get("string2", {})
            .get("values", "sitting")
        )
        try:
            import numpy as np

            m, n = len(string1), len(string2)
            d = np.zeros((m + 1, n + 1), dtype=int)
            d[0, :] = np.arange(n + 1)
            d[:, 0] = np.arange(m + 1)
            for i in range(1, m + 1):
                for j in range(1, n + 1):
                    cost = 0 if string1[i - 1] == string2[j - 1] else 1
                    d[i, j] = min(
                        d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + cost
                    )
            return {"result": int(d[m, n])}
        except Exception as e:
            return {"error": str(e)}


class KullbackLeiblerDivergence:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Kullback-Leibler divergence between two probability distributions."

    INPUT = {
        "required_inputs": {
            "p": {
                "kind": "array",
                "name": "p",
                "widget": {"kind": "array", "name": "p", "default": [0.5, 0.5]},
            },
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [0.1, 0.9]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        p = (
            node_inputs.get("required_inputs", {})
            .get("p", {})
            .get("values", [0.5, 0.5])
        )
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [0.1, 0.9])
        )
        try:
            from scipy.stats import entropy

            kl_divergence = entropy(p, q)
            return {"result": float(kl_divergence)}
        except Exception as e:
            return {"error": str(e)}


class BhattacharyyaDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = (
        "Computes the Bhattacharyya distance between two probability distributions."
    )

    INPUT = {
        "required_inputs": {
            "p": {
                "kind": "array",
                "name": "p",
                "widget": {"kind": "array", "name": "p", "default": [0.5, 0.5]},
            },
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [0.1, 0.9]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        p = (
            node_inputs.get("required_inputs", {})
            .get("p", {})
            .get("values", [0.5, 0.5])
        )
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [0.1, 0.9])
        )
        try:
            import numpy as np

            bc_coeff = np.sum(np.sqrt(np.multiply(p, q)))
            bhattacharyya_distance = -np.log(bc_coeff)
            return {"result": float(bhattacharyya_distance)}
        except Exception as e:
            return {"error": str(e)}


class EarthMoverDistance:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Earth Mover's Distance (Wasserstein distance) between two probability distributions."

    INPUT = {
        "required_inputs": {
            "p": {
                "kind": "array",
                "name": "p",
                "widget": {"kind": "array", "name": "p", "default": [0.5, 0.5]},
            },
            "q": {
                "kind": "array",
                "name": "q",
                "widget": {"kind": "array", "name": "q", "default": [0.1, 0.9]},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        p = (
            node_inputs.get("required_inputs", {})
            .get("p", {})
            .get("values", [0.5, 0.5])
        )
        q = (
            node_inputs.get("required_inputs", {})
            .get("q", {})
            .get("values", [0.1, 0.9])
        )
        try:
            import numpy as np
            from scipy.stats import wasserstein_distance

            emd = wasserstein_distance(np.arange(len(p)), np.arange(len(q)), p, q)
            return {"result": float(emd)}
        except Exception as e:
            return {"error": str(e)}


class EntropyShannon:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Shannon entropy of a probability distribution."

    INPUT = {
        "required_inputs": {
            "probabilities": {
                "kind": "array",
                "name": "probabilities",
                "widget": {
                    "kind": "array",
                    "name": "probabilities",
                    "default": [0.5, 0.5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        probabilities = (
            node_inputs.get("required_inputs", {})
            .get("probabilities", {})
            .get("values", [0.5, 0.5])
        )
        try:
            import numpy as np

            entropy = -np.sum(np.multiply(probabilities, np.log2(probabilities)))
            return {"result": float(entropy)}
        except Exception as e:
            return {"error": str(e)}


class GiniCoefficient:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Gini coefficient for a list of values, often used to measure inequality."

    INPUT = {
        "required_inputs": {
            "values": {
                "kind": "array",
                "name": "values",
                "widget": {
                    "kind": "array",
                    "name": "values",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        values = (
            node_inputs.get("required_inputs", {})
            .get("values", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            sorted_values = np.sort(values)
            index = np.arange(1, len(values) + 1)
            n = len(values)
            return {
                "result": float(
                    (np.sum((2 * index - n - 1) * sorted_values))
                    / (n * np.sum(sorted_values))
                )
            }
        except Exception as e:
            return {"error": str(e)}


class LorenzCurve:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Lorenz curve for a distribution, used in economics to represent inequality."

    INPUT = {
        "required_inputs": {
            "values": {
                "kind": "array",
                "name": "values",
                "widget": {
                    "kind": "array",
                    "name": "values",
                    "default": [1, 2, 3, 4, 5],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        values = (
            node_inputs.get("required_inputs", {})
            .get("values", {})
            .get("values", [1, 2, 3, 4, 5])
        )
        try:
            import numpy as np

            sorted_values = np.sort(values)
            cumsum = np.cumsum(sorted_values)
            return {"result": (np.insert(cumsum, 0, 0) / cumsum[-1]).tolist()}
        except Exception as e:
            return {"error": str(e)}


class PageRank:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the PageRank of nodes in a graph, used in network analysis."

    INPUT = {
        "required_inputs": {
            "adjacency_matrix": {
                "kind": "array",
                "name": "adjacency_matrix",
                "widget": {
                    "kind": "array",
                    "name": "adjacency_matrix",
                    "default": [[0, 1], [1, 0]],
                },
            },
            "damping_factor": {
                "kind": "number",
                "name": "damping_factor",
                "widget": {"kind": "number", "name": "damping_factor", "default": 0.85},
            },
            "num_iterations": {
                "kind": "number",
                "name": "num_iterations",
                "widget": {"kind": "number", "name": "num_iterations", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        adjacency_matrix = (
            node_inputs.get("required_inputs", {})
            .get("adjacency_matrix", {})
            .get("values", [[0, 1], [1, 0]])
        )
        damping_factor = (
            node_inputs.get("required_inputs", {})
            .get("damping_factor", {})
            .get("values", 0.85)
        )
        num_iterations = (
            node_inputs.get("required_inputs", {})
            .get("num_iterations", {})
            .get("values", 100)
        )
        try:
            import numpy as np

            n = len(adjacency_matrix)
            M = np.array(adjacency_matrix, dtype=float)
            M = M / M.sum(axis=0)
            v = np.ones(n) / n
            for _ in range(num_iterations):
                v = damping_factor * M.dot(v) + (1 - damping_factor) / n
            return {"result": v.tolist()}
        except Exception as e:
            return {"error": str(e)}


class SpectralRadius:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the spectral radius of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            eigenvalues = np.linalg.eigvals(matrix)
            spectral_radius = np.max(np.abs(eigenvalues))
            return {"result": float(spectral_radius)}
        except Exception as e:
            return {"error": str(e)}


class MatrixExponential:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the exponential of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np
            from scipy.linalg import expm

            result = expm(np.array(matrix))
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class FrobeniusNorm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Frobenius norm of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            frobenius_norm = np.linalg.norm(matrix, "fro")
            return {"result": float(frobenius_norm)}
        except Exception as e:
            return {"error": str(e)}


class HouseholderTransformation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Householder transformation for a vector."

    INPUT = {
        "required_inputs": {
            "vector": {
                "kind": "array",
                "name": "vector",
                "widget": {"kind": "array", "name": "vector", "default": [1, 2, 3]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        vector = (
            node_inputs.get("required_inputs", {})
            .get("vector", {})
            .get("values", [1, 2, 3])
        )
        try:
            import numpy as np

            x = np.array(vector)
            v = x / (x[0] + np.copysign(np.linalg.norm(x), x[0]))
            v[0] = 1
            H = np.eye(len(x)) - (2 / np.dot(v, v)) * np.outer(v, v)
            return {"result": H.tolist()}
        except Exception as e:
            return {"error": str(e)}


class GramSchmidtProcess:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Performs the Gram-Schmidt process on a set of vectors."

    INPUT = {
        "required_inputs": {
            "vectors": {
                "kind": "array",
                "name": "vectors",
                "widget": {
                    "kind": "array",
                    "name": "vectors",
                    "default": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        vectors = (
            node_inputs.get("required_inputs", {})
            .get("vectors", {})
            .get("values", [[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        )
        try:
            import numpy as np

            V = np.array(vectors)
            n = V.shape[1]
            U = np.zeros_like(V)
            U[:, 0] = V[:, 0] / np.linalg.norm(V[:, 0])
            for i in range(1, n):
                U[:, i] = V[:, i]
                for j in range(i):
                    U[:, i] -= np.dot(U[:, j], V[:, i]) * U[:, j]
                U[:, i] /= np.linalg.norm(U[:, i])
            return {"result": U.tolist()}
        except Exception as e:
            return {"error": str(e)}


class QRAlgorithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the eigenvalues of a matrix using the QR algorithm."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
            "num_iterations": {
                "kind": "number",
                "name": "num_iterations",
                "widget": {"kind": "number", "name": "num_iterations", "default": 100},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        num_iterations = (
            node_inputs.get("required_inputs", {})
            .get("num_iterations", {})
            .get("values", 100)
        )
        try:
            import numpy as np

            A = np.array(matrix)
            for _ in range(num_iterations):
                Q, R = np.linalg.qr(A)
                A = np.dot(R, Q)
            eigenvalues = np.diag(A)
            return {"result": eigenvalues.tolist()}
        except Exception as e:
            return {"error": str(e)}


class CholeskyFactorization:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Cholesky factorization of a positive-definite matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 0], [0, 1]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 0], [0, 1]])
        )
        try:
            import numpy as np

            L = np.linalg.cholesky(matrix)
            return {"result": L.tolist()}
        except Exception as e:
            return {"error": str(e)}


class LUFactorization:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the LU factorization of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            from scipy import linalg

            P, L, U = linalg.lu(matrix)
            return {"result": {"P": P.tolist(), "L": L.tolist(), "U": U.tolist()}}
        except Exception as e:
            return {"error": str(e)}


class QRFactorization:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the QR factorization of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            Q, R = np.linalg.qr(matrix)
            return {"result": {"Q": Q.tolist(), "R": R.tolist()}}
        except Exception as e:
            return {"error": str(e)}


class EigenDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the eigenvalues and eigenvectors of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            eigenvalues, eigenvectors = np.linalg.eig(matrix)
            return {
                "result": {
                    "eigenvalues": eigenvalues.tolist(),
                    "eigenvectors": eigenvectors.tolist(),
                }
            }
        except Exception as e:
            return {"error": str(e)}


class MatrixConditionNumber:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the condition number of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            cond = np.linalg.cond(matrix)
            return {"result": float(cond)}
        except Exception as e:
            return {"error": str(e)}


class MatrixNullSpace:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the null space of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            from scipy import linalg

            null_space = linalg.null_space(matrix)
            return {"result": null_space.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixColumnSpace:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the column space of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np
            from scipy import linalg

            Q, _ = linalg.qr(matrix)
            rank = np.linalg.matrix_rank(matrix)
            column_space = Q[:, :rank]
            return {"result": column_space.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixRowSpace:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the row space of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np
            from scipy import linalg

            Q, _ = linalg.qr(np.array(matrix).T)
            rank = np.linalg.matrix_rank(matrix)
            row_space = Q[:, :rank].T
            return {"result": row_space.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixAdjugate:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the adjugate (adjoint) of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            adj = np.linalg.inv(matrix).T * np.linalg.det(matrix)
            return {"result": adj.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixCofactor:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the cofactor matrix of a given matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            det = np.linalg.det(matrix)
            inv = np.linalg.inv(matrix)
            cofactor = det * inv.T
            return {"result": cofactor.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixHadamardProduct:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Hadamard (element-wise) product of two matrices."

    INPUT = {
        "required_inputs": {
            "matrix1": {
                "kind": "array",
                "name": "matrix1",
                "widget": {
                    "kind": "array",
                    "name": "matrix1",
                    "default": [[1, 2], [3, 4]],
                },
            },
            "matrix2": {
                "kind": "array",
                "name": "matrix2",
                "widget": {
                    "kind": "array",
                    "name": "matrix2",
                    "default": [[5, 6], [7, 8]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix1 = (
            node_inputs.get("required_inputs", {})
            .get("matrix1", {})
            .get("values", [[1, 2], [3, 4]])
        )
        matrix2 = (
            node_inputs.get("required_inputs", {})
            .get("matrix2", {})
            .get("values", [[5, 6], [7, 8]])
        )
        try:
            import numpy as np

            result = np.multiply(matrix1, matrix2)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixKroneckerProduct:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Kronecker product of two matrices."

    INPUT = {
        "required_inputs": {
            "matrix1": {
                "kind": "array",
                "name": "matrix1",
                "widget": {
                    "kind": "array",
                    "name": "matrix1",
                    "default": [[1, 2], [3, 4]],
                },
            },
            "matrix2": {
                "kind": "array",
                "name": "matrix2",
                "widget": {
                    "kind": "array",
                    "name": "matrix2",
                    "default": [[5, 6], [7, 8]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix1 = (
            node_inputs.get("required_inputs", {})
            .get("matrix1", {})
            .get("values", [[1, 2], [3, 4]])
        )
        matrix2 = (
            node_inputs.get("required_inputs", {})
            .get("matrix2", {})
            .get("values", [[5, 6], [7, 8]])
        )
        try:
            import numpy as np

            result = np.kron(matrix1, matrix2)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixTrace:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the trace of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            result = np.trace(matrix)
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class MatrixPower:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Raises a matrix to a given power."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
            "power": {
                "kind": "number",
                "name": "power",
                "widget": {"kind": "number", "name": "power", "default": 2},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        power = node_inputs.get("required_inputs", {}).get("power", {}).get("values", 2)
        try:
            import numpy as np

            result = np.linalg.matrix_power(matrix, power)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixLogarithm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the matrix logarithm."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import scipy.linalg

            result = scipy.linalg.logm(matrix)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixSquareRoot:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the square root of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import scipy.linalg

            result = scipy.linalg.sqrtm(matrix)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixExponentialMap:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the exponential map of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import scipy.linalg

            result = scipy.linalg.expm(matrix)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixLogarithmMap:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the logarithm map of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import scipy.linalg

            result = scipy.linalg.logm(matrix)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixPseudoinverse:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Moore-Penrose pseudoinverse of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            result = np.linalg.pinv(matrix)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class ToeplitzMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Constructs a Toeplitz matrix from a given vector."

    INPUT = {
        "required_inputs": {
            "vector": {
                "kind": "array",
                "name": "vector",
                "widget": {"kind": "array", "name": "vector", "default": [1, 2, 3, 4]},
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        vector = (
            node_inputs.get("required_inputs", {})
            .get("vector", {})
            .get("values", [1, 2, 3, 4])
        )
        try:
            from scipy.linalg import toeplitz

            result = toeplitz(vector)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class VandermondeMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Constructs a Vandermonde matrix from a given vector."

    INPUT = {
        "required_inputs": {
            "vector": {
                "kind": "array",
                "name": "vector",
                "widget": {"kind": "array", "name": "vector", "default": [1, 2, 3, 4]},
            },
            "degree": {
                "kind": "number",
                "name": "degree",
                "widget": {"kind": "number", "name": "degree", "default": 3},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        vector = (
            node_inputs.get("required_inputs", {})
            .get("vector", {})
            .get("values", [1, 2, 3, 4])
        )
        degree = (
            node_inputs.get("required_inputs", {}).get("degree", {}).get("values", 3)
        )
        try:
            import numpy as np

            result = np.vander(vector, degree + 1)
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class HilbertMatrix:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Constructs a Hilbert matrix of a specified size."

    INPUT = {
        "required_inputs": {
            "size": {
                "kind": "number",
                "name": "size",
                "widget": {"kind": "number", "name": "size", "default": 3},
            }
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        size = node_inputs.get("required_inputs", {}).get("size", {}).get("values", 3)
        try:
            import numpy as np

            result = np.array(
                [[1 / (i + j + 1) for j in range(size)] for i in range(size)]
            )
            return {"result": result.tolist()}
        except Exception as e:
            return {"error": str(e)}


class CayleyHamiltonTheorem:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Verifies the Cayley-Hamilton theorem for a given matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np

            A = np.array(matrix)
            char_poly = np.poly(A)
            n = A.shape[0]
            result = np.zeros_like(A)
            for i in range(n + 1):
                result += char_poly[i] * np.linalg.matrix_power(A, n - i)
            is_verified = np.allclose(result, np.zeros_like(A))
            return {"result": {"is_verified": is_verified, "residual": result.tolist()}}
        except Exception as e:
            return {"error": str(e)}


class MatrixNorm:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes various norms (e.g., L1, L2, infinity) of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            },
            "norm_type": {
                "kind": "string",
                "name": "norm_type",
                "widget": {"kind": "string", "name": "norm_type", "default": "fro"},
            },
        },
    }

    OUTPUT = {
        "kind": "number",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        norm_type = (
            node_inputs.get("required_inputs", {})
            .get("norm_type", {})
            .get("values", "fro")
        )
        try:
            import numpy as np

            result = np.linalg.norm(matrix, ord=norm_type)
            return {"result": float(result)}
        except Exception as e:
            return {"error": str(e)}


class MatrixPolarDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the polar decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            import numpy as np
            from scipy.linalg import polar

            A = np.array(matrix)
            U, P = polar(A)
            return {
                "result": {"unitary": U.tolist(), "positive_semidefinite": P.tolist()}
            }
        except Exception as e:
            return {"error": str(e)}


class MatrixSchurDecomposition:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Computes the Schur decomposition of a matrix."

    INPUT = {
        "required_inputs": {
            "matrix": {
                "kind": "array",
                "name": "matrix",
                "widget": {
                    "kind": "array",
                    "name": "matrix",
                    "default": [[1, 2], [3, 4]],
                },
            }
        },
    }

    OUTPUT = {
        "kind": "object",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        matrix = (
            node_inputs.get("required_inputs", {})
            .get("matrix", {})
            .get("values", [[1, 2], [3, 4]])
        )
        try:
            from scipy.linalg import schur

            T, Z = schur(matrix)
            return {"result": {"T": T.tolist(), "Z": Z.tolist()}}
        except Exception as e:
            return {"error": str(e)}


class MatrixSylvesterEquation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Solves the Sylvester equation for given matrices."

    INPUT = {
        "required_inputs": {
            "A": {
                "kind": "array",
                "name": "A",
                "widget": {"kind": "array", "name": "A", "default": [[1, 2], [3, 4]]},
            },
            "B": {
                "kind": "array",
                "name": "B",
                "widget": {"kind": "array", "name": "B", "default": [[5, 6], [7, 8]]},
            },
            "C": {
                "kind": "array",
                "name": "C",
                "widget": {
                    "kind": "array",
                    "name": "C",
                    "default": [[9, 10], [11, 12]],
                },
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        A = (
            node_inputs.get("required_inputs", {})
            .get("A", {})
            .get("values", [[1, 2], [3, 4]])
        )
        B = (
            node_inputs.get("required_inputs", {})
            .get("B", {})
            .get("values", [[5, 6], [7, 8]])
        )
        C = (
            node_inputs.get("required_inputs", {})
            .get("C", {})
            .get("values", [[9, 10], [11, 12]])
        )
        try:
            from scipy.linalg import solve_sylvester

            X = solve_sylvester(A, B, C)
            return {"result": X.tolist()}
        except Exception as e:
            return {"error": str(e)}


class MatrixLyapunovEquation:
    CATEGORY = "numerics"
    SUBCATEGORY = "advanced"
    DESCRIPTION = "Solves the Lyapunov equation for given matrices."

    INPUT = {
        "required_inputs": {
            "A": {
                "kind": "array",
                "name": "A",
                "widget": {"kind": "array", "name": "A", "default": [[1, 2], [3, 4]]},
            },
            "Q": {
                "kind": "array",
                "name": "Q",
                "widget": {"kind": "array", "name": "Q", "default": [[5, 6], [7, 8]]},
            },
        },
    }

    OUTPUT = {
        "kind": "array",
        "name": "result",
        "cacheable": True,
    }

    def evaluate(self, node_inputs):
        A = (
            node_inputs.get("required_inputs", {})
            .get("A", {})
            .get("values", [[1, 2], [3, 4]])
        )
        Q = (
            node_inputs.get("required_inputs", {})
            .get("Q", {})
            .get("values", [[5, 6], [7, 8]])
        )
        try:
            from scipy.linalg import solve_lyapunov

            X = solve_lyapunov(A, -Q)
            return {"result": X.tolist()}
        except Exception as e:
            return {"error": str(e)}


# Hook Functions
EXTENSION_MAPPINGS = {
    "name": "core",
    "version": version,
    "description": "core language nodes",
    "javascript_class_name": "NeoScaffoldCore",
    "nodes": {
        # Primitives
        "nsString": {
            "python_class": nsString,
            "javascript_class_name": "nsString",
            "display_name": "String",
        },
        "nsBoolean": {
            "python_class": nsBoolean,
            "javascript_class_name": "nsBoolean",
            "display_name": "Boolean",
        },
        "nsInteger": {
            "python_class": nsInteger,
            "javascript_class_name": "nsInteger",
            "display_name": "Integer",
        },
        "nsFloat": {
            "python_class": nsFloat,
            "javascript_class_name": "nsFloat",
            "display_name": "Float",
        },
        "nsNull": {
            "python_class": nsNull,
            "javascript_class_name": "nsNull",
            "display_name": "Null",
        },
        "nsHashMap": {
            "python_class": nsHashMap,
            "javascript_class_name": "nsHashMap",
            "display_name": "HashMap",
        },
        "nsArray": {
            "python_class": nsArray,
            "javascript_class_name": "nsArray",
            "display_name": "Array",
        },
        "nsArrayAppend": {
            "python_class": nsArrayAppend,
            "javascript_class_name": "nsArrayAppend",
            "display_name": "ArrayAppend",
        },
        "IfEqual": {
            "python_class": IfEqual,
            "javascript_class_name": "IfEqual",
            "display_name": "IfEqual",
        },
        "IfEqualTrue": {
            "python_class": IfEqualTrue,
            "javascript_class_name": "IfEqualTrue",
            "display_name": "IfEqualTrue",
        },
        "IfEqualFalse": {
            "python_class": IfEqualFalse,
            "javascript_class_name": "IfEqualFalse",
            "display_name": "IfEqualFalse",
        },
        "EndIfEqual": {
            "python_class": EndIfEqual,
            "javascript_class_name": "EndIfEqual",
            "display_name": "EndIfEqual",
        },
        "WhileLoop": {
            "python_class": WhileLoop,
            "javascript_class_name": "WhileLoop",
            "display_name": "WhileLoop",
        },
        "BreakWhileLoop": {
            "python_class": BreakWhileLoop,
            "javascript_class_name": "BreakWhileLoop",
            "display_name": "BreakWhileLoop",
        },
        "ContinueWhileLoop": {
            "python_class": ContinueWhileLoop,
            "javascript_class_name": "ContinueWhileLoop",
            "display_name": "ContinueWhileLoop",
        },
        "EndWhileLoop": {
            "python_class": EndWhileLoop,
            "javascript_class_name": "EndWhileLoop",
            "display_name": "EndWhileLoop",
        },
        "ValuePath": {
            "python_class": ValuePath,
            "javascript_class_name": "ValuePath",
            "display_name": "ValuePath",
        },
        "MemoryWrite": {
            "python_class": MemoryWrite,
            "javascript_class_name": "MemoryWrite",
            "display_name": "MemoryWrite",
        },
        "MemoryRead": {
            "python_class": MemoryRead,
            "javascript_class_name": "MemoryRead",
            "display_name": "MemoryRead",
        },
        "PassThrough": {
            "python_class": PassThrough,
            "javascript_class_name": "PassThrough",
            "display_name": "PassThrough",
        },
        "JSONParse": {
            "python_class": JSONParse,
            "javascript_class_name": "JSONParse",
            "display_name": "JSONParse",
        },
        "ConcatString": {
            "python_class": ConcatString,
            "javascript_class_name": "ConcatString",
            "display_name": "ConcatString",
        },
        "Subtract": {
            "python_class": Subtract,
            "javascript_class_name": "Subtract",
            "display_name": "Subtract",
        },
        "Add": {
            "python_class": Add,
            "javascript_class_name": "Add",
            "display_name": "Add",
        },
        "Multiply": {
            "python_class": Multiply,
            "javascript_class_name": "Multiply",
            "display_name": "Multiply",
        },
        "Divide": {
            "python_class": Divide,
            "javascript_class_name": "Divide",
            "display_name": "Divide",
        },
        "Exponent": {
            "python_class": Exponent,
            "javascript_class_name": "Exponent",
            "display_name": "Exponent",
        },
        "StringContains": {
            "python_class": StringContains,
            "javascript_class_name": "StringContains",
            "display_name": "StringContains",
        },
        "StringStartsWith": {
            "python_class": StringStartsWith,
            "javascript_class_name": "StringStartsWith",
            "display_name": "StringStartsWith",
        },
        "StringEndsWith": {
            "python_class": StringEndsWith,
            "javascript_class_name": "StringEndsWith",
            "display_name": "StringEndsWith",
        },
        "StringSplit": {
            "python_class": StringSplit,
            "javascript_class_name": "StringSplit",
            "display_name": "StringSplit",
        },
        "StringJoin": {
            "python_class": StringJoin,
            "javascript_class_name": "StringJoin",
            "display_name": "StringJoin",
        },
        "StringReplace": {
            "python_class": StringReplace,
            "javascript_class_name": "StringReplace",
            "display_name": "StringReplace",
        },
        "StringToUpper": {
            "python_class": StringToUpper,
            "javascript_class_name": "StringToUpper",
            "display_name": "StringToUpper",
        },
        "StringToLower": {
            "python_class": StringToLower,
            "javascript_class_name": "StringToLower",
            "display_name": "StringToLower",
        },
        "StringCapitalize": {
            "python_class": StringCapitalize,
            "javascript_class_name": "StringCapitalize",
            "display_name": "StringCapitalize",
        },
        "StringTitleCase": {
            "python_class": StringTitleCase,
            "javascript_class_name": "StringTitleCase",
            "display_name": "StringTitleCase",
        },
        "StringStrip": {
            "python_class": StringStrip,
            "javascript_class_name": "StringStrip",
            "display_name": "StringStrip",
        },
        "StringLStrip": {
            "python_class": StringLStrip,
            "javascript_class_name": "StringLStrip",
            "display_name": "StringLStrip",
        },
        "StringRStrip": {
            "python_class": StringRStrip,
            "javascript_class_name": "StringRStrip",
            "display_name": "StringRStrip",
        },
        "StringFind": {
            "python_class": StringFind,
            "javascript_class_name": "StringFind",
            "display_name": "StringFind",
        },
        "StringRFind": {
            "python_class": StringRFind,
            "javascript_class_name": "StringRFind",
            "display_name": "StringRFind",
        },
        "StringCount": {
            "python_class": StringCount,
            "javascript_class_name": "StringCount",
            "display_name": "StringCount",
        },
        "StringIsDigit": {
            "python_class": StringIsDigit,
            "javascript_class_name": "StringIsDigit",
            "display_name": "StringIsDigit",
        },
        "StringIsAlpha": {
            "python_class": StringIsAlpha,
            "javascript_class_name": "StringIsAlpha",
            "display_name": "StringIsAlpha",
        },
        "StringIsAlnum": {
            "python_class": StringIsAlnum,
            "javascript_class_name": "StringIsAlnum",
            "display_name": "StringIsAlnum",
        },
        "StringIsSpace": {
            "python_class": StringIsSpace,
            "javascript_class_name": "StringIsSpace",
            "display_name": "StringIsSpace",
        },
        "StringIsNumeric": {
            "python_class": StringIsNumeric,
            "javascript_class_name": "StringIsNumeric",
            "display_name": "StringIsNumeric",
        },
        "StringIsDecimal": {
            "python_class": StringIsDecimal,
            "javascript_class_name": "StringIsDecimal",
            "display_name": "StringIsDecimal",
        },
        "StringEncode": {
            "python_class": StringEncode,
            "javascript_class_name": "StringEncode",
            "display_name": "StringEncode",
        },
        "StringDecode": {
            "python_class": StringDecode,
            "javascript_class_name": "StringDecode",
            "display_name": "StringDecode",
        },
        "StringZFill": {
            "python_class": StringZFill,
            "javascript_class_name": "StringZFill",
            "display_name": "StringZFill",
        },
        "StringCenter": {
            "python_class": StringCenter,
            "javascript_class_name": "StringCenter",
            "display_name": "StringCenter",
        },
        "StringLJustify": {
            "python_class": StringLJustify,
            "javascript_class_name": "StringLJustify",
            "display_name": "StringLJustify",
        },
        "StringRJustify": {
            "python_class": StringRJustify,
            "javascript_class_name": "StringRJustify",
            "display_name": "StringRJustify",
        },
        "StringExpandtabs": {
            "python_class": StringExpandtabs,
            "javascript_class_name": "StringExpandtabs",
            "display_name": "StringExpandtabs",
        },
        "StringSwapcase": {
            "python_class": StringSwapcase,
            "javascript_class_name": "StringSwapcase",
            "display_name": "StringSwapcase",
        },
        "StringCasefold": {
            "python_class": StringCasefold,
            "javascript_class_name": "StringCasefold",
            "display_name": "StringCasefold",
        },
        "StringStartswithAny": {
            "python_class": StringStartswithAny,
            "javascript_class_name": "StringStartswithAny",
            "display_name": "StringStartswithAny",
        },
        "StringEndswithAny": {
            "python_class": StringEndswithAny,
            "javascript_class_name": "StringEndswithAny",
            "display_name": "StringEndswithAny",
        },
        "StringReplaceAll": {
            "python_class": StringReplaceAll,
            "javascript_class_name": "StringReplaceAll",
            "display_name": "StringReplaceAll",
        },
        "StringRegexMatch": {
            "python_class": StringRegexMatch,
            "javascript_class_name": "StringRegexMatch",
            "display_name": "StringRegexMatch",
        },
        "StringRegexSearch": {
            "python_class": StringRegexSearch,
            "javascript_class_name": "StringRegexSearch",
            "display_name": "StringRegexSearch",
        },
        "StringRegexSub": {
            "python_class": StringRegexSub,
            "javascript_class_name": "StringRegexSub",
            "display_name": "StringRegexSub",
        },
        "StringRegexFindAll": {
            "python_class": StringRegexFindAll,
            "javascript_class_name": "StringRegexFindAll",
            "display_name": "StringRegexFindAll",
        },
        "StringRegexSplit": {
            "python_class": StringRegexSplit,
            "javascript_class_name": "StringRegexSplit",
            "display_name": "StringRegexSplit",
        },
        "StringRegexCompile": {
            "python_class": StringRegexCompile,
            "javascript_class_name": "StringRegexCompile",
            "display_name": "StringRegexCompile",
        },
        "StringRegexGroup": {
            "python_class": StringRegexGroup,
            "javascript_class_name": "StringRegexGroup",
            "display_name": "StringRegexGroup",
        },
        "StringRegexGroups": {
            "python_class": StringRegexGroups,
            "javascript_class_name": "StringRegexGroups",
            "display_name": "StringRegexGroups",
        },
        "StringRegexNamedGroups": {
            "python_class": StringRegexNamedGroups,
            "javascript_class_name": "StringRegexNamedGroups",
            "display_name": "StringRegexNamedGroups",
        },
        "StringRegexFindIter": {
            "python_class": StringRegexFindIter,
            "javascript_class_name": "StringRegexFindIter",
            "display_name": "StringRegexFindIter",
        },
        "StringRegexFullMatch": {
            "python_class": StringRegexFullMatch,
            "javascript_class_name": "StringRegexFullMatch",
            "display_name": "StringRegexFullMatch",
        },
        "StringRegexEscape": {
            "python_class": StringRegexEscape,
            "javascript_class_name": "StringRegexEscape",
            "display_name": "StringRegexEscape",
        },
        "StringRegexUnescape": {
            "python_class": StringRegexUnescape,
            "javascript_class_name": "StringRegexUnescape",
            "display_name": "StringRegexUnescape",
        },
        "StringRegexSubstitutionNumber": {
            "python_class": StringRegexSubstitutionNumber,
            "javascript_class_name": "StringRegexSubstitutionNumber",
            "display_name": "StringRegexSubstitutionNumber",
        },
        "StringRegexSubWithFunction": {
            "python_class": StringRegexSubWithFunction,
            "javascript_class_name": "StringRegexSubWithFunction",
            "display_name": "StringRegexSubWithFunction",
        },
        "StringRegexSplitWithFunction": {
            "python_class": StringRegexSplitWithFunction,
            "javascript_class_name": "StringRegexSplitWithFunction",
            "display_name": "StringRegexSplitWithFunction",
        },
        "StringRegexSubWithFlags": {
            "python_class": StringRegexSubWithFlags,
            "javascript_class_name": "StringRegexSubWithFlags",
            "display_name": "StringRegexSubWithFlags",
        },
        "StringRegexSplitWithFlags": {
            "python_class": StringRegexSplitWithFlags,
            "javascript_class_name": "StringRegexSplitWithFlags",
            "display_name": "StringRegexSplitWithFlags",
        },
        "StringSlice": {
            "python_class": StringSlice,
            "javascript_class_name": "StringSlice",
            "display_name": "StringSlice",
        },
        "StringPad": {
            "python_class": StringPad,
            "javascript_class_name": "StringPad",
            "display_name": "StringPad",
        },
        "StringRemovePunctuation": {
            "python_class": StringRemovePunctuation,
            "javascript_class_name": "StringRemovePunctuation",
            "display_name": "StringRemovePunctuation",
        },
        "StringRemoveWhitespace": {
            "python_class": StringRemoveWhitespace,
            "javascript_class_name": "StringRemoveWhitespace",
            "display_name": "StringRemoveWhitespace",
        },
        "StringRemoveDigits": {
            "python_class": StringRemoveDigits,
            "javascript_class_name": "StringRemoveDigits",
            "display_name": "StringRemoveDigits",
        },
        "StringRemoveSpecialCharacters": {
            "python_class": StringRemoveSpecialCharacters,
            "javascript_class_name": "StringRemoveSpecialCharacters",
            "display_name": "StringRemoveSpecialCharacters",
        },
        "StringExtractNumbers": {
            "python_class": StringExtractNumbers,
            "javascript_class_name": "StringExtractNumbers",
            "display_name": "StringExtractNumbers",
        },
        "StringExtractWords": {
            "python_class": StringExtractWords,
            "javascript_class_name": "StringExtractWords",
            "display_name": "StringExtractWords",
        },
        "StringExtractSentences": {
            "python_class": StringExtractSentences,
            "javascript_class_name": "StringExtractSentences",
            "display_name": "StringExtractSentences",
        },
        "StringExtractParagraphs": {
            "python_class": StringExtractParagraphs,
            "javascript_class_name": "StringExtractParagraphs",
            "display_name": "StringExtractParagraphs",
        },
        "StringExtractEmails": {
            "python_class": StringExtractEmails,
            "javascript_class_name": "StringExtractEmails",
            "display_name": "StringExtractEmails",
        },
        "StringExtractUrls": {
            "python_class": StringExtractUrls,
            "javascript_class_name": "StringExtractUrls",
            "display_name": "StringExtractUrls",
        },
        "StringExtractHashtags": {
            "python_class": StringExtractHashtags,
            "javascript_class_name": "StringExtractHashtags",
            "display_name": "StringExtractHashtags",
        },
        "StringExtractMentions": {
            "python_class": StringExtractMentions,
            "javascript_class_name": "StringExtractMentions",
            "display_name": "StringExtractMentions",
        },
        "StringExtractDates": {
            "python_class": StringExtractDates,
            "javascript_class_name": "StringExtractDates",
            "display_name": "StringExtractDates",
        },
        "StringExtractTimes": {
            "python_class": StringExtractTimes,
            "javascript_class_name": "StringExtractTimes",
            "display_name": "StringExtractTimes",
        },
        "StringExtractCurrency": {
            "python_class": StringExtractCurrency,
            "javascript_class_name": "StringExtractCurrency",
            "display_name": "StringExtractCurrency",
        },
        "StringExtractPhoneNumbers": {
            "python_class": StringExtractPhoneNumbers,
            "javascript_class_name": "StringExtractPhoneNumbers",
            "display_name": "StringExtractPhoneNumbers",
        },
        "StringExtractIpAddresses": {
            "python_class": StringExtractIpAddresses,
            "javascript_class_name": "StringExtractIpAddresses",
            "display_name": "StringExtractIpAddresses",
        },
        "StringExtractHtmlTags": {
            "python_class": StringExtractHtmlTags,
            "javascript_class_name": "StringExtractHtmlTags",
            "display_name": "StringExtractHtmlTags",
        },
        "StringExtractJsonKeys": {
            "python_class": StringExtractJsonKeys,
            "javascript_class_name": "StringExtractJsonKeys",
            "display_name": "StringExtractJsonKeys",
        },
        "StringExtractXmlTags": {
            "python_class": StringExtractXmlTags,
            "javascript_class_name": "StringExtractXmlTags",
            "display_name": "StringExtractXmlTags",
        },
        "StringExtractCsvColumns": {
            "python_class": StringExtractCsvColumns,
            "javascript_class_name": "StringExtractCsvColumns",
            "display_name": "StringExtractCsvColumns",
        },
        "StringExtractMarkdownHeaders": {
            "python_class": StringExtractMarkdownHeaders,
            "javascript_class_name": "StringExtractMarkdownHeaders",
            "display_name": "StringExtractMarkdownHeaders",
        },
        "StringExtractCodeBlocks": {
            "python_class": StringExtractCodeBlocks,
            "javascript_class_name": "StringExtractCodeBlocks",
            "display_name": "StringExtractCodeBlocks",
        },
        "StringExtractComments": {
            "python_class": StringExtractComments,
            "javascript_class_name": "StringExtractComments",
            "display_name": "StringExtractComments",
        },
        "StringExtractFunctions": {
            "python_class": StringExtractFunctions,
            "javascript_class_name": "StringExtractFunctions",
            "display_name": "StringExtractFunctions",
        },
        "StringExtractClasses": {
            "python_class": StringExtractClasses,
            "javascript_class_name": "StringExtractClasses",
            "display_name": "StringExtractClasses",
        },
        "StringExtractModules": {
            "python_class": StringExtractModules,
            "javascript_class_name": "StringExtractModules",
            "display_name": "StringExtractModules",
        },
        "StringExtractImports": {
            "python_class": StringExtractImports,
            "javascript_class_name": "StringExtractImports",
            "display_name": "StringExtractImports",
        },
        "StringExtractExports": {
            "python_class": StringExtractExports,
            "javascript_class_name": "StringExtractExports",
            "display_name": "StringExtractExports",
        },
        "StringExtractExtensions": {
            "python_class": StringExtractExtensions,
            "javascript_class_name": "StringExtractExtensions",
            "display_name": "StringExtractExtensions",
        },
        "StringRemoveDuplicates": {
            "python_class": StringRemoveDuplicates,
            "javascript_class_name": "StringRemoveDuplicates",
            "display_name": "StringRemoveDuplicates",
        },
        "StringRemoveHtmlEntities": {
            "python_class": StringRemoveHtmlEntities,
            "javascript_class_name": "StringRemoveHtmlEntities",
            "display_name": "StringRemoveHtmlEntities",
        },
        "StringRemoveXmlEntities": {
            "python_class": StringRemoveXmlEntities,
            "javascript_class_name": "StringRemoveXmlEntities",
            "display_name": "StringRemoveXmlEntities",
        },
        "StringRemoveUnicode": {
            "python_class": StringRemoveUnicode,
            "javascript_class_name": "StringRemoveUnicode",
            "display_name": "StringRemoveUnicode",
        },
        "StringNormalizeUnicode": {
            "python_class": StringNormalizeUnicode,
            "javascript_class_name": "StringNormalizeUnicode",
            "display_name": "StringNormalizeUnicode",
        },
        "StringMatchCase": {
            "python_class": StringMatchCase,
            "javascript_class_name": "StringMatchCase",
            "display_name": "StringMatchCase",
        },
        "StringMatchLength": {
            "python_class": StringMatchLength,
            "javascript_class_name": "StringMatchLength",
            "display_name": "StringMatchLength",
        },
        "StringMatchPattern": {
            "python_class": StringMatchPattern,
            "javascript_class_name": "StringMatchPattern",
            "display_name": "StringMatchPattern",
        },
        "StringMatchNone": {
            "python_class": StringMatchNone,
            "javascript_class_name": "StringMatchNone",
            "display_name": "StringMatchNone",
        },
        "StringMatchFuzzy": {
            "python_class": StringMatchFuzzy,
            "javascript_class_name": "StringMatchFuzzy",
            "display_name": "StringMatchFuzzy",
        },
        "StringMatchSimilarity": {
            "python_class": StringMatchSimilarity,
            "javascript_class_name": "StringMatchSimilarity",
            "display_name": "StringMatchSimilarity",
        },
        "StringMatchCosine": {
            "python_class": StringMatchCosine,
            "javascript_class_name": "StringMatchCosine",
            "display_name": "StringMatchCosine",
        },
        "StringMatchLevenshtein": {
            "python_class": StringMatchLevenshtein,
            "javascript_class_name": "StringMatchLevenshtein",
            "display_name": "StringMatchLevenshtein",
        },
        "StringMatchHamming": {
            "python_class": StringMatchHamming,
            "javascript_class_name": "StringMatchHamming",
            "display_name": "StringMatchHamming",
        },
        "StringMatchJaro": {
            "python_class": StringMatchJaro,
            "javascript_class_name": "StringMatchJaro",
            "display_name": "StringMatchJaro",
        },
        "StringMatchJaroWinkler": {
            "python_class": StringMatchJaroWinkler,
            "javascript_class_name": "StringMatchJaroWinkler",
            "display_name": "StringMatchJaroWinkler",
        },
        "StringMatchTfIdf": {
            "python_class": StringMatchTfIdf,
            "javascript_class_name": "StringMatchTfIdf",
            "display_name": "StringMatchTfIdf",
        },
        "StringRemoveAccentedCharacters": {
            "python_class": StringRemoveAccentedCharacters,
            "javascript_class_name": "StringRemoveAccentedCharacters",
            "display_name": "StringRemoveAccentedCharacters",
        },
        "StringRemoveEmojis": {
            "python_class": StringRemoveEmojis,
            "javascript_class_name": "StringRemoveEmojis",
            "display_name": "StringRemoveEmojis",
        },
        "StringRemoveUrls": {
            "python_class": StringRemoveUrls,
            "javascript_class_name": "StringRemoveUrls",
            "display_name": "StringRemoveUrls",
        },
        "StringRemoveEmails": {
            "python_class": StringRemoveEmails,
            "javascript_class_name": "StringRemoveEmails",
            "display_name": "StringRemoveEmails",
        },
        "StringRemoveMentions": {
            "python_class": StringRemoveMentions,
            "javascript_class_name": "StringRemoveMentions",
            "display_name": "StringRemoveMentions",
        },
        "StringRemoveHashtags": {
            "python_class": StringRemoveHashtags,
            "javascript_class_name": "StringRemoveHashtags",
            "display_name": "StringRemoveHashtags",
        },
        "StringRemoveHtmlTags": {
            "python_class": StringRemoveHtmlTags,
            "javascript_class_name": "StringRemoveHtmlTags",
            "display_name": "StringRemoveHtmlTags",
        },
        "StringRemoveNonAscii": {
            "python_class": StringRemoveNonAscii,
            "javascript_class_name": "StringRemoveNonAscii",
            "display_name": "StringRemoveNonAscii",
        },
        "StringRemoveNonPrintable": {
            "python_class": StringRemoveNonPrintable,
            "javascript_class_name": "StringRemoveNonPrintable",
            "display_name": "StringRemoveNonPrintable",
        },
        "StringRemoveNonAlphanumeric": {
            "python_class": StringRemoveNonAlphanumeric,
            "javascript_class_name": "StringRemoveNonAlphanumeric",
            "display_name": "StringRemoveNonAlphanumeric",
        },
        "StringRemoveNonLetters": {
            "python_class": StringRemoveNonLetters,
            "javascript_class_name": "StringRemoveNonLetters",
            "display_name": "StringRemoveNonLetters",
        },
        "StringRemoveNonDigits": {
            "python_class": StringRemoveNonDigits,
            "javascript_class_name": "StringRemoveNonDigits",
            "display_name": "StringRemoveNonDigits",
        },
        "StringRemoveNonWords": {
            "python_class": StringRemoveNonWords,
            "javascript_class_name": "StringRemoveNonWords",
            "display_name": "StringRemoveNonWords",
        },
        "StringRemoveNonSentences": {
            "python_class": StringRemoveNonSentences,
            "javascript_class_name": "StringRemoveNonSentences",
            "display_name": "StringRemoveNonSentences",
        },
        "StringRemoveNonParagraphs": {
            "python_class": StringRemoveNonParagraphs,
            "javascript_class_name": "StringRemoveNonParagraphs",
            "display_name": "StringRemoveNonParagraphs",
        },
        "StringRemoveNonSymbols": {
            "python_class": StringRemoveNonSymbols,
            "javascript_class_name": "StringRemoveNonSymbols",
            "display_name": "StringRemoveNonSymbols",
        },
        "StringRemoveNonOperators": {
            "python_class": StringRemoveNonOperators,
            "javascript_class_name": "StringRemoveNonOperators",
            "display_name": "StringRemoveNonOperators",
        },
        "StringConvertToUtf16": {
            "python_class": StringConvertToUtf16,
            "javascript_class_name": "StringConvertToUtf16",
            "display_name": "StringConvertToUtf16",
        },
        "StringConvertToUtf32": {
            "python_class": StringConvertToUtf32,
            "javascript_class_name": "StringConvertToUtf32",
            "display_name": "StringConvertToUtf32",
        },
        "StringConvertToBase64": {
            "python_class": StringConvertToBase64,
            "javascript_class_name": "StringConvertToBase64",
            "display_name": "StringConvertToBase64",
        },
        "StringDecodeBase64": {
            "python_class": StringDecodeBase64,
            "javascript_class_name": "StringDecodeBase64",
            "display_name": "StringDecodeBase64",
        },
        "StringConvertToHex": {
            "python_class": StringConvertToHex,
            "javascript_class_name": "StringConvertToHex",
            "display_name": "StringConvertToHex",
        },
        "StringDecodeHex": {
            "python_class": StringDecodeHex,
            "javascript_class_name": "StringDecodeHex",
            "display_name": "StringDecodeHex",
        },
        "StringConvertToBinary": {
            "python_class": StringConvertToBinary,
            "javascript_class_name": "StringConvertToBinary",
            "display_name": "StringConvertToBinary",
        },
        "StringDecodeBinary": {
            "python_class": StringDecodeBinary,
            "javascript_class_name": "StringDecodeBinary",
            "display_name": "StringDecodeBinary",
        },
        "StringConvertToOctal": {
            "python_class": StringConvertToOctal,
            "javascript_class_name": "StringConvertToOctal",
            "display_name": "StringConvertToOctal",
        },
        "StringDecodeOctal": {
            "python_class": StringDecodeOctal,
            "javascript_class_name": "StringDecodeOctal",
            "display_name": "StringDecodeOctal",
        },
        "StringConvertToHtmlEntities": {
            "python_class": StringConvertToHtmlEntities,
            "javascript_class_name": "StringConvertToHtmlEntities",
            "display_name": "StringConvertToHtmlEntities",
        },
        "StringDecodeHtmlEntities": {
            "python_class": StringDecodeHtmlEntities,
            "javascript_class_name": "StringDecodeHtmlEntities",
            "display_name": "StringDecodeHtmlEntities",
        },
        "StringConvertToUrlEncoding": {
            "python_class": StringConvertToUrlEncoding,
            "javascript_class_name": "StringConvertToUrlEncoding",
            "display_name": "StringConvertToUrlEncoding",
        },
        "StringDecodeUrlEncoding": {
            "python_class": StringDecodeUrlEncoding,
            "javascript_class_name": "StringDecodeUrlEncoding",
            "display_name": "StringDecodeUrlEncoding",
        },
        "StringParseJson": {
            "python_class": StringParseJson,
            "javascript_class_name": "StringParseJson",
            "display_name": "StringParseJson",
        },
        "StringParseXml": {
            "python_class": StringParseXml,
            "javascript_class_name": "StringParseXml",
            "display_name": "StringParseXml",
        },
        "StringConvertToCsv": {
            "python_class": StringConvertToCsv,
            "javascript_class_name": "StringConvertToCsv",
            "display_name": "StringConvertToCsv",
        },
        "StringParseCsv": {
            "python_class": StringParseCsv,
            "javascript_class_name": "StringParseCsv",
            "display_name": "StringParseCsv",
        },
        "StringParseYaml": {
            "python_class": StringParseYaml,
            "javascript_class_name": "StringParseYaml",
            "display_name": "StringParseYaml",
        },
        "StringParseIni": {
            "python_class": StringParseIni,
            "javascript_class_name": "StringParseIni",
            "display_name": "StringParseIni",
        },
        "StringParseRtf": {
            "python_class": StringParseRtf,
            "javascript_class_name": "StringParseRtf",
            "display_name": "StringParseRtf",
        },
        "StringConvertToMd5": {
            "python_class": StringConvertToMd5,
            "javascript_class_name": "StringConvertToMd5",
            "display_name": "StringConvertToMd5",
        },
        "StringConvertToSha1": {
            "python_class": StringConvertToSha1,
            "javascript_class_name": "StringConvertToSha1",
            "display_name": "StringConvertToSha1",
        },
        "StringConvertToSha256": {
            "python_class": StringConvertToSha256,
            "javascript_class_name": "StringConvertToSha256",
            "display_name": "StringConvertToSha256",
        },
        "StringConvertToSha512": {
            "python_class": StringConvertToSha512,
            "javascript_class_name": "StringConvertToSha512",
            "display_name": "StringConvertToSha512",
        },
        "StringHashString": {
            "python_class": StringHashString,
            "javascript_class_name": "StringHashString",
            "display_name": "StringHashString",
        },
        "StringVerifyHash": {
            "python_class": StringVerifyHash,
            "javascript_class_name": "StringVerifyHash",
            "display_name": "StringVerifyHash",
        },
        "StringGenerateUuid": {
            "python_class": StringGenerateUuid,
            "javascript_class_name": "StringGenerateUuid",
            "display_name": "StringGenerateUuid",
        },
        "StringRemoveHtmlComments": {
            "python_class": StringRemoveHtmlComments,
            "javascript_class_name": "StringRemoveHtmlComments",
            "display_name": "StringRemoveHtmlComments",
        },
        "StringRemoveXmlComments": {
            "python_class": StringRemoveXmlComments,
            "javascript_class_name": "StringRemoveXmlComments",
            "display_name": "StringRemoveXmlComments",
        },
        "StringRemoveJsonComments": {
            "python_class": StringRemoveJsonComments,
            "javascript_class_name": "StringRemoveJsonComments",
            "display_name": "StringRemoveJsonComments",
        },
        "StringRemoveCssComments": {
            "python_class": StringRemoveCssComments,
            "javascript_class_name": "StringRemoveCssComments",
            "display_name": "StringRemoveCssComments",
        },
        "StringRemoveJsComments": {
            "python_class": StringRemoveJsComments,
            "javascript_class_name": "StringRemoveJsComments",
            "display_name": "StringRemoveJsComments",
        },
        "StringRemoveMultilineComments": {
            "python_class": StringRemoveMultilineComments,
            "javascript_class_name": "StringRemoveMultilineComments",
            "display_name": "StringRemoveMultilineComments",
        },
        "StringRemoveSinglelineComments": {
            "python_class": StringRemoveSinglelineComments,
            "javascript_class_name": "StringRemoveSinglelineComments",
            "display_name": "StringRemoveSinglelineComments",
        },
        "StringExtractHtmlAttributes": {
            "python_class": StringExtractHtmlAttributes,
            "javascript_class_name": "StringExtractHtmlAttributes",
            "display_name": "StringExtractHtmlAttributes",
        },
        "StringExtractXmlAttributes": {
            "python_class": StringExtractXmlAttributes,
            "javascript_class_name": "StringExtractXmlAttributes",
            "display_name": "StringExtractXmlAttributes",
        },
        "StringExtractCssSelectors": {
            "python_class": StringExtractCssSelectors,
            "javascript_class_name": "StringExtractCssSelectors",
            "display_name": "StringExtractCssSelectors",
        },
        "StringExtractHtmlDataAttributes": {
            "python_class": StringExtractHtmlDataAttributes,
            "javascript_class_name": "StringExtractHtmlDataAttributes",
            "display_name": "StringExtractHtmlDataAttributes",
        },
        "StringExtractXmlNamespaces": {
            "python_class": StringExtractXmlNamespaces,
            "javascript_class_name": "StringExtractXmlNamespaces",
            "display_name": "StringExtractXmlNamespaces",
        },
        "StringExtractCsvRows": {
            "python_class": StringExtractCsvRows,
            "javascript_class_name": "StringExtractCsvRows",
            "display_name": "StringExtractCsvRows",
        },
        "StringExtractCsvHeaders": {
            "python_class": StringExtractCsvHeaders,
            "javascript_class_name": "StringExtractCsvHeaders",
            "display_name": "StringExtractCsvHeaders",
        },
        "StringExtractCsvCells": {
            "python_class": StringExtractCsvCells,
            "javascript_class_name": "StringExtractCsvCells",
            "display_name": "StringExtractCsvCells",
        },
        "StringExtractYamlDocuments": {
            "python_class": StringExtractYamlDocuments,
            "javascript_class_name": "StringExtractYamlDocuments",
            "display_name": "StringExtractYamlDocuments",
        },
        "StringExtractYamlKeys": {
            "python_class": StringExtractYamlKeys,
            "javascript_class_name": "StringExtractYamlKeys",
            "display_name": "StringExtractYamlKeys",
        },
        "StringExtractYamlValues": {
            "python_class": StringExtractYamlValues,
            "javascript_class_name": "StringExtractYamlValues",
            "display_name": "StringExtractYamlValues",
        },
        "StringExtractMarkdownLinks": {
            "python_class": StringExtractMarkdownLinks,
            "javascript_class_name": "StringExtractMarkdownLinks",
            "display_name": "StringExtractMarkdownLinks",
        },
        "StringExtractMarkdownImages": {
            "python_class": StringExtractMarkdownImages,
            "javascript_class_name": "StringExtractMarkdownImages",
            "display_name": "StringExtractMarkdownImages",
        },
        "StringExtractMarkdownCodeBlocks": {
            "python_class": StringExtractMarkdownCodeBlocks,
            "javascript_class_name": "StringExtractMarkdownCodeBlocks",
            "display_name": "StringExtractMarkdownCodeBlocks",
        },
        "StringExtractMarkdownLists": {
            "python_class": StringExtractMarkdownLists,
            "javascript_class_name": "StringExtractMarkdownLists",
            "display_name": "StringExtractMarkdownLists",
        },
        "StringExtractMarkdownTables": {
            "python_class": StringExtractMarkdownTables,
            "javascript_class_name": "StringExtractMarkdownTables",
            "display_name": "StringExtractMarkdownTables",
        },
        "StringDependencyParsing": {
            "python_class": StringDependencyParsing,
            "javascript_class_name": "StringDependencyParsing",
            "display_name": "StringDependencyParsing",
        },
        "Modulus": {
            "python_class": Modulus,
            "javascript_class_name": "Modulus",
            "display_name": "Modulus",
        },
        "FloorDivision": {
            "python_class": FloorDivision,
            "javascript_class_name": "FloorDivision",
            "display_name": "FloorDivision",
        },
        "SquareRoot": {
            "python_class": SquareRoot,
            "javascript_class_name": "SquareRoot",
            "display_name": "SquareRoot",
        },
        "AbsoluteValue": {
            "python_class": AbsoluteValue,
            "javascript_class_name": "AbsoluteValue",
            "display_name": "AbsoluteValue",
        },
        "Logarithm": {
            "python_class": Logarithm,
            "javascript_class_name": "Logarithm",
            "display_name": "Logarithm",
        },
        "Power": {
            "python_class": Power,
            "javascript_class_name": "Power",
            "display_name": "Power",
        },
        "Round": {
            "python_class": Round,
            "javascript_class_name": "Round",
            "display_name": "Round",
        },
        "Ceil": {
            "python_class": Ceil,
            "javascript_class_name": "Ceil",
            "display_name": "Ceil",
        },
        "Floor": {
            "python_class": Floor,
            "javascript_class_name": "Floor",
            "display_name": "Floor",
        },
        "Truncate": {
            "python_class": Truncate,
            "javascript_class_name": "Truncate",
            "display_name": "Truncate",
        },
        "Mean": {
            "python_class": Mean,
            "javascript_class_name": "Mean",
            "display_name": "Mean",
        },
        "Median": {
            "python_class": Median,
            "javascript_class_name": "Median",
            "display_name": "Median",
        },
        "Mode": {
            "python_class": Mode,
            "javascript_class_name": "Mode",
            "display_name": "Mode",
        },
        "Variance": {
            "python_class": Variance,
            "javascript_class_name": "Variance",
            "display_name": "Variance",
        },
        "StandardDeviation": {
            "python_class": StandardDeviation,
            "javascript_class_name": "StandardDeviation",
            "display_name": "StandardDeviation",
        },
        "GCD": {
            "python_class": GCD,
            "javascript_class_name": "GCD",
            "display_name": "GCD",
        },
        "LCM": {
            "python_class": LCM,
            "javascript_class_name": "LCM",
            "display_name": "LCM",
        },
        "Factorial": {
            "python_class": Factorial,
            "javascript_class_name": "Factorial",
            "display_name": "Factorial",
        },
        "Sign": {
            "python_class": Sign,
            "javascript_class_name": "Sign",
            "display_name": "Sign",
        },
        "Clamp": {
            "python_class": Clamp,
            "javascript_class_name": "Clamp",
            "display_name": "Clamp",
        },
        "HarmonicMean": {
            "python_class": HarmonicMean,
            "javascript_class_name": "HarmonicMean",
            "display_name": "HarmonicMean",
        },
        "GeometricMean": {
            "python_class": GeometricMean,
            "javascript_class_name": "GeometricMean",
            "display_name": "GeometricMean",
        },
        "CubicRoot": {
            "python_class": CubicRoot,
            "javascript_class_name": "CubicRoot",
            "display_name": "CubicRoot",
        },
        "LogBase10": {
            "python_class": LogBase10,
            "javascript_class_name": "LogBase10",
            "display_name": "LogBase10",
        },
        "LogBase2": {
            "python_class": LogBase2,
            "javascript_class_name": "LogBase2",
            "display_name": "LogBase2",
        },
        "HyperbolicSine": {
            "python_class": HyperbolicSine,
            "javascript_class_name": "HyperbolicSine",
            "display_name": "HyperbolicSine",
        },
        "HyperbolicCosine": {
            "python_class": HyperbolicCosine,
            "javascript_class_name": "HyperbolicCosine",
            "display_name": "HyperbolicCosine",
        },
        "HyperbolicTangent": {
            "python_class": HyperbolicTangent,
            "javascript_class_name": "HyperbolicTangent",
            "display_name": "HyperbolicTangent",
        },
        "InverseSine": {
            "python_class": InverseSine,
            "javascript_class_name": "InverseSine",
            "display_name": "InverseSine",
        },
        "InverseCosine": {
            "python_class": InverseCosine,
            "javascript_class_name": "InverseCosine",
            "display_name": "InverseCosine",
        },
        "InverseTangent": {
            "python_class": InverseTangent,
            "javascript_class_name": "InverseTangent",
            "display_name": "InverseTangent",
        },
        "InverseHyperbolicSine": {
            "python_class": InverseHyperbolicSine,
            "javascript_class_name": "InverseHyperbolicSine",
            "display_name": "InverseHyperbolicSine",
        },
        "InverseHyperbolicCosine": {
            "python_class": InverseHyperbolicCosine,
            "javascript_class_name": "InverseHyperbolicCosine",
            "display_name": "InverseHyperbolicCosine",
        },
        "InverseHyperbolicTangent": {
            "python_class": InverseHyperbolicTangent,
            "javascript_class_name": "InverseHyperbolicTangent",
            "display_name": "InverseHyperbolicTangent",
        },
        "Exponential": {
            "python_class": Exponential,
            "javascript_class_name": "Exponential",
            "display_name": "Exponential",
        },
        "NaturalLogarithm": {
            "python_class": NaturalLogarithm,
            "javascript_class_name": "NaturalLogarithm",
            "display_name": "NaturalLogarithm",
        },
        "Base10Logarithm": {
            "python_class": Base10Logarithm,
            "javascript_class_name": "Base10Logarithm",
            "display_name": "Base10Logarithm",
        },
        "Base2Logarithm": {
            "python_class": Base2Logarithm,
            "javascript_class_name": "Base2Logarithm",
            "display_name": "Base2Logarithm",
        },
        "LogarithmBaseE": {
            "python_class": LogarithmBaseE,
            "javascript_class_name": "LogarithmBaseE",
            "display_name": "LogarithmBaseE",
        },
        "LogarithmBase10": {
            "python_class": LogarithmBase10,
            "javascript_class_name": "LogarithmBase10",
            "display_name": "LogarithmBase10",
        },
        "LogarithmBase2": {
            "python_class": LogarithmBase2,
            "javascript_class_name": "LogarithmBase2",
            "display_name": "LogarithmBase2",
        },
        "LogarithmBaseN": {
            "python_class": LogarithmBaseN,
            "javascript_class_name": "LogarithmBaseN",
            "display_name": "LogarithmBaseN",
        },
        "RationalApproximation": {
            "python_class": RationalApproximation,
            "javascript_class_name": "RationalApproximation",
            "display_name": "RationalApproximation",
        },
        "ComplexConjugate": {
            "python_class": ComplexConjugate,
            "javascript_class_name": "ComplexConjugate",
            "display_name": "ComplexConjugate",
        },
        "PolarToCartesian": {
            "python_class": PolarToCartesian,
            "javascript_class_name": "PolarToCartesian",
            "display_name": "PolarToCartesian",
        },
        "CartesianToPolar": {
            "python_class": CartesianToPolar,
            "javascript_class_name": "CartesianToPolar",
            "display_name": "CartesianToPolar",
        },
        "MatrixDeterminant": {
            "python_class": MatrixDeterminant,
            "javascript_class_name": "MatrixDeterminant",
            "display_name": "MatrixDeterminant",
        },
        "MatrixInverse": {
            "python_class": MatrixInverse,
            "javascript_class_name": "MatrixInverse",
            "display_name": "MatrixInverse",
        },
        "MatrixTranspose": {
            "python_class": MatrixTranspose,
            "javascript_class_name": "MatrixTranspose",
            "display_name": "MatrixTranspose",
        },
        "Eigenvalues": {
            "python_class": Eigenvalues,
            "javascript_class_name": "Eigenvalues",
            "display_name": "Eigenvalues",
        },
        "Eigenvectors": {
            "python_class": Eigenvectors,
            "javascript_class_name": "Eigenvectors",
            "display_name": "Eigenvectors",
        },
        "FourierTransform": {
            "python_class": FourierTransform,
            "javascript_class_name": "FourierTransform",
            "display_name": "FourierTransform",
        },
        "InverseFourierTransform": {
            "python_class": InverseFourierTransform,
            "javascript_class_name": "InverseFourierTransform",
            "display_name": "InverseFourierTransform",
        },
        "Cosh": {
            "python_class": Cosh,
            "javascript_class_name": "Cosh",
            "display_name": "Cosh",
        },
        "Sinh": {
            "python_class": Sinh,
            "javascript_class_name": "Sinh",
            "display_name": "Sinh",
        },
        "Tanh": {
            "python_class": Tanh,
            "javascript_class_name": "Tanh",
            "display_name": "Tanh",
        },
        "Arccosh": {
            "python_class": Arccosh,
            "javascript_class_name": "Arccosh",
            "display_name": "Arccosh",
        },
        "Arcsinh": {
            "python_class": Arcsinh,
            "javascript_class_name": "Arcsinh",
            "display_name": "Arcsinh",
        },
        "Arctanh": {
            "python_class": Arctanh,
            "javascript_class_name": "Arctanh",
            "display_name": "Arctanh",
        },
        "Log1p": {
            "python_class": Log1p,
            "javascript_class_name": "Log1p",
            "display_name": "Log1p",
        },
        "Expm1": {
            "python_class": Expm1,
            "javascript_class_name": "Expm1",
            "display_name": "Expm1",
        },
        "Hypot": {
            "python_class": Hypot,
            "javascript_class_name": "Hypot",
            "display_name": "Hypot",
        },
        "DegreesToRadians": {
            "python_class": DegreesToRadians,
            "javascript_class_name": "DegreesToRadians",
            "display_name": "DegreesToRadians",
        },
        "RadiansToDegrees": {
            "python_class": RadiansToDegrees,
            "javascript_class_name": "RadiansToDegrees",
            "display_name": "RadiansToDegrees",
        },
        "LogSumExp": {
            "python_class": LogSumExp,
            "javascript_class_name": "LogSumExp",
            "display_name": "LogSumExp",
        },
        "RootMeanSquare": {
            "python_class": RootMeanSquare,
            "javascript_class_name": "RootMeanSquare",
            "display_name": "RootMeanSquare",
        },
        "HarmonicSum": {
            "python_class": HarmonicSum,
            "javascript_class_name": "HarmonicSum",
            "display_name": "HarmonicSum",
        },
        "GeometricSum": {
            "python_class": GeometricSum,
            "javascript_class_name": "GeometricSum",
            "display_name": "GeometricSum",
        },
        "ArithmeticMean": {
            "python_class": ArithmeticMean,
            "javascript_class_name": "ArithmeticMean",
            "display_name": "ArithmeticMean",
        },
        "QuadraticMean": {
            "python_class": QuadraticMean,
            "javascript_class_name": "QuadraticMean",
            "display_name": "QuadraticMean",
        },
        "WeightedAverage": {
            "python_class": WeightedAverage,
            "javascript_class_name": "WeightedAverage",
            "display_name": "WeightedAverage",
        },
        "CumulativeSum": {
            "python_class": CumulativeSum,
            "javascript_class_name": "CumulativeSum",
            "display_name": "CumulativeSum",
        },
        "CumulativeProduct": {
            "python_class": CumulativeProduct,
            "javascript_class_name": "CumulativeProduct",
            "display_name": "CumulativeProduct",
        },
        "Percentile": {
            "python_class": Percentile,
            "javascript_class_name": "Percentile",
            "display_name": "Percentile",
        },
        "InterquartileRange": {
            "python_class": InterquartileRange,
            "javascript_class_name": "InterquartileRange",
            "display_name": "InterquartileRange",
        },
        "ZScore": {
            "python_class": ZScore,
            "javascript_class_name": "ZScore",
            "display_name": "ZScore",
        },
        "Covariance": {
            "python_class": Covariance,
            "javascript_class_name": "Covariance",
            "display_name": "Covariance",
        },
        "CorrelationCoefficient": {
            "python_class": CorrelationCoefficient,
            "javascript_class_name": "CorrelationCoefficient",
            "display_name": "CorrelationCoefficient",
        },
        "Skewness": {
            "python_class": Skewness,
            "javascript_class_name": "Skewness",
            "display_name": "Skewness",
        },
        "Kurtosis": {
            "python_class": Kurtosis,
            "javascript_class_name": "Kurtosis",
            "display_name": "Kurtosis",
        },
        "Entropy": {
            "python_class": Entropy,
            "javascript_class_name": "Entropy",
            "display_name": "Entropy",
        },
        "Fibonacci": {
            "python_class": Fibonacci,
            "javascript_class_name": "Fibonacci",
            "display_name": "Fibonacci",
        },
        "PrimeCheck": {
            "python_class": PrimeCheck,
            "javascript_class_name": "PrimeCheck",
            "display_name": "PrimeCheck",
        },
        "GreatestCommonDivisor": {
            "python_class": GreatestCommonDivisor,
            "javascript_class_name": "GreatestCommonDivisor",
            "display_name": "GreatestCommonDivisor",
        },
        "LeastCommonMultiple": {
            "python_class": LeastCommonMultiple,
            "javascript_class_name": "LeastCommonMultiple",
            "display_name": "LeastCommonMultiple",
        },
        "BinomialCoefficient": {
            "python_class": BinomialCoefficient,
            "javascript_class_name": "BinomialCoefficient",
            "display_name": "BinomialCoefficient",
        },
        "DecimalToBinary": {
            "python_class": DecimalToBinary,
            "javascript_class_name": "DecimalToBinary",
            "display_name": "DecimalToBinary",
        },
        "BinaryToDecimal": {
            "python_class": BinaryToDecimal,
            "javascript_class_name": "BinaryToDecimal",
            "display_name": "BinaryToDecimal",
        },
        "HexToDecimal": {
            "python_class": HexToDecimal,
            "javascript_class_name": "HexToDecimal",
            "display_name": "HexToDecimal",
        },
        "DecimalToHex": {
            "python_class": DecimalToHex,
            "javascript_class_name": "DecimalToHex",
            "display_name": "DecimalToHex",
        },
        "PolarToRectangular": {
            "python_class": PolarToRectangular,
            "javascript_class_name": "PolarToRectangular",
            "display_name": "PolarToRectangular",
        },
        "RectangularToPolar": {
            "python_class": RectangularToPolar,
            "javascript_class_name": "RectangularToPolar",
            "display_name": "RectangularToPolar",
        },
        "MatrixAddition": {
            "python_class": MatrixAddition,
            "javascript_class_name": "MatrixAddition",
            "display_name": "MatrixAddition",
        },
        "MatrixSubtraction": {
            "python_class": MatrixSubtraction,
            "javascript_class_name": "MatrixSubtraction",
            "display_name": "MatrixSubtraction",
        },
        "MatrixMultiplication": {
            "python_class": MatrixMultiplication,
            "javascript_class_name": "MatrixMultiplication",
            "display_name": "MatrixMultiplication",
        },
        "MatrixRank": {
            "python_class": MatrixRank,
            "javascript_class_name": "MatrixRank",
            "display_name": "MatrixRank",
        },
        "CholeskyDecomposition": {
            "python_class": CholeskyDecomposition,
            "javascript_class_name": "CholeskyDecomposition",
            "display_name": "CholeskyDecomposition",
        },
        "LUDecomposition": {
            "python_class": LUDecomposition,
            "javascript_class_name": "LUDecomposition",
            "display_name": "LUDecomposition",
        },
        "QRDecomposition": {
            "python_class": QRDecomposition,
            "javascript_class_name": "QRDecomposition",
            "display_name": "QRDecomposition",
        },
        "SingularValueDecomposition": {
            "python_class": SingularValueDecomposition,
            "javascript_class_name": "SingularValueDecomposition",
            "display_name": "SingularValueDecomposition",
        },
        "ComplexMagnitude": {
            "python_class": ComplexMagnitude,
            "javascript_class_name": "ComplexMagnitude",
            "display_name": "ComplexMagnitude",
        },
        "ComplexPhase": {
            "python_class": ComplexPhase,
            "javascript_class_name": "ComplexPhase",
            "display_name": "ComplexPhase",
        },
        "LogarithmicMean": {
            "python_class": LogarithmicMean,
            "javascript_class_name": "LogarithmicMean",
            "display_name": "LogarithmicMean",
        },
        "ArithmeticGeometricMean": {
            "python_class": ArithmeticGeometricMean,
            "javascript_class_name": "ArithmeticGeometricMean",
            "display_name": "ArithmeticGeometricMean",
        },
        "HaversineDistance": {
            "python_class": HaversineDistance,
            "javascript_class_name": "HaversineDistance",
            "display_name": "HaversineDistance",
        },
        "DecimalToOctal": {
            "python_class": DecimalToOctal,
            "javascript_class_name": "DecimalToOctal",
            "display_name": "DecimalToOctal",
        },
        "OctalToDecimal": {
            "python_class": OctalToDecimal,
            "javascript_class_name": "OctalToDecimal",
            "display_name": "OctalToDecimal",
        },
        "ModularExponentiation": {
            "python_class": ModularExponentiation,
            "javascript_class_name": "ModularExponentiation",
            "display_name": "ModularExponentiation",
        },
        "FibonacciSequence": {
            "python_class": FibonacciSequence,
            "javascript_class_name": "FibonacciSequence",
            "display_name": "FibonacciSequence",
        },
        "PrimeFactorization": {
            "python_class": PrimeFactorization,
            "javascript_class_name": "PrimeFactorization",
            "display_name": "PrimeFactorization",
        },
        "CumulativeMax": {
            "python_class": CumulativeMax,
            "javascript_class_name": "CumulativeMax",
            "display_name": "CumulativeMax",
        },
        "CumulativeMin": {
            "python_class": CumulativeMin,
            "javascript_class_name": "CumulativeMin",
            "display_name": "CumulativeMin",
        },
        "DecimalToRoman": {
            "python_class": DecimalToRoman,
            "javascript_class_name": "DecimalToRoman",
            "display_name": "DecimalToRoman",
        },
        "RomanToDecimal": {
            "python_class": RomanToDecimal,
            "javascript_class_name": "RomanToDecimal",
            "display_name": "RomanToDecimal",
        },
        "GreatestPrimeFactor": {
            "python_class": GreatestPrimeFactor,
            "javascript_class_name": "GreatestPrimeFactor",
            "display_name": "GreatestPrimeFactor",
        },
        "LeastPrimeFactor": {
            "python_class": LeastPrimeFactor,
            "javascript_class_name": "LeastPrimeFactor",
            "display_name": "LeastPrimeFactor",
        },
        "SumOfDivisors": {
            "python_class": SumOfDivisors,
            "javascript_class_name": "SumOfDivisors",
            "display_name": "SumOfDivisors",
        },
        "PerfectSquareCheck": {
            "python_class": PerfectSquareCheck,
            "javascript_class_name": "PerfectSquareCheck",
            "display_name": "PerfectSquareCheck",
        },
        "PerfectCubeCheck": {
            "python_class": PerfectCubeCheck,
            "javascript_class_name": "PerfectCubeCheck",
            "display_name": "PerfectCubeCheck",
        },
        "IsEven": {
            "python_class": IsEven,
            "javascript_class_name": "IsEven",
            "display_name": "IsEven",
        },
        "IsOdd": {
            "python_class": IsOdd,
            "javascript_class_name": "IsOdd",
            "display_name": "IsOdd",
        },
        "IsPrime": {
            "python_class": IsPrime,
            "javascript_class_name": "IsPrime",
            "display_name": "IsPrime",
        },
        "NextPrime": {
            "python_class": NextPrime,
            "javascript_class_name": "NextPrime",
            "display_name": "NextPrime",
        },
        "PreviousPrime": {
            "python_class": PreviousPrime,
            "javascript_class_name": "PreviousPrime",
            "display_name": "PreviousPrime",
        },
        "LCMArray": {
            "python_class": LCMArray,
            "javascript_class_name": "LCMArray",
            "display_name": "LCMArray",
        },
        "GCDArray": {
            "python_class": GCDArray,
            "javascript_class_name": "GCDArray",
            "display_name": "GCDArray",
        },
        "FactorialArray": {
            "python_class": FactorialArray,
            "javascript_class_name": "FactorialArray",
            "display_name": "FactorialArray",
        },
        "PrimeFactorsList": {
            "python_class": PrimeFactorsList,
            "javascript_class_name": "PrimeFactorsList",
            "display_name": "PrimeFactorsList",
        },
        "IsPerfectNumber": {
            "python_class": IsPerfectNumber,
            "javascript_class_name": "IsPerfectNumber",
            "display_name": "IsPerfectNumber",
        },
        "IsArmstrongNumber": {
            "python_class": IsArmstrongNumber,
            "javascript_class_name": "IsArmstrongNumber",
            "display_name": "IsArmstrongNumber",
        },
        "GreatestCommonDivisorArray": {
            "python_class": GreatestCommonDivisorArray,
            "javascript_class_name": "GreatestCommonDivisorArray",
            "display_name": "GreatestCommonDivisorArray",
        },
        "LeastCommonMultipleArray": {
            "python_class": LeastCommonMultipleArray,
            "javascript_class_name": "LeastCommonMultipleArray",
            "display_name": "LeastCommonMultipleArray",
        },
        "SumOfSquares": {
            "python_class": SumOfSquares,
            "javascript_class_name": "SumOfSquares",
            "display_name": "SumOfSquares",
        },
        "ProductOfArray": {
            "python_class": ProductOfArray,
            "javascript_class_name": "ProductOfArray",
            "display_name": "ProductOfArray",
        },
        "ArithmeticProgressionSum": {
            "python_class": ArithmeticProgressionSum,
            "javascript_class_name": "ArithmeticProgressionSum",
            "display_name": "ArithmeticProgressionSum",
        },
        "GeometricProgressionSum": {
            "python_class": GeometricProgressionSum,
            "javascript_class_name": "GeometricProgressionSum",
            "display_name": "GeometricProgressionSum",
        },
        "HarmonicProgressionSum": {
            "python_class": HarmonicProgressionSum,
            "javascript_class_name": "HarmonicProgressionSum",
            "display_name": "HarmonicProgressionSum",
        },
        "CatalanNumber": {
            "python_class": CatalanNumber,
            "javascript_class_name": "CatalanNumber",
            "display_name": "CatalanNumber",
        },
        "BellNumber": {
            "python_class": BellNumber,
            "javascript_class_name": "BellNumber",
            "display_name": "BellNumber",
        },
        "StirlingNumber": {
            "python_class": StirlingNumber,
            "javascript_class_name": "StirlingNumber",
            "display_name": "StirlingNumber",
        },
        "FibonacciNumber": {
            "python_class": FibonacciNumber,
            "javascript_class_name": "FibonacciNumber",
            "display_name": "FibonacciNumber",
        },
        "LucasNumber": {
            "python_class": LucasNumber,
            "javascript_class_name": "LucasNumber",
            "display_name": "LucasNumber",
        },
        "TriangularNumber": {
            "python_class": TriangularNumber,
            "javascript_class_name": "TriangularNumber",
            "display_name": "TriangularNumber",
        },
        "PentagonalNumber": {
            "python_class": PentagonalNumber,
            "javascript_class_name": "PentagonalNumber",
            "display_name": "PentagonalNumber",
        },
        "HexagonalNumber": {
            "python_class": HexagonalNumber,
            "javascript_class_name": "HexagonalNumber",
            "display_name": "HexagonalNumber",
        },
        "PerfectNumberCheck": {
            "python_class": PerfectNumberCheck,
            "javascript_class_name": "PerfectNumberCheck",
            "display_name": "PerfectNumberCheck",
        },
        "AmicableNumbersCheck": {
            "python_class": AmicableNumbersCheck,
            "javascript_class_name": "AmicableNumbersCheck",
            "display_name": "AmicableNumbersCheck",
        },
        "MersennePrimeCheck": {
            "python_class": MersennePrimeCheck,
            "javascript_class_name": "MersennePrimeCheck",
            "display_name": "MersennePrimeCheck",
        },
        "EulerTotientFunction": {
            "python_class": EulerTotientFunction,
            "javascript_class_name": "EulerTotientFunction",
            "display_name": "EulerTotientFunction",
        },
        "MobiusFunction": {
            "python_class": MobiusFunction,
            "javascript_class_name": "MobiusFunction",
            "display_name": "MobiusFunction",
        },
        "AckermannFunction": {
            "python_class": AckermannFunction,
            "javascript_class_name": "AckermannFunction",
            "display_name": "AckermannFunction",
        },
        "CollatzSequence": {
            "python_class": CollatzSequence,
            "javascript_class_name": "CollatzSequence",
            "display_name": "CollatzSequence",
        },
        "PascalTriangleRow": {
            "python_class": PascalTriangleRow,
            "javascript_class_name": "PascalTriangleRow",
            "display_name": "PascalTriangleRow",
        },
        "FermatNumber": {
            "python_class": FermatNumber,
            "javascript_class_name": "FermatNumber",
            "display_name": "FermatNumber",
        },
        "CarmichaelFunction": {
            "python_class": CarmichaelFunction,
            "javascript_class_name": "CarmichaelFunction",
            "display_name": "CarmichaelFunction",
        },
        "SophieGermainPrimeCheck": {
            "python_class": SophieGermainPrimeCheck,
            "javascript_class_name": "SophieGermainPrimeCheck",
            "display_name": "SophieGermainPrimeCheck",
        },
        "KaprekarNumberCheck": {
            "python_class": KaprekarNumberCheck,
            "javascript_class_name": "KaprekarNumberCheck",
            "display_name": "KaprekarNumberCheck",
        },
        "AutomorphicNumberCheck": {
            "python_class": AutomorphicNumberCheck,
            "javascript_class_name": "AutomorphicNumberCheck",
            "display_name": "AutomorphicNumberCheck",
        },
        "HarshadNumberCheck": {
            "python_class": HarshadNumberCheck,
            "javascript_class_name": "HarshadNumberCheck",
            "display_name": "HarshadNumberCheck",
        },
        "HappyNumberCheck": {
            "python_class": HappyNumberCheck,
            "javascript_class_name": "HappyNumberCheck",
            "display_name": "HappyNumberCheck",
        },
        "EulerNumber": {
            "python_class": EulerNumber,
            "javascript_class_name": "EulerNumber",
            "display_name": "EulerNumber",
        },
        "GoldenRatio": {
            "python_class": GoldenRatio,
            "javascript_class_name": "GoldenRatio",
            "display_name": "GoldenRatio",
        },
        "CatalanConstant": {
            "python_class": CatalanConstant,
            "javascript_class_name": "CatalanConstant",
            "display_name": "CatalanConstant",
        },
        "BernoulliNumber": {
            "python_class": BernoulliNumber,
            "javascript_class_name": "BernoulliNumber",
            "display_name": "BernoulliNumber",
        },
        "EulerNumberSequence": {
            "python_class": EulerNumberSequence,
            "javascript_class_name": "EulerNumberSequence",
            "display_name": "EulerNumberSequence",
        },
        "PartitionFunction": {
            "python_class": PartitionFunction,
            "javascript_class_name": "PartitionFunction",
            "display_name": "PartitionFunction",
        },
        "RamanujanTauFunction": {
            "python_class": RamanujanTauFunction,
            "javascript_class_name": "RamanujanTauFunction",
            "display_name": "RamanujanTauFunction",
        },
        "DedekindEtaFunction": {
            "python_class": DedekindEtaFunction,
            "javascript_class_name": "DedekindEtaFunction",
            "display_name": "DedekindEtaFunction",
        },
        "LiouvilleFunction": {
            "python_class": LiouvilleFunction,
            "javascript_class_name": "LiouvilleFunction",
            "display_name": "LiouvilleFunction",
        },
        "RiemannZetaFunction": {
            "python_class": RiemannZetaFunction,
            "javascript_class_name": "RiemannZetaFunction",
            "display_name": "RiemannZetaFunction",
        },
        "BinetFormula": {
            "python_class": BinetFormula,
            "javascript_class_name": "BinetFormula",
            "display_name": "BinetFormula",
        },
        "PellNumber": {
            "python_class": PellNumber,
            "javascript_class_name": "PellNumber",
            "display_name": "PellNumber",
        },
        "Superfactorial": {
            "python_class": Superfactorial,
            "javascript_class_name": "Superfactorial",
            "display_name": "Superfactorial",
        },
        "Hyperfactorial": {
            "python_class": Hyperfactorial,
            "javascript_class_name": "Hyperfactorial",
            "display_name": "Hyperfactorial",
        },
        "DoubleFactorial": {
            "python_class": DoubleFactorial,
            "javascript_class_name": "DoubleFactorial",
            "display_name": "DoubleFactorial",
        },
        "CoprimeCheck": {
            "python_class": CoprimeCheck,
            "javascript_class_name": "CoprimeCheck",
            "display_name": "CoprimeCheck",
        },
        "EulerMascheroniConstant": {
            "python_class": EulerMascheroniConstant,
            "javascript_class_name": "EulerMascheroniConstant",
            "display_name": "EulerMascheroniConstant",
        },
        "ApérysConstant": {
            "python_class": ApérysConstant,
            "javascript_class_name": "ApérysConstant",
            "display_name": "ApérysConstant",
        },
        "ConwaySequence": {
            "python_class": ConwaySequence,
            "javascript_class_name": "ConwaySequence",
            "display_name": "ConwaySequence",
        },
        "SylvesterSequence": {
            "python_class": SylvesterSequence,
            "javascript_class_name": "SylvesterSequence",
            "display_name": "SylvesterSequence",
        },
        "FibonacciSeries": {
            "python_class": FibonacciSeries,
            "javascript_class_name": "FibonacciSeries",
            "display_name": "FibonacciSeries",
        },
        "LucasSeries": {
            "python_class": LucasSeries,
            "javascript_class_name": "LucasSeries",
            "display_name": "LucasSeries",
        },
        "TriangularSeries": {
            "python_class": TriangularSeries,
            "javascript_class_name": "TriangularSeries",
            "display_name": "TriangularSeries",
        },
        "PentagonalSeries": {
            "python_class": PentagonalSeries,
            "javascript_class_name": "PentagonalSeries",
            "display_name": "PentagonalSeries",
        },
        "HexagonalSeries": {
            "python_class": HexagonalSeries,
            "javascript_class_name": "HexagonalSeries",
            "display_name": "HexagonalSeries",
        },
        "PerfectNumberSeries": {
            "python_class": PerfectNumberSeries,
            "javascript_class_name": "PerfectNumberSeries",
            "display_name": "PerfectNumberSeries",
        },
        "AmicablePairs": {
            "python_class": AmicablePairs,
            "javascript_class_name": "AmicablePairs",
            "display_name": "AmicablePairs",
        },
        "MersennePrimes": {
            "python_class": MersennePrimes,
            "javascript_class_name": "MersennePrimes",
            "display_name": "MersennePrimes",
        },
        "EulerTotientSeries": {
            "python_class": EulerTotientSeries,
            "javascript_class_name": "EulerTotientSeries",
            "display_name": "EulerTotientSeries",
        },
        "MobiusSeries": {
            "python_class": MobiusSeries,
            "javascript_class_name": "MobiusSeries",
            "display_name": "MobiusSeries",
        },
        "SumOfCubes": {
            "python_class": SumOfCubes,
            "javascript_class_name": "SumOfCubes",
            "display_name": "SumOfCubes",
        },
        "ArithmeticMeanArray": {
            "python_class": ArithmeticMeanArray,
            "javascript_class_name": "ArithmeticMeanArray",
            "display_name": "ArithmeticMeanArray",
        },
        "GeometricMeanArray": {
            "python_class": GeometricMeanArray,
            "javascript_class_name": "GeometricMeanArray",
            "display_name": "GeometricMeanArray",
        },
        "HarmonicMeanArray": {
            "python_class": HarmonicMeanArray,
            "javascript_class_name": "HarmonicMeanArray",
            "display_name": "HarmonicMeanArray",
        },
        "MedianArray": {
            "python_class": MedianArray,
            "javascript_class_name": "MedianArray",
            "display_name": "MedianArray",
        },
        "ModeArray": {
            "python_class": ModeArray,
            "javascript_class_name": "ModeArray",
            "display_name": "ModeArray",
        },
        "StandardDeviationArray": {
            "python_class": StandardDeviationArray,
            "javascript_class_name": "StandardDeviationArray",
            "display_name": "StandardDeviationArray",
        },
        "VarianceArray": {
            "python_class": VarianceArray,
            "javascript_class_name": "VarianceArray",
            "display_name": "VarianceArray",
        },
        "Range": {
            "python_class": Range,
            "javascript_class_name": "Range",
            "display_name": "Range",
        },
        "InterquartileRangeArray": {
            "python_class": InterquartileRangeArray,
            "javascript_class_name": "InterquartileRangeArray",
            "display_name": "InterquartileRangeArray",
        },
        "LogarithmicSpiral": {
            "python_class": LogarithmicSpiral,
            "javascript_class_name": "LogarithmicSpiral",
            "display_name": "LogarithmicSpiral",
        },
        "FibonacciSpiral": {
            "python_class": FibonacciSpiral,
            "javascript_class_name": "FibonacciSpiral",
            "display_name": "FibonacciSpiral",
        },
        "GoldenSpiral": {
            "python_class": GoldenSpiral,
            "javascript_class_name": "GoldenSpiral",
            "display_name": "GoldenSpiral",
        },
        "ComplexExponential": {
            "python_class": ComplexExponential,
            "javascript_class_name": "ComplexExponential",
            "display_name": "ComplexExponential",
        },
        "ComplexLogarithm": {
            "python_class": ComplexLogarithm,
            "javascript_class_name": "ComplexLogarithm",
            "display_name": "ComplexLogarithm",
        },
        "ComplexPower": {
            "python_class": ComplexPower,
            "javascript_class_name": "ComplexPower",
            "display_name": "ComplexPower",
        },
        "ComplexRoots": {
            "python_class": ComplexRoots,
            "javascript_class_name": "ComplexRoots",
            "display_name": "ComplexRoots",
        },
        "QuaternionAddition": {
            "python_class": QuaternionAddition,
            "javascript_class_name": "QuaternionAddition",
            "display_name": "QuaternionAddition",
        },
        "QuaternionMultiplication": {
            "python_class": QuaternionMultiplication,
            "javascript_class_name": "QuaternionMultiplication",
            "display_name": "QuaternionMultiplication",
        },
        "QuaternionConjugate": {
            "python_class": QuaternionConjugate,
            "javascript_class_name": "QuaternionConjugate",
            "display_name": "QuaternionConjugate",
        },
        "QuaternionNorm": {
            "python_class": QuaternionNorm,
            "javascript_class_name": "QuaternionNorm",
            "display_name": "QuaternionNorm",
        },
        "QuaternionInverse": {
            "python_class": QuaternionInverse,
            "javascript_class_name": "QuaternionInverse",
            "display_name": "QuaternionInverse",
        },
        "QuaternionRotation": {
            "python_class": QuaternionRotation,
            "javascript_class_name": "QuaternionRotation",
            "display_name": "QuaternionRotation",
        },
        "SphericalToCartesian": {
            "python_class": SphericalToCartesian,
            "javascript_class_name": "SphericalToCartesian",
            "display_name": "SphericalToCartesian",
        },
        "CartesianToSpherical": {
            "python_class": CartesianToSpherical,
            "javascript_class_name": "CartesianToSpherical",
            "display_name": "CartesianToSpherical",
        },
        "EllipticIntegralThirdKind": {
            "python_class": EllipticIntegralThirdKind,
            "javascript_class_name": "EllipticIntegralThirdKind",
            "display_name": "EllipticIntegralThirdKind",
        },
        "JacobiEllipticFunctions": {
            "python_class": JacobiEllipticFunctions,
            "javascript_class_name": "JacobiEllipticFunctions",
            "display_name": "JacobiEllipticFunctions",
        },
        "LambertConformalConicProjection": {
            "python_class": LambertConformalConicProjection,
            "javascript_class_name": "LambertConformalConicProjection",
            "display_name": "LambertConformalConicProjection",
        },
        "MercatorProjection": {
            "python_class": MercatorProjection,
            "javascript_class_name": "MercatorProjection",
            "display_name": "MercatorProjection",
        },
        "HaversineFormula": {
            "python_class": HaversineFormula,
            "javascript_class_name": "HaversineFormula",
            "display_name": "HaversineFormula",
        },
        "BarycentricCoordinates": {
            "python_class": BarycentricCoordinates,
            "javascript_class_name": "BarycentricCoordinates",
            "display_name": "BarycentricCoordinates",
        },
        "BezierCurve": {
            "python_class": BezierCurve,
            "javascript_class_name": "BezierCurve",
            "display_name": "BezierCurve",
        },
        "CatmullRomSpline": {
            "python_class": CatmullRomSpline,
            "javascript_class_name": "CatmullRomSpline",
            "display_name": "CatmullRomSpline",
        },
        "HermiteSpline": {
            "python_class": HermiteSpline,
            "javascript_class_name": "HermiteSpline",
            "display_name": "HermiteSpline",
        },
        "LagrangeInterpolation": {
            "python_class": LagrangeInterpolation,
            "javascript_class_name": "LagrangeInterpolation",
            "display_name": "LagrangeInterpolation",
        },
        "NewtonInterpolation": {
            "python_class": NewtonInterpolation,
            "javascript_class_name": "NewtonInterpolation",
            "display_name": "NewtonInterpolation",
        },
        "SplineInterpolation": {
            "python_class": SplineInterpolation,
            "javascript_class_name": "SplineInterpolation",
            "display_name": "SplineInterpolation",
        },
        "FourierSeries": {
            "python_class": FourierSeries,
            "javascript_class_name": "FourierSeries",
            "display_name": "FourierSeries",
        },
        "ZTransform": {
            "python_class": ZTransform,
            "javascript_class_name": "ZTransform",
            "display_name": "ZTransform",
        },
        "HilbertTransform": {
            "python_class": HilbertTransform,
            "javascript_class_name": "HilbertTransform",
            "display_name": "HilbertTransform",
        },
        "DiscreteCosineTransform": {
            "python_class": DiscreteCosineTransform,
            "javascript_class_name": "DiscreteCosineTransform",
            "display_name": "DiscreteCosineTransform",
        },
        "DiscreteSineTransform": {
            "python_class": DiscreteSineTransform,
            "javascript_class_name": "DiscreteSineTransform",
            "display_name": "DiscreteSineTransform",
        },
        "FastFourierTransform": {
            "python_class": FastFourierTransform,
            "javascript_class_name": "FastFourierTransform",
            "display_name": "FastFourierTransform",
        },
        "InverseFastFourierTransform": {
            "python_class": InverseFastFourierTransform,
            "javascript_class_name": "InverseFastFourierTransform",
            "display_name": "InverseFastFourierTransform",
        },
        "PowerSpectralDensity": {
            "python_class": PowerSpectralDensity,
            "javascript_class_name": "PowerSpectralDensity",
            "display_name": "PowerSpectralDensity",
        },
        "CrossCorrelation": {
            "python_class": CrossCorrelation,
            "javascript_class_name": "CrossCorrelation",
            "display_name": "CrossCorrelation",
        },
        "Autocorrelation": {
            "python_class": Autocorrelation,
            "javascript_class_name": "Autocorrelation",
            "display_name": "Autocorrelation",
        },
        "Convolution": {
            "python_class": Convolution,
            "javascript_class_name": "Convolution",
            "display_name": "Convolution",
        },
        "Deconvolution": {
            "python_class": Deconvolution,
            "javascript_class_name": "Deconvolution",
            "display_name": "Deconvolution",
        },
        "RiemannSum": {
            "python_class": RiemannSum,
            "javascript_class_name": "RiemannSum",
            "display_name": "RiemannSum",
        },
        "MonteCarloIntegration": {
            "python_class": MonteCarloIntegration,
            "javascript_class_name": "MonteCarloIntegration",
            "display_name": "MonteCarloIntegration",
        },
        "SimpsonRule": {
            "python_class": SimpsonRule,
            "javascript_class_name": "SimpsonRule",
            "display_name": "SimpsonRule",
        },
        "TrapezoidalRule": {
            "python_class": TrapezoidalRule,
            "javascript_class_name": "TrapezoidalRule",
            "display_name": "TrapezoidalRule",
        },
        "BisectionMethod": {
            "python_class": BisectionMethod,
            "javascript_class_name": "BisectionMethod",
            "display_name": "BisectionMethod",
        },
        "NewtonRaphsonMethod": {
            "python_class": NewtonRaphsonMethod,
            "javascript_class_name": "NewtonRaphsonMethod",
            "display_name": "NewtonRaphsonMethod",
        },
        "SecantMethod": {
            "python_class": SecantMethod,
            "javascript_class_name": "SecantMethod",
            "display_name": "SecantMethod",
        },
        "GradientDescent": {
            "python_class": GradientDescent,
            "javascript_class_name": "GradientDescent",
            "display_name": "GradientDescent",
        },
        "ConjugateGradient": {
            "python_class": ConjugateGradient,
            "javascript_class_name": "ConjugateGradient",
            "display_name": "ConjugateGradient",
        },
        "LevenbergMarquardt": {
            "python_class": LevenbergMarquardt,
            "javascript_class_name": "LevenbergMarquardt",
            "display_name": "LevenbergMarquardt",
        },
        "JacobianMatrix": {
            "python_class": JacobianMatrix,
            "javascript_class_name": "JacobianMatrix",
            "display_name": "JacobianMatrix",
        },
        "HessianMatrix": {
            "python_class": HessianMatrix,
            "javascript_class_name": "HessianMatrix",
            "display_name": "HessianMatrix",
        },
        "Laplacian": {
            "python_class": Laplacian,
            "javascript_class_name": "Laplacian",
            "display_name": "Laplacian",
        },
        "CovarianceMatrix": {
            "python_class": CovarianceMatrix,
            "javascript_class_name": "CovarianceMatrix",
            "display_name": "CovarianceMatrix",
        },
        "CorrelationMatrix": {
            "python_class": CorrelationMatrix,
            "javascript_class_name": "CorrelationMatrix",
            "display_name": "CorrelationMatrix",
        },
        "ChirpZTransform": {
            "python_class": ChirpZTransform,
            "javascript_class_name": "ChirpZTransform",
            "display_name": "ChirpZTransform",
        },
        "KalmanFilter": {
            "python_class": KalmanFilter,
            "javascript_class_name": "KalmanFilter",
            "display_name": "KalmanFilter",
        },
        "ParticleFilter": {
            "python_class": ParticleFilter,
            "javascript_class_name": "ParticleFilter",
            "display_name": "ParticleFilter",
        },
        "SphericalHarmonics": {
            "python_class": SphericalHarmonics,
            "javascript_class_name": "SphericalHarmonics",
            "display_name": "SphericalHarmonics",
        },
        "LegendreTransform": {
            "python_class": LegendreTransform,
            "javascript_class_name": "LegendreTransform",
            "display_name": "LegendreTransform",
        },
        "BesselZeros": {
            "python_class": BesselZeros,
            "javascript_class_name": "BesselZeros",
            "display_name": "BesselZeros",
        },
        "AiryFunction": {
            "python_class": AiryFunction,
            "javascript_class_name": "AiryFunction",
            "display_name": "AiryFunction",
        },
        "WeierstrassFunction": {
            "python_class": WeierstrassFunction,
            "javascript_class_name": "WeierstrassFunction",
            "display_name": "WeierstrassFunction",
        },
        "LaméFunction": {
            "python_class": LaméFunction,
            "javascript_class_name": "LaméFunction",
            "display_name": "LaméFunction",
        },
        "MinkowskiDistance": {
            "python_class": MinkowskiDistance,
            "javascript_class_name": "MinkowskiDistance",
            "display_name": "MinkowskiDistance",
        },
        "ChebyshevDistance": {
            "python_class": ChebyshevDistance,
            "javascript_class_name": "ChebyshevDistance",
            "display_name": "ChebyshevDistance",
        },
        "MahalanobisDistance": {
            "python_class": MahalanobisDistance,
            "javascript_class_name": "MahalanobisDistance",
            "display_name": "MahalanobisDistance",
        },
        "JaccardIndex": {
            "python_class": JaccardIndex,
            "javascript_class_name": "JaccardIndex",
            "display_name": "JaccardIndex",
        },
        "CosineSimilarity": {
            "python_class": CosineSimilarity,
            "javascript_class_name": "CosineSimilarity",
            "display_name": "CosineSimilarity",
        },
        "HammingDistance": {
            "python_class": HammingDistance,
            "javascript_class_name": "HammingDistance",
            "display_name": "HammingDistance",
        },
        "EditDistance": {
            "python_class": EditDistance,
            "javascript_class_name": "EditDistance",
            "display_name": "EditDistance",
        },
        "KullbackLeiblerDivergence": {
            "python_class": KullbackLeiblerDivergence,
            "javascript_class_name": "KullbackLeiblerDivergence",
            "display_name": "KullbackLeiblerDivergence",
        },
        "BhattacharyyaDistance": {
            "python_class": BhattacharyyaDistance,
            "javascript_class_name": "BhattacharyyaDistance",
            "display_name": "BhattacharyyaDistance",
        },
        "EarthMoverDistance": {
            "python_class": EarthMoverDistance,
            "javascript_class_name": "EarthMoverDistance",
            "display_name": "EarthMoverDistance",
        },
        "EntropyShannon": {
            "python_class": EntropyShannon,
            "javascript_class_name": "EntropyShannon",
            "display_name": "EntropyShannon",
        },
        "GiniCoefficient": {
            "python_class": GiniCoefficient,
            "javascript_class_name": "GiniCoefficient",
            "display_name": "GiniCoefficient",
        },
        "LorenzCurve": {
            "python_class": LorenzCurve,
            "javascript_class_name": "LorenzCurve",
            "display_name": "LorenzCurve",
        },
        "PageRank": {
            "python_class": PageRank,
            "javascript_class_name": "PageRank",
            "display_name": "PageRank",
        },
        "SpectralRadius": {
            "python_class": SpectralRadius,
            "javascript_class_name": "SpectralRadius",
            "display_name": "SpectralRadius",
        },
        "MatrixExponential": {
            "python_class": MatrixExponential,
            "javascript_class_name": "MatrixExponential",
            "display_name": "MatrixExponential",
        },
        "FrobeniusNorm": {
            "python_class": FrobeniusNorm,
            "javascript_class_name": "FrobeniusNorm",
            "display_name": "FrobeniusNorm",
        },
        "HouseholderTransformation": {
            "python_class": HouseholderTransformation,
            "javascript_class_name": "HouseholderTransformation",
            "display_name": "HouseholderTransformation",
        },
        "GramSchmidtProcess": {
            "python_class": GramSchmidtProcess,
            "javascript_class_name": "GramSchmidtProcess",
            "display_name": "GramSchmidtProcess",
        },
        "QRAlgorithm": {
            "python_class": QRAlgorithm,
            "javascript_class_name": "QRAlgorithm",
            "display_name": "QRAlgorithm",
        },
        "CholeskyFactorization": {
            "python_class": CholeskyFactorization,
            "javascript_class_name": "CholeskyFactorization",
            "display_name": "CholeskyFactorization",
        },
        "LUFactorization": {
            "python_class": LUFactorization,
            "javascript_class_name": "LUFactorization",
            "display_name": "LUFactorization",
        },
        "QRFactorization": {
            "python_class": QRFactorization,
            "javascript_class_name": "QRFactorization",
            "display_name": "QRFactorization",
        },
        "EigenDecomposition": {
            "python_class": EigenDecomposition,
            "javascript_class_name": "EigenDecomposition",
            "display_name": "EigenDecomposition",
        },
        "MatrixConditionNumber": {
            "python_class": MatrixConditionNumber,
            "javascript_class_name": "MatrixConditionNumber",
            "display_name": "MatrixConditionNumber",
        },
        "MatrixNullSpace": {
            "python_class": MatrixNullSpace,
            "javascript_class_name": "MatrixNullSpace",
            "display_name": "MatrixNullSpace",
        },
        "MatrixColumnSpace": {
            "python_class": MatrixColumnSpace,
            "javascript_class_name": "MatrixColumnSpace",
            "display_name": "MatrixColumnSpace",
        },
        "MatrixRowSpace": {
            "python_class": MatrixRowSpace,
            "javascript_class_name": "MatrixRowSpace",
            "display_name": "MatrixRowSpace",
        },
        "MatrixAdjugate": {
            "python_class": MatrixAdjugate,
            "javascript_class_name": "MatrixAdjugate",
            "display_name": "MatrixAdjugate",
        },
        "MatrixCofactor": {
            "python_class": MatrixCofactor,
            "javascript_class_name": "MatrixCofactor",
            "display_name": "MatrixCofactor",
        },
        "MatrixHadamardProduct": {
            "python_class": MatrixHadamardProduct,
            "javascript_class_name": "MatrixHadamardProduct",
            "display_name": "MatrixHadamardProduct",
        },
        "MatrixKroneckerProduct": {
            "python_class": MatrixKroneckerProduct,
            "javascript_class_name": "MatrixKroneckerProduct",
            "display_name": "MatrixKroneckerProduct",
        },
        "MatrixTrace": {
            "python_class": MatrixTrace,
            "javascript_class_name": "MatrixTrace",
            "display_name": "MatrixTrace",
        },
        "MatrixPower": {
            "python_class": MatrixPower,
            "javascript_class_name": "MatrixPower",
            "display_name": "MatrixPower",
        },
        "MatrixLogarithm": {
            "python_class": MatrixLogarithm,
            "javascript_class_name": "MatrixLogarithm",
            "display_name": "MatrixLogarithm",
        },
        "MatrixSquareRoot": {
            "python_class": MatrixSquareRoot,
            "javascript_class_name": "MatrixSquareRoot",
            "display_name": "MatrixSquareRoot",
        },
        "MatrixExponentialMap": {
            "python_class": MatrixExponentialMap,
            "javascript_class_name": "MatrixExponentialMap",
            "display_name": "MatrixExponentialMap",
        },
        "MatrixLogarithmMap": {
            "python_class": MatrixLogarithmMap,
            "javascript_class_name": "MatrixLogarithmMap",
            "display_name": "MatrixLogarithmMap",
        },
        "MatrixPseudoinverse": {
            "python_class": MatrixPseudoinverse,
            "javascript_class_name": "MatrixPseudoinverse",
            "display_name": "MatrixPseudoinverse",
        },
        "ToeplitzMatrix": {
            "python_class": ToeplitzMatrix,
            "javascript_class_name": "ToeplitzMatrix",
            "display_name": "ToeplitzMatrix",
        },
        "VandermondeMatrix": {
            "python_class": VandermondeMatrix,
            "javascript_class_name": "VandermondeMatrix",
            "display_name": "VandermondeMatrix",
        },
        "HilbertMatrix": {
            "python_class": HilbertMatrix,
            "javascript_class_name": "HilbertMatrix",
            "display_name": "HilbertMatrix",
        },
        "CayleyHamiltonTheorem": {
            "python_class": CayleyHamiltonTheorem,
            "javascript_class_name": "CayleyHamiltonTheorem",
            "display_name": "CayleyHamiltonTheorem",
        },
        "MatrixNorm": {
            "python_class": MatrixNorm,
            "javascript_class_name": "MatrixNorm",
            "display_name": "MatrixNorm",
        },
        "MatrixPolarDecomposition": {
            "python_class": MatrixPolarDecomposition,
            "javascript_class_name": "MatrixPolarDecomposition",
            "display_name": "MatrixPolarDecomposition",
        },
        "MatrixSchurDecomposition": {
            "python_class": MatrixSchurDecomposition,
            "javascript_class_name": "MatrixSchurDecomposition",
            "display_name": "MatrixSchurDecomposition",
        },
        "MatrixSylvesterEquation": {
            "python_class": MatrixSylvesterEquation,
            "javascript_class_name": "MatrixSylvesterEquation",
            "display_name": "MatrixSylvesterEquation",
        },
        "MatrixLyapunovEquation": {
            "python_class": MatrixLyapunovEquation,
            "javascript_class_name": "MatrixLyapunovEquation",
            "display_name": "MatrixLyapunovEquation",
        },
    },
    "rules": {},
}
