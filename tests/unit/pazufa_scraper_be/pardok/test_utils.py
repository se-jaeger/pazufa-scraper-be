from datetime import date
from typing import Any

import pytest
from pydantic import BaseModel

from pazufa_scraper_be.pardok.utils import ensure_list, ignore_invalid_factory, parse_german_date


@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("01.01.2020", date(2020, 1, 1)),
        ("31.12.2023", date(2023, 12, 31)),
        (date(2024, 5, 10), date(2024, 5, 10)),
    ],
)
def test_parse_german_date_success(input_val: str | date, expected: date):
    assert parse_german_date(input_val) == expected


def test_parse_german_date_failure():
    with pytest.raises(ValueError):
        parse_german_date("2020-01-01")
    with pytest.raises(ValueError):
        parse_german_date("invalid-date")


@pytest.mark.parametrize(
    "input_val, expected",
    [
        (["a", "b"], ["a", "b"]),
        ("a", ["a"]),
        (123, [123]),
        (None, [None]),
    ],
)
def test_ensure_list(input_val: Any, expected: list[Any]):
    assert ensure_list(input_val) == expected


class MockModel(BaseModel):
    name: str
    age: int


def test_ignore_invalid_factory():
    factory = ignore_invalid_factory(MockModel)

    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": "invalid"},  # Should be ignored
        {"name": "Charlie"},  # Should be ignored (missing age)
        {"name": "Dave", "age": 40},
    ]

    result = factory(data)

    assert len(result) == 2
    assert all(isinstance(item, MockModel) for item in result)
    assert result[0] == MockModel.model_validate(data[0])
    assert result[1] == MockModel.model_validate(data[3])
