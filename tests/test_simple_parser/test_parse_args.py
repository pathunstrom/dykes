from typing import NamedTuple

import simple_parser


def test_hyphenate_long_args():

    class Application(NamedTuple):
        dry_run: bool

    args = simple_parser.parse_args(Application, args=["--dry-run"])
    assert args.dry_run is True
