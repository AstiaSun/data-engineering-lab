"""connect adevents and campaigns

Revision ID: 43ae1e39aa9a
Revises: 98d697f6181a
Create Date: 2025-06-11 00:43:37.565860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43ae1e39aa9a'
down_revision: Union[str, None] = '98d697f6181a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "AdEvents",
        sa.Column("CampaignID", sa.BigInteger, nullable=False)
    )
    op.execute(
        """
            UPDATE AdEvents
            SET CampaignID = (
                SELECT Campaigns.CampaignID
                FROM Campaigns
                WHERE Campaigns.CampaignName = AdEvents.CampaignName
                  AND Campaigns.AdvertiserName = AdEvents.AdvertiserName
                LIMIT 1
            )
        """
    )
    op.create_foreign_key(
        constraint_name="fk_adevents_campaignid",
        source_table="AdEvents",
        referent_table="Campaigns",
        local_cols=["CampaignID"],
        remote_cols=["CampaignID"],
        ondelete="CASCADE"
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
            UPDATE AdEvents
            SET CampaignName, AdvertiserName = (
                SELECT Campaigns.CampaignName, Campaigns.AdvertiserName
                FROM Campaigns
                WHERE Campaigns.CampaignID = AdEvents.CampaignID
            )
        """
    )
    op.drop_constraint('fk_adevents_campaignid', 'AdEvents', type_='foreignkey')
    op.drop_column('AdEvents', 'CampaignID')