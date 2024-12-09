"""check_constraints_added

Revision ID: 8b9f594423e5
Revises: e6bbdba13386
Create Date: 2024-12-05 13:35:48.001680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b9f594423e5'
down_revision: Union[str, None] = 'e6bbdba13386'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adding check constraints manually
    op.create_check_constraint('chk_activity_level_minimum', 'customers', 'activity_level >= 1.2')
    op.create_check_constraint('chk_activity_level_maximum', 'customers', 'activity_level <= 1.725')

def downgrade() -> None:
    # Dropping the constraints manually during downgrade
    op.drop_constraint('chk_activity_level_minimum', 'customers', type_='check')
    op.drop_constraint('chk_activity_level_maximum', 'customers', type_='check')
