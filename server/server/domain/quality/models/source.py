from dataclasses import dataclass, asdict
from typing import Union

from ...models.node_input import NodeInput
from ...models.node_input_group import NodeInputGroup
from ...models.node_output import NodeOutput


from mashumaro.mixins.json import DataClassJSONMixin


@dataclass(slots=True)
class Source(DataClassJSONMixin):
    datasource: Union[NodeInput, NodeInputGroup, NodeOutput, dict]

    def get(self, path: str):
        if path == "datasource":
            return self.datasource
        return None

    def to_dict(self):
        return asdict(self)
