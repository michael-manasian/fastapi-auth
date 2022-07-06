from datetime import datetime
from typing import TYPE_CHECKING

from jose.jwt import encode, decode

from src.schemas import JWTClaims
from src.security.jwt.mission import JWTMission
from src.settings import settings

if TYPE_CHECKING:
    from datetime import timedelta


def create_jwt(sub: str, mission: JWTMission, lifetime: "timedelta") -> str:
    """
    Returns: A new JSON Web Token with the given lifetime.
             Its claims set includes the 'sub' and 'mission'.
    """
    claims = {
        "sub": sub,
        "exp": datetime.utcnow() + lifetime,
        "mission": mission
    }
    return encode(claims, settings.SECRET_TOKEN, settings.JWT_ALGORITHM)


def decode_jwt(jwt: str) -> JWTClaims:
    """
    Returns: A JWTClaims instance
             containing the JSON Web Token claims.

    Raises:
      jose.JWTError:
        If the JSON Web Token signature/any of its
        claims is invalid.

      pydantic.ValidationError:
        If the JWT claims set doesn't contain a
        required claim, or its type isn't serializable.
    """
    claims = decode(jwt, settings.SECRET_TOKEN, settings.JWT_ALGORITHM)
    return JWTClaims(**claims)
