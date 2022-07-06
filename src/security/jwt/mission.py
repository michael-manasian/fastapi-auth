from enum import Enum

from src.utils import classproperty


class JWTMission(str, Enum):
    """
    Determines what a JSON Web Token was created for.

    Each user can have more than one JSON Web Token at the same
    time, which implies that the application must distinguish them.
    """

    REGISTRATION_CONFIRMATION = "registration-confirmation"
    RECOVER_PASSWORD = "recover-password"
    CONFIRM_USER_DELETION = "confirm-user-deletion"

    @classproperty
    def ACCESS_TOKEN(cls) -> str:  # noqa
        """
        We want FastAPI to not include this member in its
        schema, but it's impossible to do it more gracefully, so
        we represent it as a property because it's used only in code.
        """
        return "access-token"

