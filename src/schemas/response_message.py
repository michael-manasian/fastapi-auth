from pydantic import BaseModel


class ResponseMessage(BaseModel):
    message: str
