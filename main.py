
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.employees import router as employees_api_router
from app.core.config import BASE_DIR
from app.core.logging import setup_logging
from app.core.middleware import log_requests
from app.routers.employees_web import router as employees_web_router

STATIC_DIR = BASE_DIR / 'app' / 'static'

setup_logging()


app = FastAPI(
    title='Система управления персоналом (EMS)',
    description='Тестовое задание, Хуснутдинова Н.А.',
)
app.middleware('http')(log_requests)


app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')

app.include_router(employees_api_router, prefix='/api')
app.include_router(employees_web_router)
