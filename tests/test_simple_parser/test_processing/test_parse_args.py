import dataclasses
import pathlib
import typing
from enum import StrEnum, auto
from typing import NamedTuple, Annotated, Optional

import pytest

import dykes

# ruff: noqa: F841


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

    with pytest.raises(
        ExceptionGroup, match="Invalid positional arguments"
    ) as err_info:
        dykes.parse_args(Application)
    exceptions = err_info.value.exceptions
    assert (len(exceptions)) == 1
    exc = exceptions[0]
    assert (
        str(exc.args[0])
        == "Positional arguments cannot have defaults without NumberOfArguments '?' or '*'. dest='ruby'"
    )


@pytest.mark.parametrize(
    "inputs, expected",
    (
        (["foo.md"], [pathlib.Path("foo.md")]),
        (["foo.md", "bar.txt"], [pathlib.Path("foo.md"), pathlib.Path("bar.txt")]),
    ),
)
def test_nargs_positional_implicit(inputs, expected):
    from pathlib import Path

    @dataclasses.dataclass
    class Application:
        paths: list[Path]

    args = dykes.parse_args(Application, args=inputs)
    assert args.paths == expected


@pytest.mark.xfail(strict=True)
def test_nargs_positional_implicit_no_param_fails():
    from pathlib import Path

    @dataclasses.dataclass
    class Application:
        paths: list[Path]

    with pytest.raises(SystemExit):
        dykes.parse_args(Application, args=[])


def test_list_with_multiple_types_fails():
    @dataclasses.dataclass
    class Application:
        paths: list[str, float]

    with pytest.RaisesGroup(
        pytest.RaisesExc(
            ValueError,
            match="Argument parsing does not support lists with multiple types.",
        ),
    ):
        args = dykes.parse_args(Application)


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
        foo: Annotated[list[str], dykes.options.NArgs("*")] = dataclasses.field(
            default_factory=lambda: ["blue"]
        )

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


def test_multi_args():
    @dataclasses.dataclass
    class Application:
        foo: str
        bar: str

    app = dykes.parse_args(Application, args=["spam", "eggs"])
    assert app.foo == "spam"
    assert app.bar == "eggs"


@dataclasses.dataclass
class WordCounterArgs:
    """A simple word counter. Provide file name to count words."""

    path: typing.Annotated[pathlib.Path, "The path to the file to word count."]
    dry_run: bool
    verbosity: typing.Annotated[
        dykes.Count, "Verbosity of script. Provide up to 3 times."
    ]


@pytest.mark.parametrize(
    ("args_list", "expected"),
    [
        (["."], WordCounterArgs(pathlib.Path("."), False, 0)),
        ([".", "-v"], WordCounterArgs(pathlib.Path("."), False, 1)),
        ([".", "--dry-run"], WordCounterArgs(pathlib.Path("."), True, 0)),
        ([".", "-vvd"], WordCounterArgs(pathlib.Path("."), True, verbosity=2)),
    ],
)
def test_basic_example(args_list, expected):
    """
    This test should match examples/basic.py

    Before releases check WordCounterArgs versus the one in basic.py
    """
    args = dykes.parse_args(WordCounterArgs, args=args_list)
    assert args == expected


@dataclasses.dataclass
class ExampleApplication:
    """
    This is a sample script that operates on a file on disk.
    """

    path: Annotated[pathlib.Path, "The paths to operate on."]
    dry_run: bool
    prompt: dykes.StoreFalse
    verbosity: dykes.Count


@pytest.mark.parametrize(
    ("args_list", "expected"),
    [
        (["."], ExampleApplication(pathlib.Path("."), False, True, 0)),
        ([".", "-p"], ExampleApplication(pathlib.Path("."), False, False, 0)),
        ([".", "-dv"], ExampleApplication(pathlib.Path("."), True, True, 1)),
        (
            [".", "--prompt", "-d", "-vvv"],
            ExampleApplication(pathlib.Path("."), True, False, 3),
        ),
    ],
)
def test_example_application(args_list, expected):
    """
    This test should match examples/example_application.py

    Before releases check ExampleApplication versus the one in example_application.py
    """
    args = dykes.parse_args(ExampleApplication, args=args_list)
    assert args == expected


def test_default_values_reported():
    """
    https://github.com/pathunstrom/dykes/issues/18
    """

    @dataclasses.dataclass
    class Problem:
        default_list: Annotated[list[str], dykes.options.Flags("-d")] = (
            dataclasses.field(default_factory=list)
        )
        number: Annotated[int, dykes.options.Flags("-n")] = 0
        words: Annotated[str, dykes.options.Flags("-w")] = ""

    args = dykes.parse_args(Problem, args=[])

    assert args == Problem([])


def test_optional_and_union_none_are_optional_arguments():
    """
    https://github.com/pathunstrom/dykes/issues/18#issuecomment-3865641996
    """

    @dataclasses.dataclass
    class TestArgs:
        foo: Optional[str] = None

    dykes.parse_args(TestArgs, args=[])


def test_optional_and_union_none_are_optional_arguments_using_bitwise_or():
    """
    https://github.com/pathunstrom/dykes/issues/18#issuecomment-3865641996
    """

    @dataclasses.dataclass
    class TestArgs:
        foo: str | None = None

    dykes.parse_args(TestArgs, args=[])


def test_str_enum_optional():
    class Values(StrEnum):
        FIRST = auto()
        SECOND = auto()

    @dataclasses.dataclass
    class App:
        argument: Optional[Values]

    app = dykes.parse_args(App, args=["first"])

    assert app == App(Values.FIRST)


def test_str_enum_optional_bitwise_or():
    class Values(StrEnum):
        FIRST = auto()
        SECOND = auto()

    @dataclasses.dataclass
    class App:
        argument: Values | None

    app = dykes.parse_args(App, args=["second"])

    assert app == App(Values.FIRST)


@pytest.mark.parametrize(
    ("inputs", "expected"), [([], {"argument": None}), (["foo"], {"argument": "foo"})]
)
def test_explicit_union_with_none(inputs: list[str], expected: dict[str, str]):
    @dataclasses.dataclass
    class App:
        argument: typing.Union[str, None]

    app = dykes.parse_args(App, args=inputs)

    assert app == App(**expected)
