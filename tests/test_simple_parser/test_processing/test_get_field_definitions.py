"""
Tests get_field_definitions

This module is going to be messy.

Classes need to be defined ahead of time to be used in parameterize,
planning to build multiple test cases.
"""

import pytest
from dataclasses import dataclass
from typing import NamedTuple

from dykes.internal import UNSET
from dykes.processing import get_field_definitions, FieldDefinition


class NamedTupleSimpleNoDefaults(NamedTuple):
    field: str
    another: int


@dataclass
class DataclassSimpleNoDefaults:
    field: str
    another: int


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
    ],
)
def test_get_field_definitions(struct: type, expected: list[FieldDefinition]):
    definitions = get_field_definitions(struct)
    assert definitions == expected
