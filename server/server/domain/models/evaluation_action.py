from dataclasses import dataclass
from mashumaro.mixins.json import DataClassJSONMixin

from ..enums.runtime_action import RuntimeAction


@dataclass(slots=True)
class EvaluationAction(DataClassJSONMixin):
    node_id: str = ""
    runtime_action: RuntimeAction = RuntimeAction.EVALUATE
    destination_node_id: str = ""

    # implements the get used for dictionary access
    def get(self, path: str, *args):
        if path == "node_id":
            return self.node_id
        if path == "destination_node_id":
            return self.destination_node_id
        if path == "runtime_action":
            return self.runtime_action
        return None
