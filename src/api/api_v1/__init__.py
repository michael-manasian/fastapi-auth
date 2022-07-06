from fastapi import APIRouter

from src.api.api_v1.endpoints import auth


api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["users"]
)
