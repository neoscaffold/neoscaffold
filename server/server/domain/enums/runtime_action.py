from enum import IntEnum


class RuntimeAction(IntEnum):
    """
    EVALUATE
    RETURN
    BYPASS
    GOTO
    """

    EVALUATE = 0  # evaluate the node and continue
    RETURN = 1  # return from workflow
    BYPASS = 2  # bypass the node and continue
    GOTO = 3  # goto a specific node and continue
