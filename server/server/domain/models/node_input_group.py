from dataclasses import dataclass, field
from typing import Dict
from mashumaro.mixins.json import DataClassJSONMixin
from .node_input import NodeInput


@dataclass(slots=True)
class NodeInputGroup(DataClassJSONMixin):
    node_id: str = ""
    required_inputs: Dict[str, NodeInput] = field(default_factory={})  # type: ignore
    optional_inputs: Dict[str, NodeInput] = field(default_factory={})  # type: ignore

    # implements the get used for dictionary access
    def get(self, path: str, *args):
        if path == "node_id":
            return self.node_id
        if path == "required_inputs":
            return self.required_inputs
        if path == "optional_inputs":
            return self.optional_inputs
        return None
