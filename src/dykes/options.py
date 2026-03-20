"""
Argument parser options.
--------------------------------------

All members of this module are exported to the :mod:`dykes` namespace, allowing
you to reference them as :class:`dykes.Action` instead of :class:`dykes.options.Action`

The basic method of applying an option to your type is via the
:class:`typing.Annotated` type. Dykes will only allow one copy of each type per
field. Dykes matches annotations by type and ignores annotations it does not
support.

Custom help strings can be provided to Annotated as string literals, they will
be displayed in the argparse generated help.
"""

import dataclasses
import typing
from enum import StrEnum, auto


class Action(StrEnum):
    """
    Actions for use with :func:`argparse.ArgumentParser.add_argument`.

    See https://docs.python.org/3/library/argparse.html#action for what each does.

    Can be used directly with argparse:

    .. code:: python

       parser = argparse.ArgumentParser
       parser.add_argument("file_path", type=pathlib.Path, action=simple_parser.Action.STORE)

    You can use an Action instance to tell dykes to change the default action for your option.

    .. code:: python

       @dataclass
       class Arguments:
           dry_run: Annotated[bool, Action.STORE_TRUE] = False

    .. hint::

       This sample is equivalent to using :class:`dykes.StoreTrue` and that should be preferred.
    """

    STORE = auto()  #:
    STORE_CONST = auto()  #:
    STORE_TRUE = auto()  #:
    STORE_FALSE = auto()  #:
    APPEND = auto()  #:
    APPEND_CONST = auto()  #:
    EXTEND = auto()  #:
    COUNT = auto()  #:
    HELP = auto()  #:
    VERSION = auto()  #:

    def __repr__(self):
        """
        Return Action.MEMBER so documentation looks nicer.
        """
        return f"Action.{self.value.upper()}"


Count = typing.Annotated[int, Action.COUNT]
StoreTrue = typing.Annotated[bool, Action.STORE_TRUE]
StoreFalse = typing.Annotated[bool, Action.STORE_FALSE]


@dataclasses.dataclass(frozen=True)
class NArgs:
    """
    Declare the number of arguments your option requires.

    Example:

    .. code:: python

       @dataclass
       class TakeMany:
           paths: Annotated[Path, NArgs('*')]
    """

    value: int | typing.Literal["*", "+", "?"]


class Flags:
    """
    Used to declare custom flag values for your command line option.

    By default, Dykes will convert any kind of optional parameter into a flag
    using the name of the parameter. This gives you finer control over what the
    flags should be.

    Use like:

    .. code:: python

       @dataclasses
       class CustomFlag:
           noisiness: typing.Annotated[dykes.Count, dykes.Flags("-v", "--verbose")]
    """

    value: list[str]

    def __init__(self, *args: str):
        self.value = list(args)

    def __hash__(self):
        return hash(f"Flags[{','.join(self.value)}]")

    def __eq__(self, other):
        return self.value == other.value and type(other) is Flags
