import pytest

from src.ph_toolbox.utils import slugify


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("  ", ""),
        (" 1234567890 ?!@#$%^&*()_=+ ", "1234567890"),
        ("Test Title", "test-title"),
        ("1 Test 2TiTlE?", "1-test-2title"),
    ],
)
def test_slugify(test_input, expected):
    assert slugify(test_input) == expected
