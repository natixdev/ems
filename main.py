from fastapi import FastAPI

from app.api.v1.employees import router as employees_router
from app.core.logging import setup_logging
from app.core.middleware import log_requests

setup_logging()


app = FastAPI(
    title='Система управления персоналом (EMS)',
    description='Тестовое задание, Хуснутдинова Н.А.',
)
app.middleware('http')(log_requests)

app.include_router(employees_router)
