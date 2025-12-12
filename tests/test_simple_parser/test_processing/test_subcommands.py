import dataclasses
import typing

import dykes


def test_dataclass():
    @dataclasses.dataclass
    class Cmd:
        inner: dykes.StoreTrue

    @dataclasses.dataclass
    class Application:
        outer: dykes.StoreTrue
        cmd: typing.Annotated[Cmd, dykes.Subparser]

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner


def test_namedtuple():
    class Cmd(typing.NamedTuple):
        inner: dykes.StoreTrue

    class Application(typing.NamedTuple):
        outer: dykes.StoreTrue
        cmd: typing.Annotated[Cmd, dykes.Subparser]

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner
