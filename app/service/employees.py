"""Вся бизнес-логика."""

import logging
from math import ceil

from fastapi import HTTPException

from app.employees.constants import (
    EMPLOYEE_ALREADY_EXISTS,
    EMPLOYEE_CREATED,
    EMPLOYEE_DELETED,
    EMPLOYEE_NOT_FOUND,
)
from app.employees.schemas import (
    EmployeeBase,
    EmployeeCreateResponse,
    EmployeeFilter,
    EmployeeOut,
    EmployeePage,
    EmployeeUpdate,
)
from app.repository.employees import EmployeeRepository

logger = logging.getLogger(__name__)


class EmployeeService:
    """Бизнес-логика для сотрудников."""

    def __init__(self, repo: EmployeeRepository) -> None:
        """Сохраняет репозиторий сотрудников."""
        self.repo = repo

    async def employee_list(
        self,
        filters: EmployeeFilter,
        page: int,
        size: int,
    ) -> EmployeePage:
        """Возвращает список данных отфильтрованных работников."""
        logger.info('Fetching employee list page=%s size=%s', page, size)
        items, total = await self.repo.get_employee_filtered(
            filters, page, size,
        )
        return EmployeePage(
            items=[EmployeeOut.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
            pages=ceil(total / size) if total else 0,
        )

    async def employee_detail(self, employee_id: int) -> EmployeeOut:
        """Запрашивает в БД работника по id."""
        logger.info('Fetching employee detail employee_id=%s', employee_id)
        employee = await self.repo.find_employee_by_id(employee_id)
        if employee is None:
            logger.warning('Employee not found')
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        return EmployeeOut.model_validate(employee)

    async def create_employee(
        self, employee: EmployeeBase,
    ) -> EmployeeCreateResponse:
        """Создает нового работника."""
        logger.info(
            'Creating employee email=%s, phone=%s',
            employee.email, employee.phone_number,
        )
        if await self.repo.is_employee_exist(
            employee.email, employee.phone_number,
        ):
            logger.warning('Duplicate employee')
            raise HTTPException(
                status_code=400,
                detail=EMPLOYEE_ALREADY_EXISTS,
            )
        created = await self.repo.add_employee(employee.model_dump())
        return EmployeeCreateResponse(
            message=EMPLOYEE_CREATED,
            employee=EmployeeOut.model_validate(created),
        )

    async def patch_employee(
        self,
        employee_id: int,
        employee_data: EmployeeUpdate,
    ) -> EmployeeOut:
        """Обновляет конкретного работника.

        Если работник не найден -- выбрасывает ошибку 404.
        """
        logger.info('Updating employee employee_id=%s', employee_id)
        employee = await self.repo.find_employee_by_id(employee_id)
        if employee is None:
            logger.warning('Employee not found')
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        updated = await self.repo.update_employee(
            employee_id,
            **employee_data.model_dump(exclude_unset=True),
        )
        if updated is None:
            logger.warning('Employee not found')
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        return EmployeeOut.model_validate(updated)

    async def delete_employee(self, employee_id: int) -> dict:
        """Обрабатывает удаление работника по id."""
        logger.info('Deleting employee employee_id=%s', employee_id)
        employee = self.repo.find_employee_by_id(employee_id)
        if employee is None:
            logger.warning('Employee not found')
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        result = await self.repo.delete_employee(employee_id)
        if not result:
            logger.warning('Employee not found')
            raise HTTPException(
                status_code=404,
                detail=EMPLOYEE_NOT_FOUND.format(employee_id=employee_id),
            )
        return {'message': EMPLOYEE_DELETED}
