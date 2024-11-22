# config.py
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Loading .env file
load_dotenv(os.getenv("APP_ENV_PATH"))
print(f"Loaded .env path: {os.getenv('APP_ENV_PATH')}")


class Settings(BaseSettings):
    app_name: str
    app_version: str
    app_running_env: str
    greeting_message: str
    database_url: str

    class Config:
        env_file = os.getenv("APP_ENV_PATH")
        extra = "ignore"


settings = Settings()  # type: ignore
