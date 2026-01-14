from pathlib import Path
from typing import Annotated, Union, Optional

import pytest

from dykes import utils


@pytest.mark.parametrize("t", (str, int, list, float, Path))
def test_get_origin_plain_types(t):
    assert utils.get_origin_type(t) == t


@pytest.mark.parametrize(
    "t_in, expected_t",
    (
        (list[int], list),
        (dict[str, str], dict),
        (Annotated[int, ""], int),
        (Annotated[list[int], ""], list),
    ),
)
def test_get_origin_subscripted(t_in, expected_t):
    assert utils.get_origin_type(t_in) == expected_t


@pytest.mark.parametrize(
    "t_in, e_origin, e_inner",
    (
        (list[int], list, int),
        (str | None, str, str),
        (Union[str, None], str, str),
        (Optional[str], str, str),
        (list[str] | None, list, str),
        (list[str | None], list, str),
        (Annotated[str | None, ""], str, str),
        (Annotated[list[str] | None, ""], list, str),
        (Annotated[list[str | None], ""], list, str),
    ),
)
def test_inners(t_in, e_origin, e_inner):
    origin = utils.get_origin_type(t_in)
    innermost = utils.get_inner_type(t_in)
    assert origin == e_origin
    assert innermost == e_inner
