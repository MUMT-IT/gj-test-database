"""changed type permission string to boolean in User model

Revision ID: 6fa84e1adfe2
Revises: a291826e8d3c
Create Date: 2023-03-01 15:15:23.848949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6fa84e1adfe2'
down_revision = 'a291826e8d3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('permission')
        batch_op.add_column(sa.Column('permission', sa.Boolean(), default=False))


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('permission', sa.String()))
        batch_op.drop_column('permission')

    # ### end Alembic commands ###
