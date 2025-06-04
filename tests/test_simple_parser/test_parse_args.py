import dataclasses
from typing import NamedTuple

import simple_parser


def test_hyphenate_long_args():

    class Application(NamedTuple):
        dry_run: bool

    args = simple_parser.parse_args(Application, args=["--dry-run"])
    assert args.dry_run is True


def test_count_default_to_0():

    @dataclasses.dataclass
    class Application:
        verbosity: simple_parser.Count

    args = simple_parser.parse_args(Application, args=[])
    assert args.verbosity == 0
