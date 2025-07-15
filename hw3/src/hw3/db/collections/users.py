from typing import ClassVar

from .abstract import BaseCollection


class UsersCollection(BaseCollection):
    COLLECTION_NAME: ClassVar[str] = "Users"