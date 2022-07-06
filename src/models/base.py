from typing import TYPE_CHECKING

from sqlalchemy.ext.declarative import as_declarative, declared_attr

if TYPE_CHECKING:
    from sqlalchemy import Column


@as_declarative()
class BaseModel:
    """
    A declarative class from which all models in the
    application must be subclassed.
    """

    id: "Column"

    @declared_attr
    def __tablename__(cls) -> str:  # noqa
        """
        Represents __tablename__ as the lowercase class name.
        """
        return cls.__name__.lower()
