from enum import Enum, auto


class State(Enum):
    DEFAULT = auto()
    STATEMENT_NAME = auto()
    STATEMENT_BODY = auto()
    LOOP_BODY = auto()
    LOOP_EXECUTION = auto()
    CONDITION_BODY = auto()
    CONDITION_ALT = auto()
    VARIABLE_NAME = auto()
