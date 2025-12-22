import dataclasses
import typing

import pytest

import dykes


def test_dataclass():
    @dataclasses.dataclass
    class Cmd:
        inner: dykes.StoreTrue

    @dataclasses.dataclass
    class Application:
        outer: dykes.StoreTrue
        cmd: dykes.Subparser[Cmd]

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner


def test_namedtuple():
    class Cmd(typing.NamedTuple):
        inner: dykes.StoreTrue

    class Application(typing.NamedTuple):
        outer: dykes.StoreTrue
        cmd: dykes.Subparser[Cmd]

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner


@pytest.mark.parametrize(
    "argv",
    (
        ([],),
        (["--help"],),
        (["cmd"],),
        (["--outer"],),
        (["cmd", "--inner"],),
        (["--outer", "cmd", "--inner"],),
        (["--outer", "cmd"],),
    ),
)
def test_parsing(argv):
    @dataclasses.dataclass
    class Cmd:
        inner: dykes.StoreTrue = False

    @dataclasses.dataclass
    class Application:
        outer: dykes.StoreTrue = False
        cmd: dykes.Subparser[Cmd] = None

    try:
        dykes.parse_args(Application, args=argv)
    except SystemExit as exc:
        assert exc.code == 0
