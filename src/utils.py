from typing import Callable, Any


class classproperty:  # noqa
    """
    A decorator class converting a method into a
    property that can be accessed directly from the class.

    This class is taken from:
    https://github.com/django/django/blob/main/django/utils/functional.py#L61
    """

    def __init__(self, method: Callable | None = None):
        self.method = method

    def __get__(self, _, cls: type | None = None) -> Any:
        return self.method(cls)

    def getter(self, method: Callable) -> "classproperty":
        self.method = method
        return self
