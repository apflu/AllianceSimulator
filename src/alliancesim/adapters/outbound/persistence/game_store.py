from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from alliancesim.application.errors import ConflictError, NotFoundError
from alliancesim.application.models import (
    ActiveAction,
    AllianceCreated,
    AllianceStatus,
    CompletionBatch,
    CreateAllianceRequest,
    InventoryItem,
    MiningStarted,
    PendingNotification,
    PlatformRef,
    StartMiningRequest,
)
from alliancesim.domain.content import (
    STARTER_CHARACTER_NAME,
    STARTER_MINING_MODULE_ID,
    STARTER_SHIP_NAME,
    STARTER_SHIP_TYPE_ID,
)
from alliancesim.domain.identity import Platform

from .models import (
    AllianceRow,
    CharacterRow,
    InventoryItemRow,
    NotificationOutboxRow,
    PlatformIdentityRow,
    PlayerRow,
    ShipRow,
    TimedActionRow,
)


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class SqlAlchemyGameStore:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def _alliance_for_identity(
        self, session: AsyncSession, identity: PlatformRef
    ) -> AllianceRow | None:
        statement = (
            select(AllianceRow)
            .join(PlayerRow, AllianceRow.owner_player_id == PlayerRow.id)
            .join(PlatformIdentityRow, PlatformIdentityRow.player_id == PlayerRow.id)
            .where(
                PlatformIdentityRow.platform == identity.platform.value,
                PlatformIdentityRow.platform_user_id == identity.user_id,
            )
        )
        return await session.scalar(statement)

    async def create_alliance(self, request: CreateAllianceRequest) -> AllianceCreated:
        try:
            async with self._sessions() as session, session.begin():
                existing = await self._alliance_for_identity(session, request.identity)
                if existing is not None:
                    return AllianceCreated(existing.id, existing.name, created=False)

                player = PlayerRow()
                session.add(player)
                await session.flush()
                session.add(
                    PlatformIdentityRow(
                        player_id=player.id,
                        platform=request.identity.platform.value,
                        platform_user_id=request.identity.user_id,
                    )
                )
                alliance = AllianceRow(owner_player_id=player.id, name=request.alliance_name)
                session.add(alliance)
                await session.flush()
                session.add_all(
                    [
                        CharacterRow(alliance_id=alliance.id, name=STARTER_CHARACTER_NAME),
                        ShipRow(
                            alliance_id=alliance.id,
                            name=STARTER_SHIP_NAME,
                            ship_type_id=STARTER_SHIP_TYPE_ID,
                            mining_module_id=STARTER_MINING_MODULE_ID,
                        ),
                    ]
                )
                return AllianceCreated(alliance.id, alliance.name, created=True)
        except IntegrityError as error:
            async with self._sessions() as session:
                existing = await self._alliance_for_identity(session, request.identity)
                if existing is not None:
                    return AllianceCreated(existing.id, existing.name, created=False)
            raise ConflictError("the platform identity is already in use") from error

    async def get_status(self, identity: PlatformRef) -> AllianceStatus:
        async with self._sessions() as session:
            alliance = await self._alliance_for_identity(session, identity)
            if alliance is None:
                raise NotFoundError("create an alliance first")
            character = await session.scalar(
                select(CharacterRow)
                .where(CharacterRow.alliance_id == alliance.id)
                .order_by(CharacterRow.id)
                .limit(1)
            )
            ship = await session.scalar(
                select(ShipRow)
                .where(ShipRow.alliance_id == alliance.id)
                .order_by(ShipRow.id)
                .limit(1)
            )
            if character is None or ship is None:
                raise NotFoundError("the alliance has no usable starter assets")
            inventory_rows = (
                await session.scalars(
                    select(InventoryItemRow)
                    .where(InventoryItemRow.alliance_id == alliance.id)
                    .order_by(InventoryItemRow.material_id)
                )
            ).all()
            action = await session.scalar(
                select(TimedActionRow)
                .where(TimedActionRow.alliance_id == alliance.id, TimedActionRow.status == "active")
                .order_by(TimedActionRow.started_at)
                .limit(1)
            )
            active_action = (
                ActiveAction(action.id, action.action_type, _aware_utc(action.finishes_at))
                if action is not None
                else None
            )
            return AllianceStatus(
                alliance_id=alliance.id,
                name=alliance.name,
                character_id=character.id,
                character_name=character.name,
                ship_id=ship.id,
                ship_name=ship.name,
                inventory=tuple(
                    InventoryItem(row.material_id, row.quantity) for row in inventory_rows
                ),
                active_action=active_action,
            )

    async def _existing_action(
        self, session: AsyncSession, alliance_id: uuid.UUID, idempotency_key: str
    ) -> TimedActionRow | None:
        return await session.scalar(
            select(TimedActionRow).where(
                TimedActionRow.alliance_id == alliance_id,
                TimedActionRow.idempotency_key == idempotency_key,
            )
        )

    @staticmethod
    def _mining_started(action: TimedActionRow, *, created: bool) -> MiningStarted:
        return MiningStarted(
            action_id=action.id,
            finishes_at=_aware_utc(action.finishes_at),
            yield_quantity=action.yield_quantity,
            created=created,
        )

    async def start_mining(self, request: StartMiningRequest) -> MiningStarted:
        alliance_id: uuid.UUID | None = None
        try:
            async with self._sessions() as session, session.begin():
                alliance = await self._alliance_for_identity(session, request.identity)
                if alliance is None:
                    raise NotFoundError("create an alliance first")
                alliance_id = alliance.id
                existing = await self._existing_action(
                    session, alliance.id, request.idempotency_key
                )
                if existing is not None:
                    return self._mining_started(existing, created=False)
                active = await session.scalar(
                    select(TimedActionRow.id).where(
                        TimedActionRow.alliance_id == alliance.id,
                        TimedActionRow.status == "active",
                    )
                )
                if active is not None:
                    raise ConflictError("the alliance already has an active action")
                character = await session.scalar(
                    select(CharacterRow)
                    .where(CharacterRow.alliance_id == alliance.id)
                    .order_by(CharacterRow.id)
                    .limit(1)
                )
                ship = await session.scalar(
                    select(ShipRow)
                    .where(ShipRow.alliance_id == alliance.id)
                    .order_by(ShipRow.id)
                    .limit(1)
                )
                if character is None or ship is None:
                    raise NotFoundError("the alliance has no usable starter assets")
                action = TimedActionRow(
                    alliance_id=alliance.id,
                    character_id=character.id,
                    ship_id=ship.id,
                    action_type="mining",
                    location_id=request.location_id,
                    material_id=request.material_id,
                    status="active",
                    started_at=request.plan.started_at,
                    finishes_at=request.plan.finishes_at,
                    yield_quantity=request.plan.yield_quantity,
                    rules_version=request.plan.rules_version,
                    idempotency_key=request.idempotency_key,
                    notification_platform=request.identity.platform.value,
                    notification_user_id=request.identity.user_id,
                )
                session.add(action)
                await session.flush()
                return self._mining_started(action, created=True)
        except IntegrityError as error:
            if alliance_id is not None:
                async with self._sessions() as session:
                    existing = await self._existing_action(
                        session, alliance_id, request.idempotency_key
                    )
                    if existing is not None:
                        return self._mining_started(existing, created=False)
            raise ConflictError("the character or ship is already busy") from error

    async def complete_due_actions(self, now: datetime, *, limit: int) -> CompletionBatch:
        completed: list[uuid.UUID] = []
        async with self._sessions() as session, session.begin():
            actions = (
                await session.scalars(
                    select(TimedActionRow)
                    .where(
                        TimedActionRow.status == "active",
                        TimedActionRow.finishes_at <= now,
                    )
                    .order_by(TimedActionRow.finishes_at, TimedActionRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            for action in actions:
                inventory = await session.scalar(
                    select(InventoryItemRow)
                    .where(
                        InventoryItemRow.alliance_id == action.alliance_id,
                        InventoryItemRow.material_id == action.material_id,
                    )
                    .with_for_update()
                )
                if inventory is None:
                    inventory = InventoryItemRow(
                        alliance_id=action.alliance_id,
                        material_id=action.material_id,
                        quantity=0,
                    )
                    session.add(inventory)
                inventory.quantity += action.yield_quantity
                action.status = "completed"
                action.completed_at = now
                session.add(
                    NotificationOutboxRow(
                        source_action_id=action.id,
                        platform=action.notification_platform,
                        platform_user_id=action.notification_user_id,
                        event_type="mining_completed",
                        payload={
                            "action_id": str(action.id),
                            "material_id": action.material_id,
                            "quantity": action.yield_quantity,
                        },
                        status="pending",
                        available_at=now,
                    )
                )
                completed.append(action.id)
        return CompletionBatch(tuple(completed))

    async def claim_notifications(
        self, now: datetime, *, limit: int
    ) -> tuple[PendingNotification, ...]:
        claimed: list[PendingNotification] = []
        async with self._sessions() as session, session.begin():
            rows = (
                await session.scalars(
                    select(NotificationOutboxRow)
                    .where(
                        NotificationOutboxRow.available_at <= now,
                        or_(
                            NotificationOutboxRow.status == "pending",
                            and_(
                                NotificationOutboxRow.status == "sending",
                                NotificationOutboxRow.locked_until <= now,
                            ),
                        ),
                    )
                    .order_by(NotificationOutboxRow.available_at, NotificationOutboxRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            for row in rows:
                row.status = "sending"
                row.attempts += 1
                row.locked_until = now + timedelta(seconds=30)
                claimed.append(
                    PendingNotification(
                        outbox_id=row.id,
                        platform=Platform(row.platform),
                        platform_user_id=row.platform_user_id,
                        event_type=row.event_type,
                        payload=dict(row.payload),
                    )
                )
        return tuple(claimed)

    async def mark_notification_sent(self, outbox_id: uuid.UUID, now: datetime) -> None:
        async with self._sessions() as session, session.begin():
            row = await session.get(NotificationOutboxRow, outbox_id, with_for_update=True)
            if row is None:
                raise NotFoundError("notification not found")
            row.status = "sent"
            row.sent_at = now
            row.locked_until = None
            row.last_error = None

    async def mark_notification_failed(
        self, outbox_id: uuid.UUID, now: datetime, error: str
    ) -> None:
        async with self._sessions() as session, session.begin():
            row = await session.get(NotificationOutboxRow, outbox_id, with_for_update=True)
            if row is None:
                raise NotFoundError("notification not found")
            delay_seconds = min(300, 2 ** min(row.attempts, 8))
            row.status = "pending"
            row.available_at = now + timedelta(seconds=delay_seconds)
            row.locked_until = None
            row.last_error = error[:500]
