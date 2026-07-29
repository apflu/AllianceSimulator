"""Generalize timed actions and add character skills.

Revision ID: 20260730_0003
Revises: 20260730_0002
Create Date: 2026-07-30
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0003"
down_revision: str | None = "20260730_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "character_skills",
        sa.Column("character_id", sa.Uuid(), nullable=False),
        sa.Column("skill_id", sa.String(length=80), nullable=False),
        sa.Column("level", sa.Integer(), server_default="0", nullable=False),
        sa.CheckConstraint("level >= 0", name="nonnegative_level"),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["characters.id"],
            name=op.f("fk_character_skills_character_id_characters"),
        ),
        sa.PrimaryKeyConstraint("character_id", "skill_id", name=op.f("pk_character_skills")),
    )
    with op.batch_alter_table("timed_actions") as batch_op:
        batch_op.alter_column("ship_id", existing_type=sa.Uuid(), nullable=True)
        batch_op.alter_column("location_id", existing_type=sa.String(length=80), nullable=True)
        batch_op.alter_column("material_id", existing_type=sa.String(length=80), nullable=True)
        batch_op.alter_column("yield_quantity", existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column("skill_id", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("target_level", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("timed_actions") as batch_op:
        batch_op.drop_column("target_level")
        batch_op.drop_column("skill_id")
        batch_op.alter_column("yield_quantity", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("material_id", existing_type=sa.String(length=80), nullable=False)
        batch_op.alter_column("location_id", existing_type=sa.String(length=80), nullable=False)
        batch_op.alter_column("ship_id", existing_type=sa.Uuid(), nullable=False)
    op.drop_table("character_skills")
