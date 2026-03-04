import dataclasses
import typing

from . import options


class Sentinel:
    _instance: typing.ClassVar[typing.Self | None] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class UnsetType(Sentinel):
    pass


class UnsupportedType(Sentinel):
    pass


UNSET = UnsetType()
UNSUPPORTED = UnsupportedType()


@dataclasses.dataclass
class Field[T]:
    name: str
    value: T


@typing.runtime_checkable
class NamedTupleProtocol(typing.Protocol):
    _fields: tuple[str]
    _field_defaults: dict[str, typing.Any]


def is_named_tuple(obj: typing.Any) -> typing.TypeGuard[NamedTupleProtocol]:
    return isinstance(obj, NamedTupleProtocol)


@dataclasses.dataclass
class ParameterOptions[T]:
    dest: str | UnsetType
    type: type[T] | typing.Callable[[str], T] | UnsetType
    flags: list[str] | UnsetType = UNSET
    help: str | UnsetType = UNSET
    action: options.Action | UnsetType = UNSET
    default: T | UnsetType = UNSET
    nargs: int | typing.Literal["?", "+", "*"] | UnsetType = UNSET

    def as_dict(self) -> dict[str, typing.Any]:
        output = {
            key: value
            for key, value in dataclasses.asdict(self).items()
            if value is not UNSET
        }
        return output


@typing.runtime_checkable
class HasOrigin(typing.Protocol):
    @property
    def __origin__(self) -> type | None:
        return None
