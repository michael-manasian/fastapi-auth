from passlib.context import CryptContext


ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(raw_password: str) -> str:
    return ctx.hash(raw_password)


def check_password(raw_password: str, hashed_password: str) -> str:
    return ctx.verify(raw_password, hashed_password)
