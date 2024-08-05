"""Added on delete for book and author

Revision ID: d74a430a0819
Revises: 679d1f9af5ee
Create Date: 2024-08-05 14:42:41.035369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd74a430a0819'
down_revision: Union[str, None] = '679d1f9af5ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a new table with the updated schema
    op.create_table(
        'bookauthorassociation_new',
        sa.Column('book_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['author_id'], ['author.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('book_id', 'author_id')
    )

    # Copy data from the old table to the new table
    op.execute(
        "INSERT INTO bookauthorassociation_new (book_id, author_id) "
        "SELECT book_id, author_id FROM bookauthorassociation"
    )

    # Drop the old table
    op.drop_table('bookauthorassociation')

    # Rename the new table to the original table name
    op.rename_table('bookauthorassociation_new', 'bookauthorassociation')

def downgrade() -> None:
    # Create a new table with the old schema (without nullable=True)
    op.create_table(
        'bookauthorassociation_old',
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['book_id'], ['book.id']),
        sa.ForeignKeyConstraint(['author_id'], ['author.id']),
        sa.PrimaryKeyConstraint('book_id', 'author_id')
    )

    # Copy data from the current table to the old table
    op.execute(
        "INSERT INTO bookauthorassociation_old (book_id, author_id) "
        "SELECT book_id, author_id FROM bookauthorassociation"
    )

    # Drop the current table
    op.drop_table('bookauthorassociation')

    # Rename the old table back to the original table name
    op.rename_table('bookauthorassociation_old', 'bookauthorassociation')