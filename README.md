# Система управления персоналом (EMS)

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

REST API для управления сотрудниками на FastAPI

## Возможности

- Создание сотрудника
- Получение списка сотрудников (фильтры: ФИО, возраст, номер телефона)
- Получение сотрудника по ID
- Обновление сотрудника
- Удаление сотрудника

## Стек

- Python 3.12+
- FastAPI
- Uvicorn
- Pydantic v2
- pydantic-settings
- PostgreSQL
- SQLAlchemy

## Структура проекта

```text
app/
├── api/
│   └── v1/
│       └── employees.py  # маршрутизация
├── core/
│   ├── config.py
│   ├── database.py
│   ├── dependency.py
│   ├── logging.py
│   └── middleware.py
├── employees/
│   ├── constants.py
│   └── models.py
│   ├── schemas.py
├── service/              # бизнес-логика
│   └── employees.py
├── repository/
│   └── employees.py      # запросы к БД
main.py
.env
```

## Установка

1. Клонируйте проект
2. Создайте виртуальное окружение
3. Установите зависимости

```bash
pip install -r requirements.txt
```

## Настройка окружения

Создайте файл `.env` в корне проекта:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ems_db
DB_USER=postgres
DB_PASSWORD=your_password
```

## Локальный запуск

```bash
uvicorn main:app --reload
```

После запуска API будет доступно по адресу:

```text
http://127.0.0.1:8000
```

## Документация API

FastAPI автоматически генерирует документацию:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## API endpoints

### Employees

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/employees` | Получить список сотрудников |
| GET | `/api/v1/employees/{employee_id}` | Получить сотрудника по ID |
| POST | `/api/v1/employees` | Создать нового сотрудника |
| PATCH | `/api/v1/employees/{employee_id}` | Частично обновить сотрудника |
| DELETE | `/api/v1/employees/{employee_id}` | Удалить сотрудника |


## Логирование

В проекте настроено логирование:

- запросов к API
- времени обработки запросов
- ключевых событий в сервисном слое
- ошибок и предупреждений


## Автор
Хуснутдинова Наталья | [ссылка на github](https://github.com/natixdev)
