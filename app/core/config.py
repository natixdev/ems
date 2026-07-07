from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / '.env'


class Settings(BaseSettings):
    """Настройки приложения для загрузки из .env и окружения."""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    model_config = SettingsConfigDict(env_file=ENV_FILE)


settings = Settings()


def get_db_url() -> str:
    """Формирует путь для подключения к БД."""
    return (f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@'
            f'{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}')
