"""Added loan_requested and loan_accepted to Loan table

Revision ID: 7b3d54929520
Revises: a4f95be27a46
Create Date: 2024-08-05 12:45:08.970148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b3d54929520'
down_revision: Union[str, None] = 'a4f95be27a46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('loan', sa.Column('loan_requested', sa.Boolean(), nullable=True))
    op.add_column('loan', sa.Column('loan_approved', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('loan', 'loan_approved')
    op.drop_column('loan', 'loan_requested')
    # ### end Alembic commands ###