from ...utilities.generate_id import generate_id
from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, field


@dataclass(slots=True)
class Cause(DataClassJSONMixin):
    uid: str = field(default_factory=generate_id)
    message: str = ""
    outliers: dict = field(default_factory=dict)
