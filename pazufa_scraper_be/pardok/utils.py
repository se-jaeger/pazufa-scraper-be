import logging
from collections.abc import Callable
from datetime import date, datetime
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ValidationError

logger = logging.getLogger(__name__)


def parse_german_date(date_or_str: date | str) -> date:
    if isinstance(date_or_str, date):
        return date_or_str

    return datetime.strptime(date_or_str, "%d.%m.%Y").date()


def ensure_list(value: Any | list) -> list:
    return value if isinstance(value, list) else [value]


def ignore_invalid_factory(cls: type[BaseModel]) -> Callable[..., list]:
    def return_function(items: list[Any]) -> list[type[BaseModel]]:
        result = []
        for item in items:
            try:
                result.append(cls.model_validate(item))

            except ValidationError:
                msg = f"Ignoring invalid {cls.__name__}: {item}"
                logger.warning(msg)

        return result

    return return_function


GermanDate = Annotated[date, BeforeValidator(parse_german_date)]
CoercedStrList = Annotated[list[str], BeforeValidator(ensure_list)]
