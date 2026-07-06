"""Все, что касается работы с данными и БД."""

import logging
from typing import Any

from sqlalchemy import select

from app.database import async_session_maker
from app.employees.models import Employee

ILIKE_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'phone_number',
]


async def get_all_employees(**filters: dict[str, Any]) -> list[Employee]:
    """Возвращает список работников с учетом фильтров."""
    logging.info(f'Filters received: {filters}')
    async with async_session_maker() as session:
        query = select(Employee)

        date_start = filters.pop('date_of_birth_start', None)
        date_end = filters.pop('date_of_birth_end', None)
        if date_start and date_end:
            query = query.filter(
                Employee.date_of_birth >= date_start,
                Employee.date_of_birth <= date_end,
            )

        for field in ILIKE_FIELDS:
            value = filters.pop(field, None)
            if value:
                value = str(value).strip()
                if value:
                    column = getattr(Employee, field)
                    query = query.filter(column.ilike(f'%{value}%'))

        if filters:
            query = query.filter_by(**filters)

        result = await session.execute(query)
        return result.scalars().all()
