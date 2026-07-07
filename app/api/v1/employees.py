"""Показывает эндпоинты."""

from fastapi import APIRouter, status
from fastapi_filter import FilterDepends

from app.employees.schemas import (
    EmployeeBase,
    EmployeeFilter,
    EmployeeOut,
    EmployeeUpdate,
)
from app.service import employees as employee_service

router = APIRouter(prefix='/employees', tags=['Управление работниками'])


@router.get('/', summary='Получить список сотрудников')
async def employee_list(
    filters: EmployeeFilter = FilterDepends(EmployeeFilter),
) -> list[EmployeeOut]:
    """Возвращает список работников с учетом фильтров (если указаны).

    Фильтры:
      - id: точное совпадение
      - first_name, middle_name, last_name: частичное совпадение (по подстроке)
      - age: возраст (будет найден по году рождения)
      - phone_number: точное совпадение.
    """
    return await employee_service.employee_list(filters)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    summary='Добавить нового сотрудника',
)
async def create_employee(employee: EmployeeBase) -> dict:
    """Добавляет нового работника."""
    created_employee = await employee_service.create_employee(
        **employee.dict(),
    )
    if created_employee:
        return {'message': 'Работник успешно добавлен', 'employee': employee}
    return {'message': 'Ошибка при добавлении работника'}


@router.get('/{employee_id}', summary='Получить данные конкретного сотрудника')
async def employee_detail(employee_id: int) -> EmployeeOut | dict:
    """Возвращает данные конкретного сотрудника."""
    result = await employee_service.employee_detail(employee_id)
    if result is None:
        return {'message': f'Работник с id = {employee_id} не найден'}
    return result


@router.patch(
    '/{employee_id}',
    response_model=EmployeeOut,
    summary='Обновить данные конкретного сотрудника',
)
async def patch_employee(
    employee_id: int,
    employee_data_to_update: EmployeeUpdate,
) -> EmployeeOut | None:
    """Обновляет данные конкретного сотрудника частично."""
    return await employee_service.patch_employee(
        employee_id, **employee_data_to_update.model_dump(exclude_unset=True),
    )


@router.delete(
    '/{employee_id}',
    summary='Удалить данные конкретного сотрудника',
)
async def delete_employee(employee_id: int) -> dict:
    """Удаляет данные конкретного сотрудника."""
    return await employee_service.delete_employee(employee_id)
