"""Create persistent alliance event occurrences.

Revision ID: 20260730_0004
Revises: 20260730_0003
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0004"
down_revision: str | None = "20260730_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "event_occurrences",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alliance_id", sa.Uuid(), nullable=False),
        sa.Column("source_action_id", sa.Uuid(), nullable=False),
        sa.Column("template_id", sa.String(length=80), nullable=False),
        sa.Column("template_version", sa.Integer(), nullable=False),
        sa.Column("content_snapshot", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("triggered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("selected_option_id", sa.String(length=80), nullable=True),
        sa.Column("resolution_idempotency_key", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(
            ["alliance_id"],
            ["alliances.id"],
            name=op.f("fk_event_occurrences_alliance_id_alliances"),
        ),
        sa.ForeignKeyConstraint(
            ["source_action_id"],
            ["timed_actions.id"],
            name=op.f("fk_event_occurrences_source_action_id_timed_actions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event_occurrences")),
        sa.UniqueConstraint(
            "alliance_id", "template_id", name="uq_event_occurrences_alliance_template"
        ),
        sa.UniqueConstraint("source_action_id", name=op.f("uq_event_occurrences_source_action_id")),
    )
    op.create_index(
        op.f("ix_event_occurrences_expires_at"),
        "event_occurrences",
        ["expires_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_event_occurrences_expires_at"), table_name="event_occurrences")
    op.drop_table("event_occurrences")
