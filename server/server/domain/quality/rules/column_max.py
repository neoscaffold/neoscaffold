# TODO (OSS): What are the "core" / build-in rules and nodes?

# import logging

# from ...enums.severity_level import SeverityLevel
# from ..models.cause import Cause
# from ..models.outcome import Outcome
# from ..models.rule import Rule
# from ..models.source import Source


# class ColumnMax(Rule):
#     def __init__(
#         self,
#         column,
#         max_numeric=None,
#         min_numeric=None,
#         name="ColumnMax",
#         description="Validates that the max value of a column is within a threshold",
#         severity_level=SeverityLevel.CRITICAL,
#         logger: logging.Logger = logging.getLogger(),
#     ):
#         if max_numeric is None and min_numeric is None:
#             raise ValueError("Must provide a max or min value")

#         self._max_numeric = max_numeric
#         self._min_numeric = min_numeric

#         self._severity_level = severity_level
#         self._logger = logger

#         self._column = column

#         super().__init__(
#             name,
#             description,
#         )

#     def evaluate_outcome(self, source: Source) -> Outcome:
#         self.max_result = None
#         if source.datasource is not None:
#             if hasattr(source.datasource, "max"):
#                 max_result = source.datasource.max(on=self.column)
#                 self.max_result = max_result

#         outcome = Outcome(
#             passed=True,
#             causes={},
#             rule=self,
#         )

#         if max_result is None:
#             outcome.passed = False
#             outcome.add_cause(
#                 Cause(
#                     message=f"Input data does not have a max value for column {self.column}",
#                     severity_level=SeverityLevel.CRITICAL,
#                     rule=self,
#                 )
#             )

#         if self.max_numeric is not None and max_result > self.max_numeric:
#             outcome.passed = False
#             outcome.add_cause(
#                 Cause(
#                     message=f"Max value of {max_result} is greater than {self.max_numeric}",
#                     outliers={
#                         "max_result": max_result,
#                         "max_numeric": self.max_numeric,
#                     },
#                     severity_level=SeverityLevel.CRITICAL,
#                     rule=self,
#                 )
#             )

#         if self.min_numeric is not None and max_result < self.min_numeric:
#             outcome.passed = False
#             outcome.add_cause(
#                 Cause(
#                     message=f"Max value of {max_result} is less than {self.min_numeric}",
#                     outliers={
#                         "max_result": max_result,
#                         "min_numeric": self.min_numeric,
#                     },
#                     severity_level=SeverityLevel.CRITICAL,
#                     rule=self,
#                 )
#             )

#         return outcome

#     def get_inputs(self):
#         return {
#             "column": self.column,
#             "max_numeric": self.max_numeric,
#             "min_numeric": self.min_numeric,
#         }

#     def get_products(self):
#         return {"max_result": self.max_result}
