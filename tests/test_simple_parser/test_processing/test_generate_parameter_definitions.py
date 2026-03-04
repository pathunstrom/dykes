"""
Test conversion from FieldDefinitions to ParameterOptions
"""

import typing

import pytest

import dykes
from dykes.internal import ParameterOptions, UNSET
from dykes.processing import FieldDefinition, generate_parameter_definitions


@pytest.mark.parametrize(
    ("field_definitions", "expected"),
    [
        # The most basic argument parser.
        (
            [FieldDefinition("parameter", str, UNSET)],
            [ParameterOptions(dest="parameter", type=str)],
        ),
        # A field that is optional using bitwise or
        (
            [FieldDefinition("optional", str | None, UNSET)],
            [
                ParameterOptions(
                    dest="optional",
                    type=str,
                    nargs="?",
                    flags=["-o", "--optional"],
                    default=None,
                )
            ],
        ),
        # A field that is optional using typing.Union
        (
            [FieldDefinition("optional", typing.Union[str, None], UNSET)],
            [
                ParameterOptions(
                    dest="optional",
                    type=str,
                    nargs="?",
                    flags=["-o", "--optional"],
                    default=None,
                )
            ],
        ),
        # A field that is optional using typing.Optional
        (
            [FieldDefinition("optional", typing.Optional[str], UNSET)],
            [
                ParameterOptions(
                    dest="optional",
                    type=str,
                    nargs="?",
                    flags=["-o", "--optional"],
                    default=None,
                )
            ],
        ),
        # A list with an explicit type should use append by default
        (
            [FieldDefinition("collection", list[str], UNSET)],
            [
                ParameterOptions(
                    dest="collection",
                    type=str,
                    nargs="*",
                    flags=UNSET,
                    default=UNSET,
                )
            ],
        ),
        # A list with no type should default to string
        (
            [FieldDefinition("collection", list, UNSET)],
            [
                ParameterOptions(
                    dest="collection",
                    type=str,
                    nargs="*",
                    default=UNSET,
                )
            ],
        ),
        # Annotated with options should do the thing.
        (
            [
                FieldDefinition(
                    "annotated",
                    typing.Annotated[
                        int,
                        "This is a test doc.",
                        dykes.options.Flags("-i"),
                    ],
                    UNSET,
                )
            ],
            [
                ParameterOptions(
                    dest="annotated", type=int, help="This is a test doc.", flags=["-i"]
                )
            ],
        ),
        (
            [
                FieldDefinition(
                    "boolean",
                    bool,
                    UNSET,
                )
            ],
            [
                ParameterOptions(
                    dest="boolean",
                    type=bool,
                    flags=["-b", "--boolean"],
                    action=dykes.Action.STORE_TRUE,
                )
            ],
        ),
        (
            [
                FieldDefinition(
                    "boolean",
                    bool,
                    True,
                )
            ],
            [
                ParameterOptions(
                    dest="boolean",
                    type=bool,
                    flags=["-b", "--boolean"],
                    action=dykes.Action.STORE_FALSE,
                    default=True,
                )
            ],
        ),
    ],
)
def test_generate_parameter_definition(
    field_definitions: list[FieldDefinition], expected: list[ParameterOptions]
):
    parameter_definitions = generate_parameter_definitions(field_definitions)
    assert parameter_definitions == expected
