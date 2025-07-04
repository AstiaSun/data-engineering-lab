from typing import Self, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from hw2.src.constants import SQLALCHEMY_DB_URL


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBSession(metaclass=Singleton):
    def __init__(self):
        self._engine = create_engine(SQLALCHEMY_DB_URL)
        self._session: Session | None = None

    def __enter__(self) -> Self:
        self._session = Session(self._engine).__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            self._session.__exit__(exc_type, exc_val, exc_tb)
            self._session.close()
        self._session = None

    @property
    def session(self) -> Session | None:
        return self._session

    def execute(self, query: str) -> Any:
        statement = text(query)
        return self.session.execute(statement)
