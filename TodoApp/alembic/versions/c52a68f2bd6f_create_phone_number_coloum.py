"""create phone number coloum

Revision ID: c52a68f2bd6f
Revises: 
Create Date: 2026-04-17 10:51:22.326373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c52a68f2bd6f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.String(),nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'phone_number')
