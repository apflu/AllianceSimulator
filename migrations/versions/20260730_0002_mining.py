"""Create starter assets, timed actions, inventory and outbox.

Revision ID: 20260730_0002
Revises: 20260730_0001
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0002"
down_revision: str | None = "20260730_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "characters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alliance_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("mining_bonus_basis_points", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(
            ["alliance_id"], ["alliances.id"], name=op.f("fk_characters_alliance_id_alliances")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_characters")),
    )
    op.create_table(
        "ships",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alliance_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("ship_type_id", sa.String(length=80), nullable=False),
        sa.Column("mining_module_id", sa.String(length=80), nullable=False),
        sa.ForeignKeyConstraint(
            ["alliance_id"], ["alliances.id"], name=op.f("fk_ships_alliance_id_alliances")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ships")),
    )
    op.create_table(
        "inventory_items",
        sa.Column("alliance_id", sa.Uuid(), nullable=False),
        sa.Column("material_id", sa.String(length=80), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("quantity >= 0", name="nonnegative_quantity"),
        sa.ForeignKeyConstraint(
            ["alliance_id"],
            ["alliances.id"],
            name=op.f("fk_inventory_items_alliance_id_alliances"),
        ),
        sa.PrimaryKeyConstraint("alliance_id", "material_id", name=op.f("pk_inventory_items")),
    )
    op.create_table(
        "timed_actions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("alliance_id", sa.Uuid(), nullable=False),
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("ship_id", sa.Uuid(), nullable=False),
        sa.Column("action_type", sa.String(length=40), nullable=False),
        sa.Column("location_id", sa.String(length=80), nullable=False),
        sa.Column("material_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finishes_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("yield_quantity", sa.Integer(), nullable=False),
        sa.Column("rules_version", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("notification_platform", sa.String(length=20), nullable=False),
        sa.Column("notification_user_id", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["alliance_id"],
            ["alliances.id"],
            name=op.f("fk_timed_actions_alliance_id_alliances"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("fk_timed_actions_character_id_characters"),
        ),
        sa.ForeignKeyConstraint(
            ["ship_id"], ["ships.id"], name=op.f("fk_timed_actions_ship_id_ships")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_timed_actions")),
        sa.UniqueConstraint(
            "alliance_id", "idempotency_key", name="uq_timed_actions_alliance_idempotency"
        ),
    )
    active = sa.text("status = 'active'")
    op.create_index(
        "uq_timed_actions_active_character",
        "timed_actions",
        ["character_id"],
        unique=True,
        postgresql_where=active,
        sqlite_where=active,
    )
    op.create_index(
        "uq_timed_actions_active_ship",
        "timed_actions",
        ["ship_id"],
        unique=True,
        postgresql_where=active,
        sqlite_where=active,
    )
    op.create_index(
        op.f("ix_timed_actions_finishes_at"), "timed_actions", ["finishes_at"], unique=False
    )
    op.create_table(
        "notification_outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_action_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("platform_user_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_action_id"],
            ["timed_actions.id"],
            name=op.f("fk_notification_outbox_source_action_id_timed_actions"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_notification_outbox")),
        sa.UniqueConstraint(
            "source_action_id", name=op.f("uq_notification_outbox_source_action_id")
        ),
    )
    op.create_index(
        op.f("ix_notification_outbox_available_at"),
        "notification_outbox",
        ["available_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_notification_outbox_available_at"), table_name="notification_outbox")
    op.drop_table("notification_outbox")
    op.drop_index(op.f("ix_timed_actions_finishes_at"), table_name="timed_actions")
    op.drop_index("uq_timed_actions_active_ship", table_name="timed_actions")
    op.drop_index("uq_timed_actions_active_character", table_name="timed_actions")
    op.drop_table("timed_actions")
    op.drop_table("inventory_items")
    op.drop_table("ships")
    op.drop_table("characters")
