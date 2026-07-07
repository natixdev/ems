"""Показывает эндпоинты."""

from fastapi import APIRouter, Query, status
from fastapi_filter import FilterDepends

from app.employees.schemas import (
    EmployeeBase,
    EmployeeCreateResponse,
    EmployeeFilter,
    EmployeeOut,
    EmployeePage,
    EmployeeUpdate,
)
from app.service import employees as employee_service

router = APIRouter(prefix='/employees', tags=['Управление работниками'])


@router.get(
    '/',
    response_model=EmployeePage,
    summary='Получить список сотрудников',
)
async def employee_list(
    filters: EmployeeFilter = FilterDepends(EmployeeFilter),
    page: int = Query(1, ge=1, description='Номер страницы'),
    size: int = Query(10, ge=1, le=100, description='Размер страницы'),
) -> EmployeePage:
    """Возвращает список работников с учетом фильтров (если указаны).

    Фильтры:
      - id: точное совпадение
      - first_name, middle_name, last_name: частичное совпадение (по подстроке)
      - age: возраст (будет найден по году рождения)
      - phone_number: точное совпадение.
    """
    return await employee_service.employee_list(
        filters=filters, page=page, size=size)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=EmployeeCreateResponse,
    summary='Добавить нового сотрудника',
)
async def create_employee(employee: EmployeeBase) -> EmployeeCreateResponse:
    """Добавляет нового работника."""
    return await employee_service.create_employee(employee=employee)


@router.get(
    '/{employee_id}',
    response_model=EmployeeOut,
    summary='Получить данные конкретного сотрудника',
)
async def employee_detail(employee_id: int) -> EmployeeOut:
    """Возвращает данные конкретного сотрудника."""
    return await employee_service.employee_detail(employee_id=employee_id)


@router.patch(
    '/{employee_id}',
    response_model=EmployeeOut,
    summary='Обновить данные конкретного сотрудника',
)
async def patch_employee(
    employee_id: int,
    employee_data_to_update: EmployeeUpdate,
) -> EmployeeOut:
    """Обновляет данные конкретного сотрудника частично."""
    return await employee_service.patch_employee(
        employee_id=employee_id,
        employee_data=employee_data_to_update,
    )


@router.delete(
    '/{employee_id}',
    summary='Удалить данные конкретного сотрудника',
)
async def delete_employee(employee_id: int) -> dict:
    """Удаляет данные конкретного сотрудника."""
    return await employee_service.delete_employee(employee_id=employee_id)
