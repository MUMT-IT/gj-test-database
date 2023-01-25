"""Changed type string to text in reporing_referral_value column in GJTest model

Revision ID: 6e4ffc7cb4b1
Revises: b80210206543
Create Date: 2023-01-22 23:40:09.984077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e4ffc7cb4b1'
down_revision = 'b80210206543'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.alter_column('reporting_referral_values',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gj_tests', schema=None) as batch_op:
        batch_op.alter_column('reporting_referral_values',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=True)


    # ### end Alembic commands ###
