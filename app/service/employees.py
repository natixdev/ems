"""Вся бизнес-логика."""

from datetime import date
from typing import Any

from app.repository.employees import (
    get_all_employees,
)


async def employee_list(**filters: dict[str, Any]) -> list:
    """Обрабатывает фильтры перед передачей в репозиторий.

    Преобразует возраст (age) в диапазон дат рождения.
    """
    age = filters.pop('age', None)
    if age is not None:
        today = date.today()
        year = today.year - age
        filters['date_of_birth_start'] = date(year, 1, 1)
        filters['date_of_birth_end'] = date(year, 12, 31)
    return await get_all_employees(**filters)
