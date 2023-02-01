"""removed unit in GJTestSpecimenQuantity model

Revision ID: bf86627718b5
Revises: 7800511fe39b
Create Date: 2023-02-01 14:30:07.646626

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf86627718b5'
down_revision = '7800511fe39b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimen_quantities', schema=None) as batch_op:
        batch_op.drop_column('unit')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimen_quantities', schema=None) as batch_op:
        batch_op.add_column(sa.Column('unit', sa.VARCHAR(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
