"""empty message

Revision ID: 8552875e037f
Revises: 1738d11342bf
Create Date: 2021-11-13 18:46:49.515030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8552875e037f'
down_revision = '1738d11342bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_info', sa.Column('picture_file', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_info', 'picture_file')
    # ### end Alembic commands ###
