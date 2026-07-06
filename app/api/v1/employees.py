"""Показывает эндпоинты."""

from fastapi import APIRouter, Depends

from app.employees.schemas import EmployeeFilters, EmployeeOut
from app.service import employees as employee_service

router = APIRouter(prefix='/employees', tags=['Управление работниками'])


@router.get('/', summary='Получить список сотрудников')
async def employee_list(
    filters: EmployeeFilters = Depends(),
) -> list[EmployeeOut]:
    """Возвращает список сотрудников с учетом фильтров (если указаны).

    Фильтры:
      - id: точное совпадение
      - first_name, middle_name, last_name: частичное совпадение (по подстроке)
      - age: возраст (будет найден по году рождения)
      - phone_number: точное совпадение.
    """
    return await employee_service.employee_list(
        **filters.model_dump(exclude_none=True),
    )
