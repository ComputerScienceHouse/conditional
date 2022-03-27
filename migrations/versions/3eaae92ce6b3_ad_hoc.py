"""ad_hoc

Revision ID: 3eaae92ce6b3
Revises: 4ac8ff82410a
Create Date: 2019-09-06 15:32:42.472975

"""

# revision identifiers, used by Alembic.
from alembic.ddl import postgresql

revision = '3eaae92ce6b3'
down_revision = '4ac8ff82410a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.alter_column('directorship_meetings', 'directorship',
               existing_type=postgresql.ENUM('Evaluations', 'History', 'Social', 'Opcomm',
                            'R&D', 'House Improvements', 'Financial', 'Chairman', 'Ad-Hoc', name="directorships_enum"),
               nullable=False)


def downgrade():
    op.alter_column('directorship_meetings', 'directorship',
               existing_type=postgresql.Enum('Evaluations', 'History', 'Social', 'Opcomm',
                            'R&D', 'House Improvements', 'Financial', 'Chairman', name="directorships_enum"),
               nullable=False)
