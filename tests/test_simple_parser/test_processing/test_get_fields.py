import pytest

from dykes.processing import _get_fields
from dykes.internal import UNSET


@pytest.mark.white_box
def test_unrecognized_class_raises():
    class Args:
        field: str

    with pytest.raises(ValueError) as ex_info:
        fields = _get_fields(Args)  # noqa: F841

    assert str(ex_info.value).startswith("Args is not a supported class type.")


@pytest.mark.white_box
def test_get_fields_from_namedtuple():
    from typing import NamedTuple

    class Args(NamedTuple):
        number: int
        flag: bool = True

    fields = _get_fields(Args)

    number_field = fields["number"]
    assert number_field.name == "number"
    assert number_field.value is UNSET

    flag_field = fields["flag"]
    assert flag_field.name == "flag"
    assert flag_field.value is True


@pytest.mark.white_box
def test_get_fields_from_namedtuple_with_optional_none_default():
    from typing import NamedTuple

    class Args(NamedTuple):
        number: int
        optional: int | None = None
        flag: bool = True

    fields = _get_fields(Args)

    number_field = fields["number"]
    assert number_field.name == "number"
    assert number_field.value is UNSET

    flag_field = fields["flag"]
    assert flag_field.name == "flag"
    assert flag_field.value is True

    optional_field = fields["optional"]
    assert optional_field.name == "optional"
    assert optional_field.value is None


@pytest.mark.white_box
def test_get_fields_from_dataclass():
    from dataclasses import dataclass

    @dataclass
    class Args:
        number: int
        flag: bool = True

    fields = _get_fields(Args)

    number_field = fields["number"]
    assert number_field.name == "number"
    assert number_field.value is UNSET

    flag_field = fields["flag"]
    assert flag_field.name == "flag"
    assert flag_field.value is True
