"""
Tests get_field_definitions

This module is going to be messy.

Classes need to be defined ahead of time to be used in parameterize,
planning to build multiple test cases.
"""

import typing

import pytest
from dataclasses import dataclass
from typing import NamedTuple

import dykes.options
from dykes.internal import UNSET
from dykes.processing import get_field_definitions, FieldDefinition


class NamedTupleSimpleNoDefaults(NamedTuple):
    field: str
    another: int


@dataclass
class DataclassSimpleNoDefaults:
    field: str
    another: int


@dataclass
class DataclassAnnotated:
    field: typing.Annotated[int, dykes.options.Flags("-g", "--generate")]


@pytest.mark.parametrize(
    ("struct", "expected"),
    [
        (
            NamedTupleSimpleNoDefaults,
            [
                FieldDefinition("field", str, UNSET),
                FieldDefinition("another", int, UNSET),
            ],
        ),
        (
            DataclassSimpleNoDefaults,
            [
                FieldDefinition("field", str, UNSET),
                FieldDefinition("another", int, UNSET),
            ],
        ),
        (
            DataclassAnnotated,
            [
                FieldDefinition(
                    "field",
                    typing.Annotated[int, dykes.options.Flags("-g", "--generate")],
                    UNSET,
                )
            ],
        ),
    ],
)
def test_get_field_definitions(struct: type, expected: list[FieldDefinition]):
    definitions = get_field_definitions(struct)
    assert definitions == expected
