from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import engine


AsyncSession = sessionmaker(autoflush=True, class_=AsyncSession, bind=engine)
