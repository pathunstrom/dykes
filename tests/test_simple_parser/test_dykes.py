import pytest

import dykes


@pytest.mark.black_box
def test_public_interface():
    """
    This test is just to catch changes to the public API.
    """
    assert dykes.options
    assert dykes.parse_args
    assert dykes.build_parser
    assert dykes.Action
    assert dykes.Count
    assert dykes.Flags
    assert dykes.NArgs
    assert dykes.StoreFalse
    assert dykes.StoreTrue
