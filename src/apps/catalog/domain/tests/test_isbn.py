import pytest

from catalog.domain.exceptions import InvalidIsbn
from catalog.domain.types import Isbn


@pytest.mark.unit
@pytest.mark.parametrize(
    "raw",
    ["978-0-00-000000-1", "978 0 00 000000 1", " 9780000000001 "],
)
def test_isbn_13_spellings_clean_to_one_value(raw):
    assert Isbn.from_raw(raw) == Isbn(value="9780000000001")


@pytest.mark.unit
def test_isbn_10_may_end_in_x():
    assert Isbn.from_raw("0-00-000000-x").value == "000000000X"


@pytest.mark.unit
@pytest.mark.parametrize("raw", ["", "123", "97800000000AB", "X000000000"])
def test_malformed_isbn_is_refused(raw):
    with pytest.raises(InvalidIsbn):
        Isbn.from_raw(raw)
