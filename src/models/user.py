from datetime import datetime

import sqlalchemy

from src.models import BaseModel


class User(BaseModel):
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        index=True,
        primary_key=True
    )
    first_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    last_name = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    email_address = sqlalchemy.Column(
        sqlalchemy.String,
        index=True,
        unique=True,
        nullable=False
    )
    password = sqlalchemy.Column(
        sqlalchemy.String,
        nullable=False
    )
    is_confirmed = sqlalchemy.Column(
        sqlalchemy.Boolean,
        index=True,
        default=False,
        nullable=False
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    @property
    def full_name(self) -> str:
        return "{} {}".format(self.name, self.surname)

