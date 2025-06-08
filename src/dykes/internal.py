import dataclasses
import typing

from dykes import options


class _Unset:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __bool__(self):
        return False


UNSET = _Unset()


@dataclasses.dataclass
class Field:
    name: str
    value: typing.Any


@typing.runtime_checkable
class NamedTupleProtocol(typing.Protocol):
    _fields: tuple[str]
    _field_defaults: dict[str, typing.Any]


@dataclasses.dataclass
class ParameterOptions[T]:
    dest: str | _Unset
    type: typing.Type[T] | typing.Callable[[], T] | UNSET
    flags: list[str] | _Unset = UNSET
    help: str | _Unset = UNSET
    action: options.Action | _Unset = UNSET
    default: T | _Unset = UNSET
    nargs: int | typing.Literal["?", "+", "*"] | _Unset = UNSET

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
