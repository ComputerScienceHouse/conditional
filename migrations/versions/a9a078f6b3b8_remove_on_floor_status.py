"""remove on floor status

Revision ID: a9a078f6b3b8
Revises: 3f094d78df95
Create Date: 2026-10-26 20:18:38.312393

"""

# revision identifiers, used by Alembic.
revision = 'a9a078f6b3b8'
down_revision = '3f094d78df95'

from alembic import op
import sqlalchemy as sa

def upgrade():

    op.rename_table('onfloor_datetime', 'housing_queue_assignment')

    with op.batch_alter_table('housing_queue_assignment', schema=None) as batch_op:
        batch_op.alter_column('onfloor_granted', new_column_name='housing_queue_joined')

    with op.batch_alter_table('freshman_accounts', schema=None) as batch_op:
        batch_op.drop_column('onfloor_status')

    # ### end Alembic commands ###


def downgrade():
    op.rename_table('housing_queue_assignment', 'onfloor_datetime')

    with op.batch_alter_table('onfloor_datetime', schema=None) as batch_op:
        batch_op.alter_column('housing_queue_joined', new_column_name='onfloor_granted')

    with op.batch_alter_table('freshman_accounts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('onfloor_status', sa.BOOLEAN(), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
