from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Liste PC Montage"
    environment: str = "production"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/pcmontage"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24
    cors_origins: str = "*"
    admin_username: str = "admin"
    admin_password: str = "admin"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
