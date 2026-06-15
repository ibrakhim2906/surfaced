"""add salary_currency to jobs

Revision ID: c3a1f8b92e10
Revises: 7dfe28af890e
Create Date: 2026-06-15

"""
from alembic import op
import sqlalchemy as sa

revision = "c3a1f8b92e10"
down_revision = "7dfe28af890e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("salary_currency", sa.String(10), server_default="KZT", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("jobs", "salary_currency")
