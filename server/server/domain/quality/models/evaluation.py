from typing import Dict

from ...utilities.generate_id import generate_id
from .outcome import Outcome

from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, field


@dataclass(slots=True)
class Evaluation(DataClassJSONMixin):
    uid: str = field(default_factory=generate_id)
    passed: bool = False
    outcomes: Dict[str, Outcome] = field(default_factory=dict)

    def __init__(self, passed: bool, outcomes: Dict[str, Outcome]):
        self.uid = generate_id()
        self.passed = passed
        self.outcomes = outcomes

    def __eq__(self, other):
        all_outcomes_match = True
        if len(self.outcomes) != len(other.outcomes):
            all_outcomes_match = False
        else:
            for x, y in zip(self.outcomes, other.outcomes):
                if x != y:
                    all_outcomes_match = False
                    break

        return bool((self.passed == other.passed) and all_outcomes_match)

    def __lt__(self, other):
        return self.uid < other.uid
