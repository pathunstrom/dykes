import argparse
import dataclasses
import typing
from enum import StrEnum, auto
from inspect import getdoc
from sys import argv
from typing import get_type_hints


@dataclasses.dataclass
class Flags:
    value: list[str]


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


def parse_args[ArgsType](
    parameter_definition: type[ArgsType], *, args: list | None = None
) -> ArgsType:
    """
    Your entry point.
    """
    if args is None:
        args = argv[1:]
    parser = build_parser(parameter_definition)
    parsed = parser.parse_args(args)
    return parameter_definition(**vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    hints = get_type_hints(application_definition, include_extras=True)
    for name, cls in hints.items():
        action = None
        flags = None
        configuration = {
            "help": None
        }
        if (meta := getattr(cls, "__metadata__", None)) is not None:
            for datum in meta:
                if isinstance(datum, Action) and action is not None:
                    raise ValueError(
                        "Multiple actions in annotations. Please use only one Action."
                    )
                elif isinstance(datum, Action):
                    action = datum
                elif isinstance(datum, str) and configuration["help"] is not None:
                    raise (
                        ValueError(
                            "Multiple bare strings in annotation. Please use only one bare string in Annotation."
                        )
                    )
                elif isinstance(datum, str):
                    configuration["help"] = datum
        if flags is None:
            flags = f"-{name[0]}", f"--{name.replace('_', '-')}"
        if cls is bool:
            parser.add_argument(*flags, dest=name, action=Action.STORE_TRUE, **configuration)
        elif action is Action.COUNT:
            parser.add_argument(*flags, dest=name, action=action, **configuration)
        else:
            parser.add_argument(name, type=cls, **configuration)
    return parser
