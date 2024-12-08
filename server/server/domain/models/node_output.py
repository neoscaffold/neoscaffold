from dataclasses import dataclass
from typing import Optional
from mashumaro.mixins.json import DataClassJSONMixin
from ..quality.models.evaluation import Evaluation


@dataclass(slots=True)
class NodeOutput(DataClassJSONMixin):
    kind: str = ""
    name: str = ""
    node_id: str = ""
    values: str = ""
    cacheable: bool = False
    input_evaluation: Optional[Evaluation] = None
    output_evaluation: Optional[Evaluation] = None

    # implements the get used for dictionary access
    def get(self, path: str, *args):
        if path == "kind":
            return self.kind
        if path == "name":
            return self.name
        if path == "node_id":
            return self.node_id
        if path == "values":
            return self.values
        if path == "cacheable":
            return self.cacheable
        if path == "input_evaluation":
            return self.input_evaluation
        if path == "output_evaluation":
            return self.output_evaluation
        return None
