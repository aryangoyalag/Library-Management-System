"""Added on delete to user table

Revision ID: 679d1f9af5ee
Revises: 7b3d54929520
Create Date: 2024-08-05 14:30:51.349540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '679d1f9af5ee'
down_revision: Union[str, None] = '7b3d54929520'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
