"""AI usage input for major projects

Revision ID: 3bf67c4939f6
Revises: 3f094d78df95
Create Date: 2026-10-05 20:47:05.837923

"""

# revision identifiers, used by Alembic.
revision = "3bf67c4939f6"
down_revision = "3f094d78df95"

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column("major_projects", sa.Column("ai_usage", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("major_projects", "ai_usage")
