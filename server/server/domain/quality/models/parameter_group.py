from dataclasses import dataclass, field
from typing import Dict
from mashumaro.mixins.json import DataClassJSONMixin
from .parameter import Parameter


@dataclass(slots=True)
class ParameterGroup(DataClassJSONMixin):
    rule_id: str = ""
    required_parameters: Dict[str, Parameter] = field(default_factory={})  # type: ignore
    optional_parameters: Dict[str, Parameter] = field(default_factory={})  # type: ignore

    # implements the get used for dictionary access
    def get(self, path: str, *args):
        if path == "required_parameters":
            return self.required_parameters
        if path == "optional_parameters":
            return self.optional_parameters
        return None
