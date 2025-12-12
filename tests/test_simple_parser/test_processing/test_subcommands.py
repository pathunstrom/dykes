import dataclasses

import dykes


def test_basic():
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
