"""Dropped specimen id and specimen relationship in GJTest model

Revision ID: 02d1942af1ed
Revises: b1bea04a8d07
Create Date: 2023-01-20 15:21:49.168850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '02d1942af1ed'
down_revision = 'b1bea04a8d07'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.drop_constraint('gj_tests_specimen_id_fkey', type_='foreignkey')
        batch_op.drop_column('specimen_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specimen_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('gj_tests_specimen_id_fkey', 'gj_test_specimens', ['specimen_id'], ['id'])


    # ### end Alembic commands ###
