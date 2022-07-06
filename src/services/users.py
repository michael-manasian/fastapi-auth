from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from src.models import User
from src.schemas import UserCreationSchema, Credentials
from src.security.password import get_hashed_password, check_password
from src.settings import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_by_id(session: "AsyncSession", user_id: int) -> User | None:
    return await session.get(User, user_id)


async def get_user_by_email_address(session: "AsyncSession", email_address: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email_address == email_address)
    )
    return result.scalar()


async def create_user(session: "AsyncSession",
                      user_creation_data: UserCreationSchema) -> User:
    """
    Creates a new user in the database, pre-hashing his password.
    """
    new_user = User(
        first_name=user_creation_data.first_name,
        last_name=user_creation_data.last_name,
        email_address=user_creation_data.email_address,
        password=get_hashed_password(user_creation_data.password)
    )
    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return new_user


async def authenticate_user(session: "AsyncSession",
                            credentials: Credentials) -> User | None:
    """
    Returns: The user referenced by the given email address, if the given password
             matches the required one, and this user is confirmed. Otherwise, None.
    """
    user = await get_user_by_email_address(session, credentials.email_address)

    is_allowed = (
        user is not None and
        user.is_confirmed and
        check_password(credentials.password, user.password)
    )
    if is_allowed:
        return user


async def delete_unconfirmed_users(session: "AsyncSession") -> None:
    """
    Deletes users who haven't yet been confirmed.

    Notes:
      * Unconfirmed users who're expected to confirm their
        registration won't be deleted.

        It'd be extremely irrational to delete a newly created user,
        since he wouldn't even have enough time to confirm registration.

      * It's intended to be called periodically as part of the
        application maintenance procedure.

        First, it optimizes the database. In addition, we allow
        re-registration to any previously taken email address that can't
        be confirmed because a JSON Web Token issued for this has expired.
    """
    statement = select(User).where(
        User.is_confirmed.is_(False)
    )
    unconfirmed_users = await session.execute(statement)

    for unconfirmed_user in unconfirmed_users.scalars():
        confirmation_token_expiration_ts = (
            unconfirmed_user.created_at + settings.MFA_JWT_TOKEN_LIFETIME
        )
        if datetime.utcnow() >= confirmation_token_expiration_ts:
            await session.delete(unconfirmed_user)

    await session.commit()
