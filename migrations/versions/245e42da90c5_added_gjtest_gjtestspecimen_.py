"""Added GJTest, GJTestSpecimen, GJTestLocation, GJTestDate, GJTestTimePeriodRequest, and GJTestWaitingPeriod model

Revision ID: 245e42da90c5
Revises: 
Create Date: 2022-12-26 13:55:00.506706

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '245e42da90c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gj_test_dates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_date', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gj_test_locations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gj_test_time_period_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time_period_request', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gj_test_waiting_periods',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('waiting_time_normal', sa.String(), nullable=True),
    sa.Column('waiting_time_urgent', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gj_test_specimens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('specimen', sa.String(), nullable=True),
    sa.Column('specimen_quantity', sa.String(), nullable=True),
    sa.Column('specimen_container', sa.String(), nullable=True),
    sa.Column('specimen_date_time', sa.String(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['gj_test_locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gj_tests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('test_name', sa.String(), nullable=True),
    sa.Column('code', sa.String(), nullable=True),
    sa.Column('desc', sa.Text(), nullable=True),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('prepare', sa.String(), nullable=True),
    sa.Column('specimen_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('solution', sa.String(), nullable=True),
    sa.Column('test_date_id', sa.Integer(), nullable=True),
    sa.Column('time_period_request_id', sa.Integer(), nullable=True),
    sa.Column('waiting_period_id', sa.Integer(), nullable=True),
    sa.Column('reporting_referral_values', sa.String(), nullable=True),
    sa.Column('time_period_requested', sa.String(), nullable=True),
    sa.Column('interference_analysis', sa.String(), nullable=True),
    sa.Column('caution', sa.String(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['gj_test_locations.id'], ),
    sa.ForeignKeyConstraint(['specimen_id'], ['gj_test_specimens.id'], ),
    sa.ForeignKeyConstraint(['test_date_id'], ['gj_test_dates.id'], ),
    sa.ForeignKeyConstraint(['time_period_request_id'], ['gj_test_time_period_requests.id'], ),
    sa.ForeignKeyConstraint(['waiting_period_id'], ['gj_test_waiting_periods.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gj_tests')
    op.drop_table('gj_test_specimens')
    op.drop_table('gj_test_waiting_periods')
    op.drop_table('gj_test_time_period_requests')
    op.drop_table('gj_test_locations')
    op.drop_table('gj_test_dates')
    # ### end Alembic commands ###
