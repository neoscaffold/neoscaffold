from dataclasses import dataclass, field
from typing import Any
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.config import BaseConfig


@dataclass(slots=True)
class Parameter(DataClassJSONMixin):
    kind: str = ""
    name: str = ""
    values: Any = field(default=None)
    widget: Any = field(default=None)

    class Config(BaseConfig):
        omit_none = True

    # implements the get used for dictionary access
    def get(self, path: str, *args):
        if path == "kind":
            return self.kind
        if path == "name":
            return self.name
        if path == "values":
            return self.values
        if path == "widget":
            return self.widget
        return None
