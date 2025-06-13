from pathlib import Path
from typing import Annotated

import pytest

from dykes import utils


@pytest.mark.parametrize(
    "t",
    (str, int, list, float, Path)
)
def test_get_origin_plain_types(t):
    assert utils.get_origin(t) == t


@pytest.mark.parametrize(
    "t_in, expected_t",
    (
        (list[int], list),
        (dict[str, str], dict),
        (Annotated[int, ""], int),
        (Annotated[list[int], ""], list)
    )
)
def test_get_origin_subscripted(t_in, expected_t):
    assert utils.get_origin(t_in) == expected_t
