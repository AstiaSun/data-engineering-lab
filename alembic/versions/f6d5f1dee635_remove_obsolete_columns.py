"""remove-obsolete-columns

Revision ID: f6d5f1dee635
Revises: 43ae1e39aa9a
Create Date: 2025-06-12 08:55:55.360088

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6d5f1dee635'
down_revision: Union[str, None] = '43ae1e39aa9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("AdEvents", "CampaignName")
    op.drop_column("AdEvents", "AdvertiserName")



def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("AdEvents", sa.Column("CampaignName", sa.String(30), nullable=False))
    op.add_column("AdEvents", sa.Column("AdvertiserName", sa.String(50), nullable=False))
