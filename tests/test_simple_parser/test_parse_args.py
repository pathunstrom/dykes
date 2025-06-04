import dataclasses
from typing import NamedTuple

import pytest

import dykes


def test_hyphenate_long_args():

    class Application(NamedTuple):
        dry_run: bool

    args = dykes.parse_args(Application, args=["--dry-run"])
    assert args.dry_run is True


def test_count_default_to_0():

    @dataclasses.dataclass
    class Application:
        verbosity: dykes.Count

    args = dykes.parse_args(Application, args=[])
    assert args.verbosity == 0


def test_positional_parameter_with_default_raises():
    @dataclasses.dataclass
    class Application:
        ruby: str = "red"

    with pytest.raises(ValueError) as err_info:
        parser = dykes.build_parser(Application)
    assert str(err_info.value) == "Positional arguments cannot have defaults."
