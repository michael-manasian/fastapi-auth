import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from src import schemas
from src.api import dependencies
from src.emails import send_multi_factor_authentication_jwt
from src.models import User
from src.security import jwt, password
from src.services import users
from src.settings import settings


router = fastapi.APIRouter()


@router.post(
    "/request-multi-factor-authentication-token",
    response_model=schemas.ResponseMessage
)
async def send_mfa_token(
    mission: jwt.JWTMission,
    email_address: str = fastapi.Body(...),
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    user = await users.get_user_by_email_address(db_session, email_address)
    if user is None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            "The user with this email address doesn't exist."
        )

    json_web_token = jwt.create_jwt(
        str(user.id),
        mission,
        settings.MFA_TOKEN_LIFETIME
    )
    await send_multi_factor_authentication_jwt(user, json_web_token)

    return {"message": "A multi-factor authentication token has been sent."}


@router.post(
    "/create-user",
    response_model=schemas.UserDisplaySchema
)
async def create_user(
    user: schemas.UserCreationSchema,
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    if await users.get_user_by_email_address(db_session, user.email_address):
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            "The chosen username is already taken."
        )
    new_user = await users.create_user(db_session, user)
    return new_user


@router.post(
    "/receive-access-token",
    response_model=schemas.ResponseAccessToken
)
async def provide_access_token(
    credentials: schemas.Credentials,
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    user = await users.authenticate_user(db_session, credentials)
    if user is None:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            "The credentials are invalid."
        )

    access_token = jwt.create_jwt(
        str(user.id),
        jwt.JWTMission.ACCESS_TOKEN,
        settings.ACCESS_TOKEN_LIFETIME
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/confirm-user", response_model=schemas.ResponseMessage)
async def confirm_user(
    user: User = fastapi.Depends(
        dependencies.JWTUser(jwt.JWTMission.REGISTRATION_CONFIRMATION)
    ),
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    user.is_confirmed = True
    await db_session.commit()
    return {"message": "The user has been confirmed successfully."}


@router.post(
    "/recover-password",
    response_model=schemas.ResponseMessage
)
async def recover_password(
    new_password: str = fastapi.Body(**schemas.PASSWORD_KWARGS),
    user: User = fastapi.Depends(
        dependencies.JWTUser(jwt.JWTMission.RECOVER_PASSWORD)
    ),
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    user.password = password.get_hashed_password(new_password)
    await db_session.commit()
    return {"message": "The password has been changed successfully."}


@router.post(
    "/delete-user",
    response_model=schemas.ResponseMessage
)
async def delete_user(
    user: User = fastapi.Depends(
        dependencies.JWTConfirmedUser(jwt.JWTMission.CONFIRM_USER_DELETION)
    ),
    db_session: AsyncSession = fastapi.Depends(dependencies.get_database_session)
):
    await db_session.delete(user)
    await db_session.commit()
    return {"message": "The user has been deleted successfully."}
