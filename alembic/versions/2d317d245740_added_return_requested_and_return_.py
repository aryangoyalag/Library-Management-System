"""Added return_requested and return_accepted to Loan table

Revision ID: 2d317d245740
Revises: 1144a5afc29a
Create Date: 2024-08-05 12:15:06.931299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d317d245740'
down_revision: Union[str, None] = '1144a5afc29a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('loan', sa.Column('return_requested', sa.Boolean(), nullable=True))
    op.add_column('loan', sa.Column('return_accepted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('loan', 'return_accepted')
    op.drop_column('loan', 'return_requested')
    # ### end Alembic commands ###
