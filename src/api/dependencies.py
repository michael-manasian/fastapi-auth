from abc import abstractmethod
from typing import Generator, Any

import fastapi
from aioredis import StrictRedis
from fastapi.security import OAuth2PasswordBearer
from jose.jwt import JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession as AlchemyAsyncSession

from src.database.session import AsyncSession
from src.models import User
from src.schemas import JWTClaims
from src.security import jwt as jwt_package
from src.services import users
from src.settings import settings


async def get_database_session() -> Generator:
    async with AsyncSession() as session:
        yield session


blacklist = jwt_package.JWTBlacklist(
    StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DATABASE,
        password=settings.REDIS_PASSWORD
    )
)


class JWTProcessor:
    def __init__(self,
                 mission: jwt_package.JWTMission,
                 add_to_blacklist: bool = True):
        """
        Args:
          mission:
            Only JSON Web Tokens with
            this mission will be accepted.

          add_to_blacklist:
            If True, each JSON Web Token
            is blacklisted after processing.
        """
        self._mission = mission
        self._add_to_blacklist = add_to_blacklist

        self._exception = fastapi.HTTPException(
            fastapi.status.HTTP_400_BAD_REQUEST,
            "The given JSON Web Token is invalid."
        )

    @abstractmethod
    async def process_claims(self,
                             claims: JWTClaims,
                             db_session: AlchemyAsyncSession) -> Any:
        """
        Implement this method to add logic for processing an outgoing
        JSON Web Token claims set.

        The method is called after a JSON Web Token has been validated.
        """

    async def __call__(
        self,
        jwt: str = fastapi.Body(...),
        db_session: AlchemyAsyncSession = fastapi.Depends(get_database_session)
    ) -> Any:
        """
        Validates the JSON Web Token and, if it's valid, processes
        its claims set.

        JSON Web Token is considered invalid if one of the following
        conditions is violated: JSON Web Token must have valid signature,
        not an expired one, valid claims set, it mustn't be blacklisted.

        Raises:
          fastapi.HTTPException: If the JSON Web Token is invalid.
        """
        try:
            claims = jwt_package.decode_jwt(jwt)
        except (JWTError, ValidationError):
            raise self._exception

        if (
            claims.mission != self._mission or
            await blacklist.is_blocked(jwt)
        ):
            raise self._exception

        if self._add_to_blacklist:
            await blacklist.block(jwt, claims.exp)

        return await self.process_claims(claims, db_session)


class JWTUser(JWTProcessor):
    async def process_claims(self,
                             claims: JWTClaims,
                             db_session: AlchemyAsyncSession) -> User:
        """
        Returns:
          The JSON Web Token user referenced by the 'sub'.

        Raises:
          fastapi.HTTPException: If the user hasn't been found.
        """
        user = await users.get_user_by_id(
            db_session,
            user_id=claims.sub
        )
        if user is None:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_404_NOT_FOUND,
                "The JSON Web Token user hasn't been found."
            )
        return user


class JWTConfirmedUser(JWTUser):
    async def process_claims(self,
                             claims: JWTClaims,
                             db_session: AlchemyAsyncSession) -> User:
        """
        Returns:
          The active JSON Web Token user referenced by the 'sub'.

        Raises:
          fastapi.HTTPException:
            If the user hasn't been found or is unconfirmed.
        """
        user = await super().process_claims(claims, db_session)
        if not user.is_confirmed:
            raise fastapi.HTTPException(
                fastapi.status.HTTP_404_NOT_FOUND,
                "The JSON Web Token user is unconfirmed."
            )
        return user


oauth2 = OAuth2PasswordBearer(f"{settings.API_V1}/login-access-token")


class JWTAuthenticationUser(JWTConfirmedUser):
    def __call__(
        self,
        jwt: str = fastapi.Depends(oauth2),
        db_session: AlchemyAsyncSession = fastapi.Depends(get_database_session)
    ) -> Any:
        super().__call__(jwt, db_session)
