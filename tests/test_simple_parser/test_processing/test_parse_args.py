import dataclasses
import pathlib
from typing import NamedTuple, Annotated

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
        parser = dykes.parse_args(Application)
    assert str(err_info.value) == "Positional arguments cannot have defaults without NumberOfArguments '?' or '*'."


@pytest.mark.parametrize(
    "inputs, expected",
    (
        (["foo.md"], [pathlib.Path("foo.md")]),
        (["foo.md", "bar.txt"], [pathlib.Path("foo.md"), pathlib.Path("bar.txt")])
    )
)
def test_nargs_positional_implicit(inputs, expected):
    from pathlib import Path

    @dataclasses.dataclass
    class Application:
        paths: list[Path]

    args = dykes.parse_args(Application, args=inputs)
    assert args.paths == expected


def test_nargs_positional_implicit_no_param_fails():
    from pathlib import Path

    @dataclasses.dataclass
    class Application:
        paths: list[Path]

    with pytest.raises(SystemExit):
        args = dykes.parse_args(Application, args=[])


def test_list_with_multiple_types_fails():
    @dataclasses.dataclass
    class Application:
        paths: list[str, float]

    with pytest.raises(ValueError) as ex_info:
        args = dykes.parse_args(Application)

    assert str(ex_info.value) == "dykes does not support lists with multiple type values. Convert list[str, float] to list[str] or list[float]"


def test_positional_parameter_with_default_proper_nargs_optional():

    @dataclasses.dataclass
    class Application:
        foo: Annotated[str, dykes.options.NArgs("?")] = "blue"

    app = dykes.parse_args(Application, args=[])
    assert app.foo == "blue"

    app = dykes.parse_args(Application, args=["red"])
    assert app.foo == "red"


def test_positional_parameter_with_default_proper_nargs_zero_or_many():

    @dataclasses.dataclass
    class Application:
        foo: Annotated[list[str], dykes.options.NArgs("*")] = dataclasses.field(default_factory=lambda: ["blue"])

    app = dykes.parse_args(Application, args=[])
    assert app.foo == ["blue"]

    app = dykes.parse_args(Application, args=["red"])
    assert app.foo == ["red"]


def test_option_explicit_store_makes_flag():
    @dataclasses.dataclass
    class Application:
        foo: Annotated[str, dykes.options.Action.STORE]

    app = dykes.parse_args(Application, args=[])
    assert app.foo is None

    app = dykes.parse_args(Application, args=["-f", "test"])
    assert app.foo == "test"
