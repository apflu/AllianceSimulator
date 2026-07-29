"""Create player identities and alliances.

Revision ID: 20260730_0001
Revises:
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "players",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_players")),
    )
    op.create_table(
        "alliances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_player_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_player_id"], ["players.id"], name=op.f("fk_alliances_owner_player_id_players")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_alliances")),
        sa.UniqueConstraint("owner_player_id", name=op.f("uq_alliances_owner_player_id")),
    )
    op.create_table(
        "platform_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("player_id", sa.Uuid(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False),
        sa.Column("platform_user_id", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["player_id"], ["players.id"], name=op.f("fk_platform_identities_player_id_players")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_platform_identities")),
        sa.UniqueConstraint(
            "platform", "platform_user_id", name="uq_platform_identities_platform_user"
        ),
    )


def downgrade() -> None:
    op.drop_table("platform_identities")
    op.drop_table("alliances")
    op.drop_table("players")
