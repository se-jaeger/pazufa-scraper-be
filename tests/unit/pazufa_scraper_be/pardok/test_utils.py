from datetime import UTC, date, datetime

import pytest
from pydantic import BaseModel

from pazufa_scraper_be.pardok.utils import ensure_list, ignore_invalid_factory, parse_german_date


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        ("01.01.2020", datetime(2020, 1, 1, tzinfo=UTC)),
        ("31.12.2023", datetime(2023, 12, 31, tzinfo=UTC)),
        (date(2024, 5, 10), datetime(2024, 5, 10, tzinfo=UTC)),
    ],
)
def test_parse_german_date_success(input_val: str | date, expected: date) -> None:
    """parse_german_date returns the correct date for valid inputs."""
    assert parse_german_date(input_val) == expected


def test_parse_german_date_failure() -> None:
    """parse_german_date raises ValueError for invalid date strings and TypeError for invalid types."""
    with pytest.raises(ValueError, match="does not match format"):
        parse_german_date("2020-01-01")
    with pytest.raises(ValueError, match="does not match format"):
        parse_german_date("invalid-date")
    with pytest.raises(TypeError, match="Can not parse given type"):
        parse_german_date(123)  # ty: ignore[invalid-argument-type]


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [
        (["a", "b"], ["a", "b"]),
        ("a", ["a"]),
        (123, [123]),
        (None, [None]),
    ],
)
def test_ensure_list(input_val: object, expected: list[object]) -> None:
    """ensure_list wraps non-list values and passes through lists unchanged."""
    assert ensure_list(input_val) == expected


class MockModel(BaseModel):
    """Minimal Pydantic model used in ignore_invalid_factory tests."""

    name: str
    age: int


def test_ignore_invalid_factory() -> None:
    """ignore_invalid_factory filters out invalid Pydantic model instances."""
    factory = ignore_invalid_factory(MockModel)

    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": "invalid"},  # Should be ignored
        {"name": "Charlie"},  # Should be ignored (missing age)
        {"name": "Dave", "age": 40},
    ]

    expected_count = 2
    result = factory(data)

    assert len(result) == expected_count
    assert all(isinstance(item, MockModel) for item in result)
    assert result[0] == MockModel.model_validate(data[0])
    assert result[1] == MockModel.model_validate(data[3])
