import traceback


def make_stack_trace_dict(e):
    # create a dict that displays the stack trace
    # serialize the traceback
    tb_dict = {i: line for i, line in enumerate(traceback.format_tb(e.__traceback__))}

    stack_trace = {
        "message": f"{type(e).__name__}: {str(e)}",
        "stack_trace": tb_dict,
    }

    return stack_trace
