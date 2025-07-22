from functools import lru_cache
from typing import Self, Any

from sqlalchemy import create_engine, Connection, Engine, text, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from .constants import SQLALCHEMY_DB_URL
from .models import Base, Interest, Location, Campaign


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
        self._session = Session(self._engine, expire_on_commit=False).__enter__()
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
        result = self.session.execute(statement)
        self._session.commit()
        return result

    def insert_batch(self, batch: list[Base]):
        self.session.bulk_save_objects(batch)
        self.session.commit()

    @lru_cache(maxsize=20)
    def get_interest(self, interest: str) -> Interest:
        try:
            statement = select(Interest).where(Interest.Field == interest)
            return self.session.execute(statement).scalar_one()
        except NoResultFound:
            new_interest = Interest(Field=interest)
            self.session.add(new_interest)
            self.session.flush()
            return new_interest

    @lru_cache(maxsize=20)
    def get_location(self, location: str) -> Location:
        try:
            statement = select(Location).where(Location.Country == location)
            return self.session.execute(statement).scalar_one()
        except NoResultFound:
            new_location = Location(Country=location)
            self.session.add(new_location)
            self.session.flush()
            return new_location

    def update_campaigns(self, fields_by_id: dict[int, dict[str, Any]]):
        for campaign_id, fields in fields_by_id.items():
            statement = update(Campaign).where(Campaign.CampaignID==campaign_id).values(**fields)
            self.session.execute(statement)
        self.session.commit()
