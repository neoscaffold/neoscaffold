from dataclasses import asdict, dataclass, field
import json
from typing import Any, List, Optional

from ..quality.models.evaluation import Evaluation
from ..quality.models.rule import Rule

from ..quality.models.evaluator import Evaluator
from ..quality.models.source import Source

from ..utilities.generate_id import generate_id
from ..utilities.run_callback import run_callback

from .node_input_group import NodeInputGroup
from .node_input import NodeInput
from .node_output import NodeOutput
from mashumaro.mixins.json import DataClassJSONMixin


@dataclass(slots=True)
class Node(DataClassJSONMixin):
    """An abstract node object that represents a node in the system."""

    node_id: str = field(default_factory=generate_id)
    name: str = ""
    class_instance: Any = field(default=None)

    inputs: dict = field(default_factory=dict)
    _input_validator: Optional[Evaluator] = field(default=None)
    _output_validator: Optional[Evaluator] = field(default=None)
    pre_evaluate_callbacks: List = field(default_factory=list)
    post_evaluate_callbacks: List = field(default_factory=list)

    def __init__(self, node_id="", name="", class_instance=None):
        self.name = name
        self.class_instance = class_instance

        if node_id:
            self.node_id = node_id
        else:
            self.node_id = generate_id()

        self.inputs: dict = {}

        self.pre_evaluate_callbacks: List = []
        self.post_evaluate_callbacks: List = []

    def to_dict(self):
        return asdict(self)

    # @time_duration("Node duration:")
    def _evaluate(self, node_inputs: NodeInputGroup) -> NodeOutput:
        """Evaluate the node."""

        node_output = self.output_template()

        # fix any required node_input that is a NodeOutput
        for value in node_inputs.required_inputs.values():
            if hasattr(value, "values"):
                # if it is a NodeOutput
                if hasattr(value.values, "node_id"):
                    value.values = value.values.values

        # fix any optional node_input that is a NodeOutput
        for value in node_inputs.optional_inputs.values():
            if hasattr(value, "values"):
                # if it is a NodeOutput
                if hasattr(value.values, "node_id"):
                    value.values = value.values.values

        try:
            input_evaluation = self._validate_inputs(node_inputs)
            node_output.input_evaluation = input_evaluation
            if input_evaluation is not None and not input_evaluation.passed:
                raise Exception(
                    f"FAILED: input validation for {self.name}, id: {self.node_id} failed"
                    + f"\n{input_evaluation.outcomes}"
                )
        except Exception as e:
            raise e

        self._pre_evaluate(node_inputs)

        if self.class_instance is None:
            raise ValueError(f"Node {self.name} has no class instance")

        # Evaluate the node
        output = self.class_instance.evaluate(node_inputs.to_dict())

        node_output.values = output

        output_evaluation = Evaluation(passed=True, outcomes={})
        try:
            output_evaluation = self._validate_output(node_inputs, node_output)
            node_output.output_evaluation = output_evaluation
            if output_evaluation is not None and not output_evaluation.passed:
                raise Exception(
                    f"FAILED: output validation for {self.name}, id: {self.node_id} failed"
                    + f"\n{output_evaluation.outcomes}"
                )
        except Exception as e:
            raise e

        self._post_evaluate(node_inputs, node_output)
        return node_output

    def input_template(self) -> NodeInputGroup:
        required_inputs = {
            k: NodeInput.from_dict(v)
            for k, v in self.class_instance.INPUT.get("required_inputs", {}).items()
        }
        optional_inputs = {
            k: NodeInput.from_dict(v)
            for k, v in self.class_instance.INPUT.get("optional_inputs", {}).items()
        }

        # all nodes have in_rules and out_rules
        optional_inputs["in_rules"] = NodeInput(kind="rule_group", name="in_rules")
        optional_inputs["out_rules"] = NodeInput(kind="rule_group", name="out_rules")

        input_types = NodeInputGroup(
            node_id=self.node_id,
            required_inputs=required_inputs,
            optional_inputs=optional_inputs,
        )

        input_types.node_id = self.node_id
        return input_types

    def output_template(self) -> NodeOutput:
        output_types = NodeOutput(
            node_id=self.node_id,
            kind=self.class_instance.OUTPUT.get("kind", ""),
            name=self.class_instance.OUTPUT.get("name", ""),
            cacheable=self.class_instance.OUTPUT.get("cacheable", False),
        )
        return output_types

    def set_input_rules(self, *rules: Rule):
        if not hasattr(self, "_input_validator"):
            self._input_validator = Evaluator()
        self._input_validator.set_rules(*rules)

    def set_output_rules(self, *rules: Rule):
        if not hasattr(self, "_output_validator"):
            self._output_validator = Evaluator()
        self._output_validator.set_rules(*rules)

    def _pre_evaluate(self, node_inputs: NodeInputGroup):
        """Callbacks will run before the evaluate"""
        for callback in self.pre_evaluate_callbacks:
            run_callback(self, callback, node_inputs)

    def _post_evaluate(self, node_inputs: NodeInputGroup, output: NodeOutput):
        """Callbacks will run after the evaluate"""
        for callback in self.post_evaluate_callbacks:
            run_callback(self, callback, node_inputs, output)

    def _validate_inputs(self, node_inputs: NodeInputGroup):
        """Validate the input group with any specified rules"""
        if not hasattr(self, "_input_validator"):
            return
        if len(self._input_validator.rules) < 1:
            return
        return self._input_validator.evaluate(
            Source(
                {
                    "input": node_inputs,
                }
            )
        )

    def _validate_output(self, node_inputs: NodeInputGroup, output: NodeOutput):
        """
        Validate the output with any specified rules
        TODO: root cause analysis with node from output (consider passing in self-reference)
        """
        if not hasattr(self, "_output_validator"):
            return
        if len(self._output_validator.rules) < 1:
            return
        output = self._output_validator.evaluate(
            Source(
                {
                    "output": output,
                    # input can be helpful in quality checks for output sometimes
                    "input": node_inputs,
                }
            )
        )
        return output

    def __lt__(self, other):
        return self.node_id < other.id

    def __eq__(self, other):
        return self.node_id == other.id

    def __iter__(self):
        out = {
            "id": self.node_id,
            "name": self.name,
        }
        for key, value in out.items():
            yield key, value

    def __repr__(self):
        return json.dumps(dict(self))

    def __str__(self):
        return self.__repr__()
