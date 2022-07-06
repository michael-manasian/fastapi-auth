from asyncio import run
from logging.config import fileConfig
from typing import TYPE_CHECKING

from alembic import context

from src.database.engine import engine
from src.models import BaseModel
from src.settings import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncConnection


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = BaseModel.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.POSTGRES_DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations(connection: "AsyncConnection") -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    async with engine.connect() as connection:
        await connection.run_sync(run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run(run_migrations_online())
