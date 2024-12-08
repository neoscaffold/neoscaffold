from typing import Any, List

from ...enums.severity_level import SeverityLevel
from ...decorators.time_duration import time_duration
from ...utilities.generate_id import generate_id
from ...utilities.get_nested import get_nested
from ...utilities.resolve_property_path import resolve_value_path
from ...utilities.run_callback import run_callback
from .outcome import Outcome
from .source import Source
from .parameter_group import ParameterGroup
from .parameter import Parameter
from .cause import Cause


from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, asdict, field


@dataclass(slots=True)
class Rule(DataClassJSONMixin):
    rule_id: str = field(default_factory=generate_id)
    name: str = "Unnamed Rule"
    class_instance: Any = field(default=None)
    parameters: ParameterGroup = field(default=None)
    description: str = "No description"
    severity_level: SeverityLevel = SeverityLevel.CRITICAL
    pre_evaluate_callbacks: List = field(default_factory=list)
    post_evaluate_callbacks: List = field(default_factory=list)

    def __init__(
        self,
        name="Unnamed Rule",
        class_instance=None,
        parameters=None,
        description="No description",
        severity_level=SeverityLevel.CRITICAL,
    ):
        self.rule_id = generate_id()
        self.name = name
        self.class_instance = class_instance

        self.parameters = parameters

        self.description = description

        self.severity_level = severity_level

        self.pre_evaluate_callbacks: List = []
        self.post_evaluate_callbacks: List = []

    def to_dict(self):
        return asdict(self)

    @time_duration("Rule duration:")
    def _evaluate(self, source: Source) -> Outcome:
        """Evaluate the rule."""

        self._pre_evaluate(source)

        if self.class_instance is None:
            raise ValueError(f"Node {self.name} has no class instance")

        # preprocess source into format for rule class instance
        source_input = source.datasource

        if (
            self.parameters
            and self.parameters.required_parameters.get("value_path")
            and self.parameters.required_parameters.get("value_path").get("values")
        ):
            value_path_list = resolve_value_path(
                self.parameters.required_parameters.get("value_path").get("values", "")
            )
            source_input = get_nested(source_input, *value_path_list)

        # Evaluate the rule
        outcome_dict = self.class_instance.evaluate(source_input, self.parameters)

        causes = {
            cause_id: Cause.from_dict(c)
            for cause_id, c in outcome_dict.get("causes", {}).items()
        }
        outcome = Outcome(
            rule=self, passed=outcome_dict.get("passed", False), causes=causes
        )

        self._post_evaluate(source, outcome)

        return outcome

    def parameter_template(self) -> ParameterGroup:
        required_parameters = {
            k: Parameter.from_dict(v)
            for k, v in self.class_instance.PARAMETERS.get(
                "required_parameters", {}
            ).items()
        }
        optional_parameters = {
            k: Parameter.from_dict(v)
            for k, v in self.class_instance.PARAMETERS.get(
                "optional_parameters", {}
            ).items()
        }

        optional_parameters["rule_group"] = Parameter(
            kind="rule_group", name="rule_group"
        )

        parameter_template = ParameterGroup(
            rule_id=self.rule_id,
            required_parameters=required_parameters,
            optional_parameters=optional_parameters,
        )
        parameter_template.rule_id = self.rule_id
        return parameter_template

    def _pre_evaluate(self, source: Source):
        """Callbacks will run before the evaluate"""
        for callback in self.pre_evaluate_callbacks:
            run_callback(self, callback, source)

    def _post_evaluate(self, source, outcome: Outcome):
        """Callbacks will run after the evaluate"""
        for callback in self.post_evaluate_callbacks:
            run_callback(self, callback, source, outcome)

    def __lt__(self, other):
        return self.rule_id < other.rule_id

    def __eq__(self, other):
        return self.rule_id == other.rule_id

    def __iter__(self):
        out = {
            "id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "severity_level": self.severity_level,
            "pre_evaluate_callbacks": self.pre_evaluate_callbacks,
            "post_evaluate_callbacks": self.post_evaluate_callbacks,
        }
        for key, value in out.items():
            yield key, value
