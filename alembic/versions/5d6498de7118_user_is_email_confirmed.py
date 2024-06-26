"""user_is_email_confirmed

Revision ID: 5d6498de7118
Revises: 2b76db564670
Create Date: 2024-05-09 16:21:07.797047

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5d6498de7118'
down_revision: Union[str, None] = '2b76db564670'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_email_confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'is_email_confirmed')
    # ### end Alembic commands ###
