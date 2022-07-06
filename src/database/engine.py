from sqlalchemy.ext.asyncio import create_async_engine

from src.settings import settings


engine = create_async_engine(settings.POSTGRES_DATABASE_URI, future=True, pool_pre_ping=True)
