"""Все, что касается работы с данными и БД."""

import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.employees.models import Employee
from app.employees.schemas import EmployeeFilter

ILIKE_FIELDS = [
    'first_name',
    'middle_name',
    'last_name',
    'phone_number',
]


logger = logging.getLogger(__name__)


class EmployeeRepository:
    """Репозиторий для работы с сотрудниками."""

    def __init__(self, session: AsyncSession) -> None:
        """Сохраняет сессию БД."""
        self.session = session

    async def get_employee_filtered(
        self,
        filters: EmployeeFilter,
        page: int,
        size: int,
    ) -> tuple[list[Employee], int]:
        """Возвращает отфильтрованных сотрудников и их общее количество."""
        base_query = filters.filter(select(Employee))
        total = await self.session.scalar(
            select(func.count()).select_from(base_query.subquery()),
        ) or 0
        query = (
            base_query
            .order_by(Employee.id)
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.session.execute(query)
        items = result.scalars().all()
        return items, total

    async def find_employee_by_id(
        self,
        employee_id: int,
    ) -> Employee | None:
        """Возвращает работника по id или None, если не существует."""
        result = await self.session.execute(select(Employee)
                                            .filter_by(id=employee_id))
        return result.scalar_one_or_none()

    async def is_employee_exist(
        self,
        email: str,
        phone_number: str,
    ) -> bool:
        """Проверяет, существует ли работник в БД по email и phone_number."""
        query = select(Employee).where(
            (Employee.email == email)
            | (Employee.phone_number == phone_number),
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None

    async def add_employee(
        self,
        employee_data: dict[str, Any],
    ) -> Employee:
        """Добавляет данные работника в БД."""
        employee = Employee(
            last_name=employee_data['last_name'],
            first_name=employee_data['first_name'],
            middle_name=employee_data.get('middle_name'),
            date_of_birth=employee_data['date_of_birth'],
            sex=employee_data['sex'],
            photo=str(employee_data.get('photo'))
            if employee_data.get('photo') else None,
            phone_number=employee_data['phone_number'],
            email=employee_data['email'],
        )
        self.session.add(employee)
        await self.session.commit()
        await self.session.refresh(employee)
        return employee

    async def update_employee(
        self, employee_id: int, **values: Any,
    ) -> Employee | None:
        """Обновляет данные работника.

        Возвращает обновлённого работника или None, если не найден.
        """
        employee = await self.session.get(Employee, employee_id)
        if employee is None:
            return None

        for key, value in values.items():
            setattr(employee, key, value)

        await self.session.commit()
        await self.session.refresh(employee)
        return employee

    async def delete_employee(self, employee_id: int) -> bool:
        """Удаляет работника по id или None, если не существует."""
        employee = await self.session.get(Employee, employee_id)
        if employee is None:
            return False
        await self.session.delete(employee)
        await self.session.commit()
        return True
