"""Added specimens_unit column and relationship in GJTestSpecimenSource model 

Revision ID: e97a7914cf7b
Revises: bf86627718b5
Create Date: 2023-02-01 14:41:52.373752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e97a7914cf7b'
down_revision = 'bf86627718b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gj_test_specimen_units',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('specimens_unit', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('gj_test_specimen_sources', schema=None) as batch_op:
        batch_op.add_column(sa.Column('specimens_unit_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'gj_test_specimen_units', ['specimens_unit_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimen_sources', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('specimens_unit_id')

    op.drop_table('gj_test_specimen_units')
    # ### end Alembic commands ###