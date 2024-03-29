"""Moved unit column from GJTest to GJ TestSpecimen model

Revision ID: e5c825b61ee4
Revises: 61b4ca5568c1
Create Date: 2022-12-29 13:49:08.390030

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5c825b61ee4'
down_revision = '61b4ca5568c1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit', sa.String(), nullable=True))

    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.drop_column('unit')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit', sa.VARCHAR(), autoincrement=False, nullable=True))

    with op.batch_alter_table('gj_test_specimens', schema=None) as batch_op:
        batch_op.drop_column('unit')

    # ### end Alembic commands ###
