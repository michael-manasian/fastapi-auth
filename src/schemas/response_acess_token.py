from pydantic import BaseModel


class ResponseAccessToken(BaseModel):
    access_token: str
    token_type: str
