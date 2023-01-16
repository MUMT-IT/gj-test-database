"""Removed location column and location id in GJTestSpecimenTransportation model

Revision ID: c7be9a503fbd
Revises: 2116032ecc42
Create Date: 2022-12-29 15:57:12.367255

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7be9a503fbd'
down_revision = '2116032ecc42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimen_transportations', schema=None) as batch_op:
        batch_op.drop_constraint('gj_test_specimen_transportations_location_id_fkey', type_='foreignkey')
        batch_op.drop_column('location_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_test_specimen_transportations', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('gj_test_specimen_transportations_location_id_fkey', 'gj_test_locations', ['location_id'], ['id'])

    # ### end Alembic commands ###
