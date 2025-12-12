import dataclasses
import typing

import dykes


def test_dataclass():
    @dataclasses.dataclass
    class Application:
        outer: dykes.StoreTrue

        @dykes.subcommand
        class cmd:
            inner: dykes.StoreTrue

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner


def test_namedtuple():
    class Application(typing.NamedTuple):
        outer: dykes.StoreTrue

        @dykes.subcommand
        class cmd(typing.NamedTuple):
            inner: dykes.StoreTrue

    args = dykes.parse_args(Application, args=["--outer", "cmd", "--inner"])
    assert args.outer
    assert args.cmd is not None
    assert args.cmd.inner
