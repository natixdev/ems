from datetime import date

from sqlalchemy.orm import Mapped

from app.core.database import Base, int_pk, str_null_true, str_uniq


class Employee(Base):
    """Модель таблицы Работников."""

    id: Mapped[int_pk]
    last_name: Mapped[str]
    first_name: Mapped[str]
    middle_name: Mapped[str_null_true]
    date_of_birth: Mapped[date]
    sex: Mapped[str]
    photo: Mapped[str_null_true]
    phone_number: Mapped[str_uniq]
    email: Mapped[str_uniq]

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(id={self.id}, '
                f'first_name={self.first_name!r},'
                f'last_name={self.last_name!r})')

    def __repr__(self) -> str:
        return str(self)
