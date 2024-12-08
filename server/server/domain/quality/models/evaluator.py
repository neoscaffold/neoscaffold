from multiprocessing import pool

from ...enums.severity_level import SeverityLevel

from ...utilities.generate_id import generate_id
from .outcome import Outcome
from .evaluation import Evaluation

from mashumaro.mixins.json import DataClassJSONMixin
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass(slots=True)
class Evaluator(DataClassJSONMixin):
    uid: str = field(default_factory=generate_id)
    rules: List = field(default_factory=list)

    def __init__(self, *rules):
        self.uid = generate_id()
        self.set_rules(*rules)

    def to_dict(self):
        return asdict(self)

    def set_rules(self, *rules):
        sorted_rules = sorted(rules)
        self.rules = sorted_rules
        return self

    def _process_evaluation(self, rule_source):
        rule, source = rule_source
        return rule._evaluate(source)

    def evaluate(self, source, minimum_severity=SeverityLevel.MINOR):
        evaluation_id = generate_id()
        results = []
        try:
            print(f"Starting evaluation {evaluation_id} for {self.uid}")

            batches = list(zip(self.rules, [source] * len(self.rules)))

            batchLength = len(batches)

            if batchLength:
                with pool.ThreadPool(batchLength) as p:
                    results = results + p.map(self._process_evaluation, batches)

            print(f"Finished evaluation {evaluation_id} for {self.uid}")

            evaluation = Evaluation(passed=True, outcomes=results)

            try:
                evaluation.passed = next(
                    False
                    for r in results
                    if self._not_passing_and_severe(r, minimum_severity)
                )
            except StopIteration:
                print("all checks passed")

            return evaluation

        except Exception as e:
            print(f"Failed evaluation {evaluation_id} for {self.uid}")
            raise e

    def comparison_evaluation(
        self,
        *sources_severity_pairs,
    ):
        if len(sources_severity_pairs) < 2:
            raise ValueError("Must provide at least two sources to compare")

        results = [
            self.evaluate(sourcePair[0], sourcePair[1])
            for sourcePair in sources_severity_pairs
        ]
        evaluation = Evaluation(passed=True, outcomes=results)
        try:
            evaluation.passed = next(False for r in results if not results[0] == r)
        except StopIteration:
            print("all checks passed")

        return evaluation

    def _not_passing_and_severe(
        self, outcome: Outcome, minimum_severity: SeverityLevel
    ) -> bool:
        list_of_severity = [
            SeverityLevel(sev) for sev in range(minimum_severity.value, 0, -1)
        ]
        return bool(
            (not outcome.passed) and (outcome.rule.severity_level in list_of_severity)
        )

    def __lt__(self, other) -> bool:
        return bool(self.uid < other.uid)
