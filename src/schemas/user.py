import pydantic


PASSWORD_KWARGS = {
    "min_length": 8,
    "max_length": 128,
    "regex": (
        r"(?=.*?[a-z])"
        r"(?=.*?[A-Z])"
        r"(?=.*?[0-9])"
    )
}


class UserCreationSchema(pydantic.BaseModel):
    first_name: str = pydantic.Field(min_length=2, max_length=50)
    last_name: str = pydantic.Field(max_length=50)
    email_address: pydantic.EmailStr
    password: str = pydantic.Field(**PASSWORD_KWARGS)


class Credentials(pydantic.BaseModel):
    email_address: str
    password: str


class UserDisplaySchema(pydantic.BaseModel):
    id: int
    first_name: str
    last_name: str
    is_confirmed: bool
    email_address: str

    class Config:
        orm_mode = True

