"""Вся бизнес-логика."""

from datetime import date
from typing import Any

from fastapi import HTTPException

from app.database import async_session_maker
from app.employees.models import Employee
from app.repository.employees import (
    add_employee,
    find_employee_by_id,
    get_all_employees,
    is_employee_exist,
    update_employee,
)
from app.repository.employees import delete_employee as delete_employee_by_id


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
    async with async_session_maker() as session:
        return await get_all_employees(session, **filters)


async def employee_detail(employee_id: int) -> Employee | None:
    """Запрашивает в БД работника по id."""
    async with async_session_maker() as session:
        return await find_employee_by_id(session, employee_id)


async def create_employee(**employee: dict) -> Employee:
    """Добавляет нового работника."""
    async with async_session_maker() as session:
        if await is_employee_exist(
            session, employee['email'], employee['phone_number'],
        ):
            raise HTTPException(
                status_code=400,
                detail='Работник с таким email и/или номером телефона'
                ' существует',
            )
        return await add_employee(session, employee)


async def patch_employee(
    employee_id: int,
    **employee_data: dict,
) -> Employee | None:
    """Обновляет конкретного работника.

    Если работник не найден -- выбрасывает ошибку 404.
    """
    async with async_session_maker() as session:
        employee = await find_employee_by_id(session, employee_id)
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден',
            )
        return await update_employee(
            session, employee_id, **employee_data,
        )


async def delete_employee(employee_id: int) -> dict:
    """Запрашивает в БД работника по id."""
    async with async_session_maker() as session:
        employee = await find_employee_by_id(session, employee_id)
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден',
            )
        return await delete_employee_by_id(session, employee_id)
