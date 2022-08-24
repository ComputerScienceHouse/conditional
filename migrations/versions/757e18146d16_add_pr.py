"""Add PR

Revision ID: 757e18146d16
Revises: 3eaae92ce6b3
Create Date: 2022-09-07 12:13:17.966970

"""

# revision identifiers, used by Alembic.
revision = '757e18146d16'
down_revision = '3eaae92ce6b3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.alter_column('committee_meetings', 'committee',
               existing_type=postgresql.ENUM('Evaluations', 'History', 'Social', 'Opcomm',
                            'R&D', 'House Improvements', 'Financial', 'Public Relations', 'Chairman', 'Ad-Hoc', name="committees_enum"),
               nullable=False)


def downgrade():
    op.alter_column('committee_meetings', 'committee',
               existing_type=postgresql.Enum('Evaluations', 'History', 'Social', 'Opcomm',
                            'R&D', 'House Improvements', 'Financial', 'Chairman', 'Ad-Hoc', name="committees_enum"),
               nullable=False)
