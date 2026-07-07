"""Вся бизнес-логика."""


from fastapi import HTTPException
from math import ceil

from app.database import async_session_maker
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
    delete_employee as delete_employee_by_id,
)
from app.employees.constants import (
    EMPLOYEE_ALREADY_EXISTS,
    EMPLOYEE_NOT_FOUND,
    EMPLOYEE_DELETED,
    EMPLOYEE_CREATED,
)


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
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
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
                detail=EMPLOYEE_ALREADY_EXISTS,
            )
        created = await add_employee(session, employee.model_dump())
        return EmployeeCreateResponse(
            message=EMPLOYEE_CREATED,
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
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        updated = await update_employee(
            session, employee_id,
            **employee_data.model_dump(exclude_unset=True),
        )
        if updated is None:
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        return EmployeeOut.model_validate(updated)


async def delete_employee(employee_id: int) -> dict:
    """Обрабатывает удаление работника по id."""
    async with async_session_maker() as session:
        employee = await find_employee_by_id(session, employee_id)
        if employee is None:
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        result = await delete_employee_by_id(session, employee_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        return {'message': EMPLOYEE_DELETED}
