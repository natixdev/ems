from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.repository.employees import EmployeeRepository
from app.service.employees import EmployeeService


def get_employee_service(
    session: AsyncSession = Depends(get_session),
) -> EmployeeService:
    """Создаёт сервис сотрудников с доступом к БД."""
    repo = EmployeeRepository(session)
    return EmployeeService(repo)
