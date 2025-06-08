"""
Argument Parser Options

Provided for public API use.
"""
import dataclasses
import typing
from enum import StrEnum, auto


class Action(StrEnum):
    """
    Actions for use with ArgumentParser.add_argument.

    See https://docs.python.org/3/library/argparse.html#action for what each does.

    Can be used directly:

        parser = argparse.ArgumentParser
        parser.add_argument("file_path", type=pathlib.Path, action=simple_parser.Action.STORE)
    """

    STORE = auto()
    STORE_CONST = auto()
    STORE_TRUE = auto()
    STORE_FALSE = auto()
    APPEND = auto()
    APPEND_CONST = auto()
    EXTEND = auto()
    COUNT = auto()
    HELP = auto()
    VERSION = auto()


Count = typing.Annotated[int, Action.COUNT]
StoreTrue = typing.Annotated[bool, Action.STORE_TRUE]
StoreFalse = typing.Annotated[bool, Action.STORE_FALSE]


@dataclasses.dataclass(frozen=True)
class NumberOfArguments:
    value: int | typing.Literal["*", "+", "?"]


class Flags:
    value: list[str]

    def __init__(self, *args: str):
        self.value = list(args)

    def __hash__(self):
        return hash(f"Flags[{",".join(self.value)}]")
