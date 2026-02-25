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

from . import options, internal

NO_TYPE = options.Action.COUNT, options.Action.STORE_FALSE, options.Action.STORE_TRUE
MUST_BE_FLAG = (
    options.Action.COUNT,
    options.Action.STORE_TRUE,
    options.Action.STORE_FALSE,
)

SET_FLAG_DEFAULT = (
    options.Action.COUNT,
    options.Action.STORE_TRUE,
    options.Action.STORE_FALSE,
    options.Action.STORE,
)


dev_mode = False


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

        args = parse_args(Application, args=["some", "arguments"])

    Activate development mode with `development_mode=True`:

    Example:

        args = parse_args(Application, development_mode=True)

    Some error messages will change in development mode.
    """
    if development_mode:
        global dev_mode
        dev_mode = True
    if args is None:
        args = argv[1:]
    parser = build_parser(application_struct)
    parsed = parser.parse_args(args)
    return application_struct(**vars(parsed))


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    exceptions = []
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    fields = get_field_definitions(application_definition)
    parameters = generate_parameter_definitions(fields)
    for parameter in parameters:
        flag_unset = parameter.flags is internal.UNSET
        default_set = parameter.default is not internal.UNSET
        nargs_not_default_friendly = parameter.nargs not in ("?", "*")
        if default_set and flag_unset and nargs_not_default_friendly:
            exceptions.append(
                ValueError(
                    f"Positional arguments cannot have defaults without NumberOfArguments '?' or '*'. dest={parameter.dest!r}"
                )
            )
            continue

        arguments = parameter.as_dict()

        if parameter.action in NO_TYPE:
            arguments.pop("type")

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

    rv: list[FieldDefinition] = []
    type_hints = typing.get_type_hints(struct, include_extras=True)
    # dataclasses.fields doesn't reify type hints, the rest of the system
    # expects a reified type. We're going to stitch together
    # typing.get_type_hints with fields. Which is painful to make work in a
    # list comprehension, so we're just for looping.

    for field in dataclasses.fields(struct):
        name = field.name
        reified_type = type_hints[name]
        default_value = get_default(field)
        rv.append(
            FieldDefinition(
                name=name, type_def=reified_type, default_value=default_value
            )
        )
    return rv


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
            return typing.cast(list[FieldDefinition], maybe_definitions)
        except Exception as err:
            errors.append(err)
    if errors:
        raise ValueError("Struct type not supported.") from ExceptionGroup(
            "Errors raised during field extraction.", errors
        )
    raise ValueError(
        "Struct type not supported. Consider using typing.NamedTuple or dataclasses.dataclass."
    )


class TypeMeta(typing.NamedTuple):
    real_type: type
    is_optional: bool
    is_list: bool
    options: dict[type, typing.Any]


def get_metadata(type_def: type, field_name: str) -> TypeMeta:
    real_type = type_def
    is_optional = False
    is_list = False
    parse_options = {}

    # Unroll Annotated
    origin = typing.get_origin(real_type)
    if origin == typing.Annotated:
        args = typing.get_args(real_type)
        real_type = args[0]
        for annotation in args[1:]:
            key = type(annotation)
            if key in parse_options:
                raise ValueError(
                    f"Found duplicate annotated options. Check {field_name} for duplicated options."
                )
            parse_options[key] = annotation

    # Unroll Optional
    origin = typing.get_origin(real_type)
    if origin == types.UnionType or origin == typing.Union:
        args = typing.get_args(real_type)
        if len(args) != 2 or types.NoneType not in args:
            raise ValueError(
                f"Dykes argument parsing cannot support complex unions. Check {field_name}'s type hint."
            )
        else:
            stripped_none = list(args)
            stripped_none.remove(types.NoneType)
            real_type = stripped_none[0]
            is_optional = True

    # Unroll collections
    origin = typing.get_origin(real_type)
    if origin in (dict, set, tuple):
        raise ValueError(
            f"Argument parsing does not support {origin.__name__}. Check {field_name}'s type hint. Consider using `list`"
        )
    elif origin is list:
        args = typing.get_args(real_type)
        if len(args) > 1:
            raise ValueError(
                f"Argument parsing does not support lists with multiple types. Check {field_name}'s type hint. Limit your list to a single type."
            )
        real_type = args[0]
        is_list = True

    # Special cases
    if real_type in (dict, set, tuple):
        raise ValueError(
            f"Dykes argument parsing does not support {real_type.__name__}. Check {field_name}'s type hint."
        )
    elif real_type is list:
        real_type = str
        is_list = True

    return TypeMeta(
        real_type,
        is_optional,
        is_list,
        parse_options,
    )


def generate_parameter_definitions(
    field_definitions: list[FieldDefinition],
) -> list[internal.ParameterOptions]:
    """
    Turn an iterable of `FieldDefinitions` into a list of `ParameterOptions`

    This function is gnarly and is basically _the place_ we catch all the weird
    edge cases we care about. Things like what to do if the user declares a bool
    or list.

    Organized into sections (look for comments) based on the order of the
    parameters to ParameterOptions. Don't worry if incompatible fields for an
    action are set. Handling the API barrier between ParameterOptions and
    argparse live in the `build_parser` function.
    """
    exceptions = []
    parameters_options: list[internal.ParameterOptions] = []

    for field_definition in field_definitions:
        param_dest = field_definition.name

        # Handle type
        try:
            param_type, is_optional, is_list, annotations_dict = get_metadata(
                field_definition.type_def, param_dest
            )
        except Exception as err:
            exceptions.append(err)
            continue
        # Handle action
        param_action: options.Action | internal._Unset = internal.UNSET

        if is_list:
            param_action = options.Action.EXTEND
        elif param_type is bool and field_definition.default_value is True:
            param_action = options.Action.STORE_FALSE
        elif param_type is bool:
            param_action = options.Action.STORE_TRUE

        param_action = annotations_dict.get(options.Action, param_action)

        # Handle flags
        param_flags: list[str] | internal._Unset = internal.UNSET
        if param_action in SET_FLAG_DEFAULT or is_optional:
            param_flags = [f"-{param_dest[0]}", f"--{param_dest.replace('_', '-')}"]

        declared_flags: options.Flags | None = annotations_dict.get(options.Flags, None)
        if declared_flags is not None:
            param_flags = declared_flags.value

        # Handle help
        param_help: str | internal._Unset = internal.UNSET
        declared_help: str | None = annotations_dict.get(str, None)
        if declared_help is not None:
            param_help = declared_help

        # Handle default
        param_default: typing.Any = internal.UNSET
        if is_optional:
            param_default = None
        elif param_action is options.Action.COUNT:
            param_default = 0

        if field_definition.default_value is not internal.UNSET:
            param_default = field_definition.default_value

        # Handle nargs
        param_nargs: int | typing.Literal["*", "?", "+"] | internal._Unset = (
            internal.UNSET
        )
        if is_optional:
            param_nargs = "?"
        elif is_list:
            param_nargs = "*"
        declared_nargs: options.NArgs = annotations_dict.get(
            options.NArgs, internal.UNSET
        )
        if declared_nargs is not internal.UNSET:
            param_nargs = declared_nargs.value

        parameters_options.append(
            internal.ParameterOptions(
                dest=param_dest,
                type=param_type,
                flags=param_flags,
                help=param_help,
                action=param_action,
                default=param_default,
                nargs=param_nargs,
            )
        )
    if exceptions:
        raise ExceptionGroup(
            "Could not generate parameters. See included exceptions.", exceptions
        )
    return parameters_options
