"""empty message

Revision ID: d2d4aad22c26
Revises: a033d03b1230
Create Date: 2024-05-09 14:18:42.072380

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2d4aad22c26'
down_revision = 'a033d03b1230'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('show_items_artist_id_fkey', 'show_items', type_='foreignkey')
    op.drop_column('show_items', 'artist_id')
    op.drop_column('show_items', 'id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show_items', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('show_items', sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('show_items_artist_id_fkey', 'show_items', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###
