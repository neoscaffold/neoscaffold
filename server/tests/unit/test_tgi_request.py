from server import SeverityLevel, Cause, Outcome, Rule, TGIRequest, NodeInputGroup, NodeInput

import json

class TextLength(Rule):
    def __init__(
        self,
        value_path,
        max_numeric=None,
        min_numeric=None,
        name="TextLength",
        description="Validates that the length of a string is within a threshold",
        severity_level=SeverityLevel.CRITICAL,
        logger: logging.Logger = logging.getLogger(),
    ):
        if max_numeric is None and min_numeric is None:
            raise ValueError("Must provide a max or min value")

        self.value_path = value_path
        self.max_numeric = max_numeric
        self.min_numeric = min_numeric

        self._severity_level = severity_level
        self._logger = logger

        super().__init__(
            name,
            description,
        )

    def get_nested(self, data, *args):
        print(f"data {data}")
        if args and data:
            element = args[0]
            if element:
                value = data.get(element)
                return value if len(args) == 1 else self.get_nested(value, *args[1:])
        return None

    def evaluate_outcome(self, source) -> Outcome:
        str_length = len(
            self.get_nested(source, *self.value_path)
        )
        self.str_length = str_length

        outcome = Outcome(
            passed=True,
            causes={},
            rule=self,
        )

        if self.max_numeric is not None and str_length > self.max_numeric:
            outcome.passed = False
            outcome.add_cause(
                Cause(
                    message=f"String length of {str_length} is greater than {self.max_numeric}",
                    outliers=[str_length],
                    severity_level=SeverityLevel.CRITICAL,
                    rule=self,
                )
            )

        if self.min_numeric is not None and str_length < self.min_numeric:
            outcome.passed = False
            outcome.add_cause(
                Cause(
                    message=f"String length of {str_length} is less than {self.min_numeric}",
                    outliers=[str_length],
                    severity_level=SeverityLevel.CRITICAL,
                    rule=self,
                )
            )

        return outcome

    def get_inputs(self):
        return {
            "column": self.column,
            "max_numeric": self.max_numeric,
            "min_numeric": self.min_numeric,
        }

    def get_products(self):
        return {"str_length": self.str_length}

def test_tgi_request():

    # create a prompt
    prompt = json.dumps({
        "inputs": "Can you please let us know more details about your ",
        "parameters": {}
    })

    node_input_group = NodeInputGroup(
        required_inputs={
            "uri": NodeInput(values='http://127.1.1.1/'),
            "body": NodeInput(values=prompt)
        }
    )

    # create an Input Validation Rule
    length_rule = TextLength(
        value_path=["datasource", "input", "required_inputs", "body", "values"],
        max_numeric=100,
        description="Validates outbound json payload is less than 100 chars"
    )

    # create an Output Validation Rule
    out_length_rule = TextLength(
        value_path=["datasource", "output", "values"],
        max_numeric=700,
        description="Validates inbound json payload is less than 700 chars"
    )

    # create a TGIRequest
    tgi_request = TGIRequest(
        name="TGIRequest",
        node_id="1"
    )
    tgi_request.set_input_rules(length_rule)
    tgi_request.set_output_rules(out_length_rule)

    out = tgi_request._evaluate(
        node_input_group
    )
    print(out)
