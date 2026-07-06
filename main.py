from fastapi import FastAPI

from app.api.v1.employees import router as employees_router

app = FastAPI(
    title='Система управления персоналом (EMS)',
    description='Тестовое задание, Хуснутдинова Н.А.',
)

app.include_router(employees_router)
