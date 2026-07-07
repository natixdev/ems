"""Вся бизнес-логика."""


from fastapi import HTTPException
from math import ceil
from sqlalchemy import select


from app.database import async_session_maker
from app.employees.models import Employee
from app.employees.schemas import (
    EmployeeBase,
    EmployeeCreateResponse,
    EmployeeFilter,
    EmployeeOut,
    EmployeePage,
    EmployeeUpdate,
)
from app.repository.employees import (
    add_employee,
    find_employee_by_id,
    get_employee_filtered,
    is_employee_exist,
    update_employee,
)
from app.repository.employees import delete_employee as delete_employee_by_id


async def employee_list(
    filters: EmployeeFilter,
    page: int,
    size: int
) -> EmployeePage:
    """Возвращает список данных отфильтрованных работников."""
    async with async_session_maker() as session:
        items, total = await get_employee_filtered(
            session, filters, page, size
        )
    return EmployeePage(
        items=[EmployeeOut.model_validate(item) for item in items],
        total=total,
        page=page,
        size=size,
        pages=ceil(total / size) if total else 0,
    )


async def employee_detail(employee_id: int) -> EmployeeOut:
    """Запрашивает в БД работника по id."""
    async with async_session_maker() as session:
        employee = await find_employee_by_id(session, employee_id)
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден'
            )
        return EmployeeOut.model_validate(employee)


async def create_employee(employee: EmployeeBase) -> EmployeeCreateResponse:
    """Добавляет нового работника."""
    async with async_session_maker() as session:
        if await is_employee_exist(
            session, employee.email, employee.phone_number,
        ):
            raise HTTPException(
                status_code=400,
                detail='Работник с таким email и/или номером телефона'
                ' существует',
            )
        created = await add_employee(session, employee.model_dump())
        return EmployeeCreateResponse(
            message='Работник успешно добавлен',
            employee=EmployeeOut.model_validate(created),
        )


async def patch_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
) -> EmployeeOut:
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
        updated = await update_employee(
            session, employee_id,
            **employee_data.model_dump(exclude_unset=True),
        )
        if updated is None:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден'
            )
        return EmployeeOut.model_validate(updated)


async def delete_employee(employee_id: int) -> dict:
    """Обрабатывает удаление работника по id."""
    async with async_session_maker() as session:
        employee = await find_employee_by_id(session, employee_id)
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден',
            )
        result = await delete_employee_by_id(session, employee_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f'Работник с id = {employee_id} не найден'
            )
        return {'message': 'Данные работника успешно удалены'}
