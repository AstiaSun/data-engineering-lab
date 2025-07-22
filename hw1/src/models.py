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


class Location(Base):
    __tablename__ = "Locations"

    LocationID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    Country: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="location")
    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="location")


class Interest(Base):
    __tablename__ = "Interests"

    InterestID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    Field: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    campaigns: Mapped[list["Campaign"]] = relationship(back_populates="interest")
    user_interests: Mapped[list["UserInterests"]] = relationship(back_populates="interest")


class User(Base):
    __tablename__ = "Users"

    UserID: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    Age: Mapped[int] = mapped_column(Integer, nullable=False)
    Gender: Mapped[Gender] = mapped_column(Enum(Gender), nullable=False)
    LocationID: Mapped[int] = mapped_column(ForeignKey("Locations.LocationID"), nullable=False)
    SignupDate: Mapped[datetime] = mapped_column(Date)

    location: Mapped["Location"] = relationship(back_populates="users")
    user_interests: Mapped[list["UserInterests"]] = relationship(back_populates="user")
    ad_events: Mapped[list["AdEvent"]] = relationship(back_populates="user")


class UserInterests(Base):
    __tablename__ = "UsersInterests"

    UserID: Mapped[int] = mapped_column(
        ForeignKey("Users.UserID"), primary_key=True, nullable=False
    )
    InterestID: Mapped[int] = mapped_column(
        ForeignKey("Interests.InterestID"), primary_key=True, nullable=False
    )

    user: Mapped[User] = relationship(back_populates="user_interests")
    interest: Mapped["Interest"] = relationship(back_populates="user_interests")


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
    TargetInterestID: Mapped[int] = mapped_column(ForeignKey("Interests.InterestID"), nullable=False)
    TargetLocationID: Mapped[int] = mapped_column(ForeignKey("Locations.LocationID"), nullable=True)

    interest: Mapped["Interest"] = relationship(back_populates="campaigns")
    location: Mapped["Location"] = relationship(back_populates="campaigns")

    ad_events: Mapped[list["AdEvent"]] = relationship(back_populates="campaign")


class AdEvent(Base):
    __tablename__ = "AdEvents"

    EventID: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    UserID: Mapped[int] = mapped_column(ForeignKey("Users.UserID"), nullable=False)
    CampaignID: Mapped[int] = mapped_column(ForeignKey("Campaigns.CampaignID"), nullable=False)
    Timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    Device: Mapped[str] = mapped_column(String(10), nullable=False)
    BidAmount: Mapped[float] = mapped_column(Float, nullable=False)
    AdCost: Mapped[float] = mapped_column(Float, nullable=False)
    WasClicked: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ClickTimestamp: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    AdRevenue: Mapped[float] = mapped_column(Float, nullable=False)

    user: Mapped[User] = relationship(back_populates="ad_events")
    campaign: Mapped[Campaign] = relationship(back_populates="ad_events")
