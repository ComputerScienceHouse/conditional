"""empty message

Revision ID: 8f8820a72637
Revises: 983d69afb7f8
Create Date: 2016-12-29 19:29:22.512317

"""

# revision identifiers, used by Alembic.
revision = '8f8820a72637'
down_revision = '983d69afb7f8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('member_committee_attendance', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('member_hm_attendance', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column('member_seminar_attendance', sa.Column('active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('member_seminar_attendance', 'active')
    op.drop_column('member_hm_attendance', 'active')
    op.drop_column('member_committee_attendance', 'active')
    # ### end Alembic commands ###
