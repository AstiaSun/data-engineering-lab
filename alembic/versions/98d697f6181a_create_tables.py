"""create tables

Revision ID: 98d697f6181a
Revises:
Create Date: 2025-06-11 00:22:40.533948

"""

from enum import Enum
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector

# revision identifiers, used by Alembic.
revision: str = "98d697f6181a"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class Gender(Enum):
    Male = "Male"
    Female = "Female"
    Non_Binary = "Non-Binary"


def upgrade() -> None:
    """Upgrade schema."""
    inspector = Inspector.from_engine(op.get_bind().engine)
    if "Users" in inspector.get_table_names():
        return
    op.create_table(
        "Users",
        sa.Column("UserID", sa.BigInteger, primary_key=True),
        sa.Column("Age", sa.Integer, nullable=False),
        sa.Column("Gender", sa.Enum(Gender), nullable=False),
        sa.Column("Location", sa.String(30), nullable=False),
    )
    op.create_table(
        "UsersInterests",
        sa.Column(
            "UserID",
            sa.BigInteger,
            sa.ForeignKey("Users.UserID", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("Interest", sa.String(20), primary_key=True, nullable=False),
    )
    op.create_table(
        "Campaigns",
        sa.Column("CampaignID", sa.BigInteger, primary_key=True),
        sa.Column("CampaignName", sa.String(30), nullable=False),
        sa.Column("AdvertiserName", sa.String(50), nullable=False),
        sa.Column("CampaignStartDate", sa.Date, nullable=False),
        sa.Column("CampaignEndDate", sa.Date, nullable=False),
        sa.Column("AdSlotSize", sa.String(11), nullable=False),
        sa.Column("Budget", sa.Float, nullable=False),
        sa.Column("RemainingBudget", sa.Float, nullable=False),
        sa.Column("TargetAgeMin", sa.Integer, nullable=False),
        sa.Column("TargetAgeMax", sa.Integer, nullable=False),
        sa.Column("TargetInterest", sa.String(15), nullable=False),
        sa.Column("TargetLocation", sa.String(50), nullable=False),
    )

    op.create_table(
        "AdEvents",
        sa.Column("EventID", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "UserID", sa.BigInteger, sa.ForeignKey("Users.UserID", ondelete="CASCADE")
        ),
        sa.Column(
            "CampaignID",
            sa.BigInteger,
            sa.ForeignKey("Campaigns.CampaignID", ondelete="CASCADE"),
        ),
        sa.Column("Timestamp", sa.DateTime, nullable=False),
        sa.Column("Device", sa.String(20), nullable=False),
        sa.Column("BidAmount", sa.Float, nullable=False),
        sa.Column("AdCost", sa.Float, nullable=False),
        sa.Column("WasClicked", sa.Boolean, nullable=False),
        sa.Column("ClickTimestamp", sa.DateTime, nullable=True),
        sa.Column("AdRevenue", sa.Float, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("UsersInterests")
    op.drop_table("Users")
    op.drop_table("Campaigns")
    op.drop_table("AdEvents")
