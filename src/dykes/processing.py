"""
The dykes plumbing module.

This is all the things used internally to turn your definitions into something useful.
"""
import argparse
import dataclasses
import typing
from inspect import getdoc
from sys import argv

from dykes import options, internal, utils

NO_TYPE = options.Action.COUNT, options.Action.STORE_FALSE, options.Action.STORE_TRUE
MUST_BE_FLAG = options.Action.COUNT, options.Action.STORE_TRUE, options.Action.STORE_FALSE


def parse_args[ArgsType](
    parameter_definition: type[ArgsType], *, args: list | None = None
) -> ArgsType:
    """
    Process arguments and conform them to an input type.

    Supports dataclasses and NamedTuples.

    Sample use:

        from dataclasses import dataclass
        from pathlib import Path

        from dykes import parse_args, Count

        @dataclass
        class Application:
            input: Path
            dry_run: bool
            verbosity: dykes.Count

        args = parse_args(Application)
        print(args)
    """
    if args is None:
        args = argv[1:]
    parser = build_parser(parameter_definition)
    parsed = parser.parse_args(args)
    return parameter_definition(**vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    hints = typing.get_type_hints(application_definition, include_extras=True)
    fields = _get_fields(application_definition)

    for dest, cls in hints.items():
        origin = utils.get_origin(cls)
        parameter_options: internal.ParameterOptions = internal.ParameterOptions(
            dest=dest,
            type=utils.get_field_type(cls),
            default=fields[dest].value if fields[dest].value else internal.UNSET
        )

        parameter_options = utils.get_meta_args(cls, parameter_options)

        if parameter_options.action is internal.UNSET:
            if parameter_options.type is bool:
                if parameter_options.default is True:
                    parameter_options.action = options.Action.STORE_FALSE
                elif parameter_options.default in (False, internal.UNSET):
                    parameter_options.action = options.Action.STORE_TRUE

        if parameter_options.action in NO_TYPE:
            parameter_options.type = internal.UNSET

        if parameter_options.action in MUST_BE_FLAG and not parameter_options.flags:
            parameter_options.flags = [f"-{dest[0]}", f"--{dest.replace("_", "-")}"]

        if parameter_options.action is options.Action.COUNT:
            parameter_options.default = parameter_options.default if parameter_options.default else 0

        if origin is list and parameter_options.nargs is internal.UNSET:
            parameter_options.nargs = "+"

        if parameter_options.flags is internal.UNSET and parameter_options.default is not internal.UNSET:
            raise ValueError("Positional arguments cannot have defaults.")
        arguments = parameter_options.as_dict()
        dest = arguments["dest"]
        flags = arguments.pop("flags", None)
        name_or_flags = flags if flags else [dest]
        if not flags:
            arguments.pop("dest")
        parser.add_argument(*name_or_flags, **arguments)
    return parser


def _get_fields(cls: type) -> dict["str", internal.Field]:
    fields = {}
    if dataclasses.is_dataclass(cls):
        fields = {
            field.name: internal.Field(
                field.name,
                field.default if field.default is not dataclasses.MISSING else None,
            )
            for field in dataclasses.fields(cls)
        }

        return fields
    elif isinstance(cls, internal.NamedTupleProtocol):
        fields = {
            field: internal.Field(field, cls._field_defaults.get(field)) for field in cls._fields
        }
    return fields
