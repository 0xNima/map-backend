"""migration-001

Revision ID: 8460e06a6ddb
Revises: 
Create Date: 2023-05-14 13:48:12.794048

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '8460e06a6ddb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('query_report_url', sqlalchemy_utils.types.url.URLType(), nullable=True))
        batch_op.add_column(sa.Column('query_start_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('query_end_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('query_indicator_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'indicators', ['query_indicator_id'], ['id'])
        batch_op.drop_column('report_url')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('report_url', sa.TEXT(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('query_indicator_id')
        batch_op.drop_column('query_end_date')
        batch_op.drop_column('query_start_date')
        batch_op.drop_column('query_report_url')

    # ### end Alembic commands ###