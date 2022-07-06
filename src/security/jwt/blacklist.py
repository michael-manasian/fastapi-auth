from calendar import timegm
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aioredis import Redis


class JWTBlacklist:
    """
    The application may need to deny access using some
    JSON Web Token before it expires, but it's impossible
    because this mechanism works independently of the server.

    So this class stores wasted JWTs in Redis, which allows
    the application to invalidate a JSON Web Token prematurely.
    """

    def __init__(self, redis_storage: "Redis"):
        self._redis_storage = redis_storage
        # Zero is used as the value for each
        # record because we only work with keys.
        self._default_value = 0

    async def is_blocked(self, jwt: str) -> bool:
        """
        Returns: A Boolean value designating whether
                 the JSON Web Token is in the blacklist.
        """
        record = await self._redis_storage.exists(jwt)
        return bool(record)

    async def block(self, jwt: str, exp: int) -> None:
        """
        Adds the JSON Web Token to the blacklist until its
        signatures expires.
        """
        current_timetuple = datetime.utcnow().utctimetuple()
        lifetime = exp - timegm(current_timetuple)

        await self._redis_storage.set(jwt, self._default_value, lifetime)
