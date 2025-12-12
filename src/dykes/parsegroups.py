# This entire module is basically typing fiction
import dataclasses
import typing


class _Descriptor[T, P](typing.Protocol):
    @typing.overload
    def __get__(self, inst: P, owner: type[P] | None = None) -> T: ...

    @typing.overload
    def __get__(self, inst: None, owner: type[P]) -> type[T]: ...


def subcommand[T](cls: type[T]) -> _Descriptor[T | None]:
    if cls.__bases__ == (object,):
        cls = dataclasses.dataclass(cls)
    return cls
