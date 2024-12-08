# rule_instance = server.rules.get("TextLength").get("python_class")()

# rule = Rule(
#     name="TextLength",
#     class_instance=rule_instance,
# )

# # create dummy parameter group from user specified in ui
# parameter_group = rule.parameter_template()

# parameter_group.required_parameters["value_path"].values = [
#     "input",
#     "required_inputs",
#     "body",
#     "values",
# ]
# parameter_group.optional_parameters["max_length"].values = 5

# rule.parameters = parameter_group

# # create dummy evaluation source
# ni = NodeInput(values="Can you please let us know more details about your ")
# ng = NodeInputGroup(node_id="", required_inputs={"body": ni}, optional_inputs={})
# datasource = {"input": ng}

# source = Source(datasource)

# print(server.rules)

# evl = Evaluator()
# evl.set_rules(rule)

# result = evl.evaluate(source)

# print(result.passed)
# print(result)