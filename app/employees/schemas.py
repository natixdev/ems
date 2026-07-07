import re
from datetime import date
from enum import Enum

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator
from sqlalchemy.orm import Query
from sqlalchemy.sql.selectable import Select

from .models import Employee

PHONE_PATTERN = r'^(\+7)\d{10}$'
MIN_AGE = 14
MAX_AGE = 122


class SexEnum(str, Enum):
    """Пол сотрудника."""

    MALE = 'Муж.'
    FEMALE = 'Жен.'


class EmployeeValidatorMixin:
    """Миксин, добавляющий валидацию даты рождения и телефона."""

    @field_validator('date_of_birth')
    @classmethod
    def _validate_date_of_birth(cls, value: date | None) -> date | None:
        """Проверяет дату рождения.

        Вызывает ошибку, если возраст менее MIN_AGE(14) или более MAX_AGE(122).
        """
        if value is None:
            return value
        today = date.today()
        if value >= today:
            raise ValueError('Дата рождения не может быть в будущем')
        age = today.year - value.year - (
            (today.month, today.day) < (value.month, value.day)
        )
        if age < MIN_AGE:
            raise ValueError(f'Возраст должен быть не менее {MIN_AGE} лет')
        if age > MAX_AGE:
            raise ValueError(f'Возраст должен быть не более {MAX_AGE} лет')
        return value

    @field_validator('phone_number')
    @classmethod
    def _validate_phone(cls, value: str | None) -> str | None:
        """Проверяет, что номер телефона указан в формате +7XXXXXXXXXX."""
        if value is None:
            return value
        if not re.match(PHONE_PATTERN, value):
            raise ValueError('Введите номер телефона в формате +7XXXXXXXXXX')
        return value


class EmployeeBase(EmployeeValidatorMixin, BaseModel):
    """Базовая схема работника."""

    last_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50 )
    middle_name: str | None = Field(None, max_length=50)
    date_of_birth: date
    sex: SexEnum
    photo: HttpUrl | None = None
    phone_number: str
    email: EmailStr


class EmployeeOut(BaseModel):
    """Схема для ответа API – содержит id и все поля EmployeeBase."""

    id: int
    last_name: str
    first_name: str
    middle_name: str | None
    date_of_birth: date
    sex: SexEnum
    photo: str | None
    phone_number: str
    email: EmailStr

    class Config:
        from_attributes = True


class EmployeeFilter(Filter):
    """Класс для фильтрации списка сотрудников."""

    id: int | None = None
    last_name__ilike: str | None = None
    first_name__ilike: str | None = None
    middle_name__ilike: str | None = None
    age: int | None = None
    phone_number: str | None = None

    class Constants(Filter.Constants):
        model = Employee

    class Config:
        allow_population_by_field_name = True

    def filter(self, query: Query | Select) -> Query | Select:
        """Преобразует возраст (age) в диапазон дат рождения."""
        age = self.age
        self.age = None
        query = super().filter(query)

        if age is not None:
            today = date.today()
            year = today.year - age
            birth_date_start = date(year - 1, today.month, today.day + 1) if (
                today.day < 28
            ) else date(year - 1, today.month, 28)
            birth_date_end = date(year, today.month, today.day)

            query = query.where(
                Employee.date_of_birth >= birth_date_start,
                Employee.date_of_birth <= birth_date_end,
            )
        return query


class EmployeeUpdate(EmployeeValidatorMixin, BaseModel):
    """Схема для частичного обновления сотрудника."""

    last_name: str | None = Field(None, min_length=1, max_length=50)
    first_name: str | None = Field(None, min_length=1, max_length=50)
    middle_name: str | None = Field(None, max_length=50)
    date_of_birth: date | None = None
    sex: SexEnum | None = None
    photo: HttpUrl | None = None
    phone_number: str | None = None
    email: EmailStr | None = None
