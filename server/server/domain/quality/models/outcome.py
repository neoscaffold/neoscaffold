from typing import Dict

from ...utilities.generate_id import generate_id
from .cause import Cause


from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Outcome(DataClassJSONMixin):
    uid: str = field(default_factory=generate_id)
    rule: Any = None
    passed: bool = False
    causes: Dict[str, Cause] = field(default_factory=dict)

    def __init__(
        self,
        rule,
        passed: bool,
        causes: Dict[str, Cause],
    ):
        self.uid = generate_id()
        self.rule = rule

        self.passed = passed
        self.causes = causes

    def __eq__(self, other):
        return (
            self.rule.name == other.rule.name
            # and self.rule.get_inputs == other.rule.get_inputs
            and
            # the products are not included in the equality check
            # self.rule.get_products == other.rule.get_products and
            self.passed == other.passed
            and self.causes == other.causes
        )

    def __lt__(self, other):
        return self.uid < other.uid

    def add_cause(self, cause: Cause):
        self.causes[cause.uid] = cause

    def remove_cause(self, cause: Cause):
        del self.causes[cause.uid]

    def remove_all_causes(self):
        self.causes = {}
