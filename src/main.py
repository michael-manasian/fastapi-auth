from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

from src.api.api_v1 import api_router
from src.database.session import AsyncSession
from src.services.users import delete_unconfirmed_users
from src.settings import settings


application = FastAPI(
    title=settings.APPLICATION_NAME,
    openapi_url=f"{settings.API_V1}/openapi.json"
)
application.include_router(api_router)


@application.on_event("startup")
@repeat_every(seconds=settings.USERS_CLEANUP_DELAY)
async def cleanup_unconfirmed_users() -> None:
    async with AsyncSession() as session:
        await delete_unconfirmed_users(session)
