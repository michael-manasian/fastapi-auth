import typing
from datetime import timedelta
from secrets import token_urlsafe

import pydantic


class Settings(pydantic.BaseSettings):
    APPLICATION_NAME: str = "fastapi-auth"
    API_V1: str = "/api/v1"
    SECRET_TOKEN: str = token_urlsafe(32)

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str
    POSTGRES_DATABASE: str
    POSTGRES_DATABASE_URI: pydantic.PostgresDsn | None = None

    @pydantic.validator("POSTGRES_DATABASE_URI", pre=True)
    def construct_database_uri(
        cls,
        value: str | None,
        values: dict[str | typing.Any]
    ) -> str:
        if isinstance(value, str):
            return value

        return pydantic.PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path="/" + values.get("POSTGRES_DATABASE")
        )

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DATABASE: str | int = 0
    REDIS_PASSWORD: str | None = None

    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_LIFETIME: timedelta = timedelta(hours=2)
    MFA_TOKEN_LIFETIME: timedelta = timedelta(hours=2)

    USERS_CLEANUP_DELAY: int = timedelta(days=7).total_seconds()

    class Config:
        case_sensitive = True


settings = Settings()

