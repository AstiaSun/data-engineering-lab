import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Enum,
    Date,
    ForeignKey,
    DateTime,
    Boolean,
    Float,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Gender(enum.Enum):
    Male = "Male"
    Female = "Female"
    Non_Binary = "Non-Binary"


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "Users"

    UserID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    Age: Mapped[int] = mapped_column(Integer, nullable=False)
    Gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    Location: Mapped[str] = mapped_column(String(30), nullable=False)

    AdEvents: Mapped[list["AdEvent"]] = relationship(back_populates="user")
    Interests: Mapped[list["UserInterests"]] = relationship(back_populates="user")


class UserInterests(Base):
    __tablename__ = "UsersInterests"

    UserID: Mapped[User] = mapped_column(
        ForeignKey("Users.UserID"), primary_key=True, nullable=False
    )
    Interest: Mapped[String] = mapped_column(
        String(20), primary_key=True, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="Interests")


class Campaign(Base):
    __tablename__ = "Campaigns"

    CampaignID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    AdvertiserName: Mapped[str] = mapped_column(String(50), nullable=False)
    CampaignName: Mapped[str] = mapped_column(String(30), nullable=False)
    CampaignStartDate: Mapped[datetime] = mapped_column(Date, nullable=False)
    CampaignEndDate: Mapped[datetime] = mapped_column(Date, nullable=False)
    AdSlotSize: Mapped[str] = mapped_column(String(11), nullable=False)
    Budget: Mapped[float] = mapped_column(nullable=False)
    RemainingBudget: Mapped[float] = mapped_column(nullable=False)
    TargetAgeMin: Mapped[int] = mapped_column(nullable=False)
    TargetAgeMax: Mapped[int] = mapped_column(nullable=False)
    TargetInterest: Mapped[str] = mapped_column(String(15), nullable=False)
    TargetLocation: Mapped[str] = mapped_column(String(50), nullable=False)

    AdEvents: Mapped[list["AdEvent"]] = relationship(back_populates="campaign")


class AdEvent(Base):
    __tablename__ = "AdEvents"

    EventID: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)

    UserID: Mapped[int] = mapped_column(ForeignKey("Users.UserID"), nullable=False)
    CampaignID: Mapped[str] = mapped_column(
        ForeignKey("Campaigns.CampaignID"), nullable=False
    )
    Timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    Device: Mapped[str] = mapped_column(String(10), nullable=False)
    BidAmount: Mapped[float] = mapped_column(Float, nullable=False)
    AdCost: Mapped[float] = mapped_column(Float, nullable=False)
    WasClicked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ClickTimestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    AdRevenue: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped[User] = relationship(back_populates="AdEvents")
    campaign: Mapped[Campaign] = relationship(back_populates="AdEvents")
