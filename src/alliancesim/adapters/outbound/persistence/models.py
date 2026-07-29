from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class PlayerRow(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PlatformIdentityRow(Base):
    __tablename__ = "platform_identities"
    __table_args__ = (
        UniqueConstraint(
            "platform", "platform_user_id", name="uq_platform_identities_platform_user"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("players.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class AllianceRow(Base):
    __tablename__ = "alliances"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    owner_player_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("players.id"), nullable=False, unique=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CharacterRow(Base):
    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    alliance_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alliances.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    mining_bonus_basis_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class ShipRow(Base):
    __tablename__ = "ships"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    alliance_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alliances.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    ship_type_id: Mapped[str] = mapped_column(String(80), nullable=False)
    mining_module_id: Mapped[str] = mapped_column(String(80), nullable=False)


class InventoryItemRow(Base):
    __tablename__ = "inventory_items"
    __table_args__ = (CheckConstraint("quantity >= 0", name="nonnegative_quantity"),)

    alliance_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("alliances.id"), primary_key=True
    )
    material_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class TimedActionRow(Base):
    __tablename__ = "timed_actions"
    __table_args__ = (
        UniqueConstraint(
            "alliance_id", "idempotency_key", name="uq_timed_actions_alliance_idempotency"
        ),
        Index(
            "uq_timed_actions_active_character",
            "character_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
        Index(
            "uq_timed_actions_active_ship",
            "ship_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    alliance_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("alliances.id"), nullable=False)
    character_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("characters.id"), nullable=False
    )
    ship_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("ships.id"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    location_id: Mapped[str] = mapped_column(String(80), nullable=False)
    material_id: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finishes_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    yield_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    rules_version: Mapped[str] = mapped_column(String(40), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(120), nullable=False)
    notification_platform: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_user_id: Mapped[str] = mapped_column(String(100), nullable=False)


class NotificationOutboxRow(Base):
    __tablename__ = "notification_outbox"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_action_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("timed_actions.id"), nullable=False, unique=True
    )
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    platform_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
