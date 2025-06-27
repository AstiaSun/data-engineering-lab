from typing import Self, Any

from sqlalchemy import create_engine, Connection, Engine, text
from sqlalchemy.orm import Session

from constants import SQLALCHEMY_DB_URL
from hw1.src.models import Base


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
    def engine(self) -> Engine:
        return self._engine

    @property
    def session(self) -> Session | None:
        return self._session

    def connection(self) -> Connection | None:
        if self._session:
            return self._session.connection()
        return None

    def execute(self, query: str) -> Any:
        statement = text(query)
        return self.session.execute(statement)

    def insert_batch(self, batch: list[Base]):
        self._session.bulk_save_objects(batch)
        self._session.commit()
