"""This is the main file for this application"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.v1.router.router import api_router as main_router
from configuration.config import settings
from configuration.database import Base, engine
from easter_eggs.greeting import ascii_hello_devs, default_art

logging.basicConfig(level=logging.INFO)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


print(ascii_hello_devs)
print(default_art)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.include_router(main_router)


# Test routes. We will remove those later
@app.get("/hello")
async def hello():
    """This is a test route"""
    return {"message": "Hello, World!"}


@app.get("/config-info")
async def config_info():
    """This route returns the configuration information"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "app_running_env": settings.app_running_env,
        "greeting_message": settings.greeting_message,
    }


@app.on_event("startup")
async def startup_event():
    # Добавляем вызов функции создания таблиц
    await create_tables()


async def create_tables():
    """Создает таблицы в базе данных при запуске приложения."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
