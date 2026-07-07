"""Все, что касается работы с данными и БД."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.employees.models import Employee
from app.employees.schemas import EmployeeFilter

ILIKE_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'phone_number',
]


async def get_employee_filtered(
    session: AsyncSession,
    filters: EmployeeFilter,
) -> list[Employee]:
    """Фильтрует список работников по заданным фильтрам."""
    query = filters.filter(select(Employee))
    result = await session.execute(query)
    return result.scalars().all()


async def find_employee_by_id(
    session: AsyncSession,
    employee_id: int,
) -> Employee | None:
    """Возвращает работника по id или None, если не существует."""
    result = await session.execute(select(Employee).filter_by(id=employee_id))
    return result.scalar_one_or_none()


async def is_employee_exist(
    session: AsyncSession,
    email: str,
    phone_number: str,
) -> bool:
    """Проверяет, существует ли работник в БД по email и phone_number."""
    query = select(Employee).where(
        (Employee.email == email) | (Employee.phone_number == phone_number),
    )
    result = await session.execute(query)
    return result.scalars().first() is not None


async def add_employee(session: AsyncSession, employee_data: dict) -> Employee:
    """Добавляет данные работника в БД."""
    employee = Employee(
        last_name=employee_data['last_name'],
        first_name=employee_data['first_name'],
        middle_name=employee_data.get('middle_name', None),
        date_of_birth=employee_data['date_of_birth'],
        sex=employee_data['sex'],
        photo=str(employee_data.get('photo')),
        phone_number=employee_data['phone_number'],
        email=employee_data['email'],
    )
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


async def update_employee(
    session: AsyncSession, employee_id: int, **values: Any,
) -> Employee | None:
    """Обновляет данные работника.

    Возвращает обновлённого работника или None, если не найден.
    """
    employee = await session.get(Employee, employee_id)
    if employee is None:
        return None

    for key, value in values.items():
        setattr(employee, key, value)

    await session.commit()
    return await session.get(Employee, employee_id)


async def delete_employee(
    session: AsyncSession, employee_id: int,
) -> dict | None:
    """Удаляет работника по id или None, если не существует."""
    employee = await session.get(Employee, employee_id)
    if employee is None:
        return None
    await session.delete(employee)
    await session.commit()
    return {'message': 'Данные работника успешно удалены'}
