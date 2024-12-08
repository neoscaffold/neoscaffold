from ..decorators.time_duration import time_duration


@time_duration("Callback duration:")
def run_callback(
    self,
    callback,
    source=None,
    result=None,
):
    return callback(self, source=source, result=result)
