"""
The dykes plumbing module.

This is all the things used internally to turn your definitions into something useful.
"""

import argparse
import dataclasses
import types
import typing
from inspect import getdoc
from sys import argv

from . import options, internal, utils

NO_TYPE = options.Action.COUNT, options.Action.STORE_FALSE, options.Action.STORE_TRUE
MUST_BE_FLAG = (
    options.Action.COUNT,
    options.Action.STORE_TRUE,
    options.Action.STORE_FALSE,
)


def parse_args[ArgsType](
    application_struct: type[ArgsType],
    *,
    args: list | None = None,
    development_mode: bool = False,
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

    You can provide arguments just like parser.parse_args by supplying args=[...]

    Example:

        args = parse_args(Application, args=["some", "arguments"]

    Activate development mode with `development_mode=True`:

    Example:

        args = parse_args(Application, development_mode=True)

    Some error messages will change in development mode.
    """
    if args is None:
        args = argv[1:]
    parser = build_parser(application_struct)
    parsed = parser.parse_args(args)
    return application_struct(**vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    exceptions = []
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    hints = typing.get_type_hints(application_definition, include_extras=True)
    fields = _get_fields(application_definition)
    for dest, cls in hints.items():
        origin = utils.get_origin(cls)
        parameter_options: internal.ParameterOptions = internal.ParameterOptions(
            dest=dest,
            type=utils.get_field_type(cls),
            default=fields[dest].value,
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

        store_flag_unset = (
            parameter_options.action is options.Action.STORE
            and parameter_options.flags is internal.UNSET
        )
        # If explicit Store action, we assume it's a flag.
        must_be_flag_unset = (
            parameter_options.action in MUST_BE_FLAG and not parameter_options.flags
        )
        if store_flag_unset or must_be_flag_unset:
            parameter_options.flags = [f"-{dest[0]}", f"--{dest.replace('_', '-')}"]

        if parameter_options.action is options.Action.COUNT:
            parameter_options.default = (
                parameter_options.default if parameter_options.default else 0
            )

        if origin is list and parameter_options.nargs is internal.UNSET:
            parameter_options.nargs = "+"

        flag_unset = parameter_options.flags is internal.UNSET
        default_set = parameter_options.default is not internal.UNSET
        nargs_not_default_friendly = parameter_options.nargs not in ("?", "*")
        if default_set and flag_unset and nargs_not_default_friendly:
            exceptions.append(
                ValueError(
                    f"Positional arguments cannot have defaults without NumberOfArguments '?' or '*'. {dest=}"
                )
            )
            continue
        arguments = parameter_options.as_dict()
        dest = arguments["dest"]
        flags = arguments.pop("flags", None)
        name_or_flags = flags if flags else [dest]
        if not flags:
            arguments.pop("dest")
        parser.add_argument(*name_or_flags, **arguments)
    if exceptions:
        raise ExceptionGroup("Invalid positional arguments", exceptions)
    return parser


class _Field(typing.Protocol):
    default: typing.Any
    default_factory: typing.Callable[[], typing.Any]


def _get_default(data_class_field: _Field):
    if data_class_field.default is not dataclasses.MISSING:
        return data_class_field.default
    elif data_class_field.default_factory is not dataclasses.MISSING:
        return data_class_field.default_factory()
    else:
        return internal.UNSET


def _get_fields(cls: type) -> dict["str", internal.Field]:
    fields = {}
    if dataclasses.is_dataclass(cls):
        fields = {
            field.name: internal.Field(
                field.name, _get_default(typing.cast(_Field, field))
            )
            for field in dataclasses.fields(cls)
        }
    elif isinstance(cls, internal.NamedTupleProtocol):
        fields = {
            field: internal.Field(field, cls._field_defaults.get(field, internal.UNSET))
            for field in cls._fields
        }
    else:
        raise ValueError(
            f"{cls.__name__} is not a supported class type. Please use a dataclass or NamedTuple."
        )
    return fields


@dataclasses.dataclass
class FieldDefinition[T]:
    name: str  # Destination
    type_def: type[T]  # The type hint of the field.
    default_value: (
        T | internal._Unset
    )  # A default value. If there is a factory, an instance of the return.


def is_optional(type_def: type) -> bool:
    """
    Checks if type is Optional or a Union against None.
    """
    origin = typing.get_origin(type_def)
    args = typing.get_args(type_def)
    if origin == typing.Annotated:
        annotated = typing.get_args(type_def)[0]
        origin = typing.get_origin(annotated)
        args = typing.get_args(annotated)
    if origin == typing.Union or origin == types.UnionType:
        return len(args) == 2 and type(None) in args
    return False


def _get_definitions_dataclass(
    struct: typing.Any,
) -> list[FieldDefinition] | type[NotImplemented]:
    """
    Generate field definitions if the struct is a dataclass.

    Uses `dataclasses.is_dataclass` to determine membership.
    """

    if not dataclasses.is_dataclass(struct):
        return NotImplemented

    def get_default(field: dataclasses.Field) -> typing.Any | internal._Unset:
        if field.default is not dataclasses.MISSING:
            return field.default
        elif field.default_factory is not dataclasses.MISSING:
            return field.default_factory()
        else:
            return internal.UNSET

    return [
        FieldDefinition(
            name=field.name, type_def=field.type, default_value=get_default(field)
        )
        for field in dataclasses.fields(struct)
    ]


def _get_definitions_named_tuple(
    struct: typing.Any,
) -> list[FieldDefinition] | type[NotImplemented]:
    """
    Generate field definitions if the struct looks like a NamedTuple.

    Uses a protocol. The important parts:

    * `_fields` member list of strings.
    * `_fields_defaults` member, mapping of strings to values.
    * fields have type hints (and can be retrieved via `typing.get_type_hints`)
    """

    if not internal.is_named_tuple(struct):
        return NotImplemented

    defaults = struct._field_defaults
    hints = typing.get_type_hints(struct, include_extras=True)
    return [
        FieldDefinition(
            name=field,
            type_def=hints[field],
            default_value=defaults.get(field, internal.UNSET),
        )
        for field in struct._fields
    ]


def get_field_definitions(app_definition: typing.Any) -> list[FieldDefinition]:
    """
    Produce a list of fields for generating an argument parser.

    Will eventually have a pluggable interface to support struct libraries
    outside the standard library.
    """
    _get_definitions_list = [_get_definitions_dataclass, _get_definitions_named_tuple]
    errors = []
    for _get_definitions in _get_definitions_list:
        try:
            maybe_definitions = _get_definitions(app_definition)
            if maybe_definitions is NotImplemented:
                continue
            return maybe_definitions
        except Exception as err:
            errors.append(err)
    if errors:
        raise ValueError("Struct type not supported.") from ExceptionGroup(
            "Errors raised during field extraction.", errors
        )
    raise ValueError(
        "Struct type not supported. Consider using typing.NamedTuple or dataclasses.dataclass."
    )
