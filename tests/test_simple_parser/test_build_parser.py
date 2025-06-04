import argparse
from dataclasses import dataclass
from typing import NamedTuple, Annotated

from pytest import mark

import simple_parser


@mark.parametrize(
    "docstring",
    [
        "This is a test",
        "An extra test with longer time.",
        "This one has a newline.\nSee, this is another line."
        "Does it suppress multiple new lines?\n\nMore text here."
    ]
)
def test_description_from_docstring(docstring):

    @dataclass
    class Application:
        foo: str

    Application.__doc__ = docstring
    # Can't use an f-string as a docstring, so we're faking it.

    result_parser = simple_parser.build_parser(Application)
    assert docstring == result_parser.description


def test_typed_actions():
    import pathlib

    @dataclass
    class Application:
        """
        A sample application with two simple positional parameters.
        """
        foo: str
        place: pathlib.Path

    result_parser = simple_parser.build_parser(Application)

    for action in result_parser._actions:
        assert action.dest in ("help", "foo", "place")
        if action.dest == "foo":
            assert action.type == str
        elif action.dest == "place":
            assert action.type == pathlib.Path


def test_with_store_true_implicit():

    class Application(NamedTuple):
        """
        A sample NamedTuple Application Definition
        """
        jessica: bool

    result_parser = simple_parser.build_parser(Application)

    for action in result_parser._actions:
        assert action.dest in ("help", "jessica")
        if action.dest == "jessica":
            assert isinstance(action, argparse._StoreTrueAction)
            assert action.default is False


def test_annotated_with_help():

    @dataclass
    class Application:
        """Application description"""
        param: Annotated[int, "This is the help text."]

    parser = simple_parser.build_parser(Application)

    action = [action for action in parser._actions if action.dest == "param"][0]
    assert action.help == "This is the help text."


def test_count_action():

    @dataclass
    class Application:
        """Application description"""
        verbosity: Annotated[simple_parser.Count, "Verbosity of script. Apply up to 3."]

    parser = simple_parser.build_parser(Application)
    action = [action for action in parser._actions if action.dest == "verbosity"][0]

    assert action.help == "Verbosity of script. Apply up to 3."
    assert type(action) is argparse._CountAction
