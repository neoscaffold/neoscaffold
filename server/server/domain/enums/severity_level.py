from enum import IntEnum


class SeverityLevel(IntEnum):
    """
    SEV 1 "CRITICAL"
    SEV 2 "MAJOR"
    SEV 3 "MINOR"
    SEV 4 "WARNING"
    SEV 5 "INFO"
    """

    CRITICAL = 1
    MAJOR = 2
    MINOR = 3
    WARNING = 4
    INFO = 5
