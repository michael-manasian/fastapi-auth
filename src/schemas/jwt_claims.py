from pydantic import BaseModel


class JWTClaims(BaseModel):
    sub: int
    exp: int
    mission: str
