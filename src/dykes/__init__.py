import argparse
import dataclasses
import typing
from enum import StrEnum, auto
from inspect import getdoc
from sys import argv


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

NO_TYPE = Action.COUNT, Action.STORE_FALSE, Action.STORE_TRUE
MUST_BE_FLAG = Action.COUNT, Action.STORE_TRUE, Action.STORE_FALSE

@dataclasses.dataclass
class Field:
    name: str
    value: typing.Any


class _Unset:
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            cls._instance = super().__new__()
        return cls._instance

    def __bool__(self):
        return False


UNSET = _Unset()


@dataclasses.dataclass
class ParameterOptions[T]:
    dest: str | _Unset
    type: typing.Type[T] | typing.Callable[[], T] | UNSET
    flags: list[str] | _Unset = UNSET
    help: str | UNSET = UNSET
    action: Action | _Unset = UNSET
    default: T | _Unset = UNSET
    nargs: int | typing.Literal["?", "+", "*"] | _Unset = UNSET

    def as_dict(self) -> dict[str, typing.Any]:
        output = {key: value for key, value in dataclasses.asdict(self).items() if value is not UNSET}
        return output


def build_parser(application_definition: type) -> argparse.ArgumentParser:
    description = getdoc(application_definition)
    parser = argparse.ArgumentParser(description=description)
    hints = typing.get_type_hints(application_definition, include_extras=True)
    fields = _get_fields(application_definition)

    for dest, cls in hints.items():
        origin = get_origin(cls)
        options: ParameterOptions = ParameterOptions(
            dest=dest,
            type=get_field_type(cls),
            default=fields[dest].value if fields[dest].value else UNSET
        )

        options = get_meta_args(cls, options)

        if options.action is UNSET:
            if options.type is bool:
                if options.default is True:
                    options.action = Action.STORE_FALSE
                elif options.default in (False, UNSET):
                    options.action = Action.STORE_TRUE

        if options.action in NO_TYPE:
            options.type = UNSET

        if options.action in MUST_BE_FLAG and not options.flags:
            options.flags = [f"-{dest[0]}", f"--{dest.replace("_", "-")}"]

        if options.action is Action.COUNT:
            options.default = options.default if options.default else 0

        if origin is list and options.nargs is UNSET:
            options.nargs = "+"

        if options.flags is UNSET and options.default is not UNSET:
            raise ValueError("Positional arguments cannot have defaults.")
        arguments = options.as_dict()
        dest = arguments["dest"]
        flags = arguments.pop("flags", None)
        name_or_flags = flags if flags else [dest]
        if not flags:
            arguments.pop("dest")
        parser.add_argument(*name_or_flags, **arguments)
    return parser


type_map = {
    Action: "action",
    str: "help",
}


def is_instance_unique[T: (str, Action)](value: typing.Any, check_type: type[T], options: ParameterOptions) -> typing.TypeGuard[T]:
    if not isinstance(value, check_type):
        return False

    if getattr(options, type_map[check_type]) != UNSET:
        raise ValueError(f"Found multiple {check_type.__name__} in Annotated. Please use only one {check_type.__name__}")

    return True


def get_meta_args[FieldType](cls: type[FieldType], options: ParameterOptions) -> ParameterOptions[FieldType]:
    if (meta := getattr(cls, "__metadata__", None)) is not None:
        for datum in meta:
            if is_instance_unique(datum, Action, options):
                options.action = datum
            elif is_instance_unique(datum, str, options):
                options.help = datum

    return options


def get_field_type[T](cls: type[T] | list[type[T]]) -> type[T]:
    origin = get_origin(cls)
    if origin is list:
        type_args = typing.get_args(cls)
        if len(type_args) > 1:
            change_to = " or ".join(f"list[{t.__name__}]" for t in typing.get_args(cls))
            raise ValueError(
                f"dykes does not support lists with multiple type values. Convert {cls} to {change_to}"
            )
        elif len(type_args) == 0:
            return str
        else:
            return type_args[0]
    else:
        return cls


@typing.runtime_checkable
class _HasOrigin(typing.Protocol):
    @property
    def __origin__(self) -> type | None:
        return None


def get_origin(t: type) -> type:
    """
    Get true type from a hint.

    A version of typing.get_origin that exposed Annotated types to their root
    and also returns the input for un-subscripted types.
    """
    result = typing.get_origin(t)
    if result is None:
        return t
    elif result is typing.Annotated:
        if isinstance(t, _HasOrigin) and isinstance(
            t.__origin__, type
        ):  # Make mypy happy.
            return get_origin(t.__origin__)
        else:
            raise ValueError(
                "Annotated without a type or annotations. Please subscript Annotated."
            )
    return result


@typing.runtime_checkable
class _NamedTupleProtocol(typing.Protocol):
    _fields: tuple[str]
    _field_defaults: dict[str, typing.Any]


def _get_fields(cls: type) -> dict["str", Field]:
    fields = {}
    if dataclasses.is_dataclass(cls):
        fields = {
            field.name: Field(
                field.name,
                field.default if field.default is not dataclasses.MISSING else None,
            )
            for field in dataclasses.fields(cls)
        }

        return fields
    elif isinstance(cls, _NamedTupleProtocol):
        fields = {
            field: Field(field, cls._field_defaults.get(field)) for field in cls._fields
        }
    return fields
