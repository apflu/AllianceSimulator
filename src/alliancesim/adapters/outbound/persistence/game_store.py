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
    EventOption,
    EventResolved,
    InventoryItem,
    MiningStarted,
    PendingEvent,
    PendingNotification,
    PlatformRef,
    ResolveEventRequest,
    SkillLevel,
    StartMiningRequest,
    StartTrainingRequest,
    TrainingStarted,
)
from alliancesim.domain.content import (
    ORE_DISCOVERY_EVENT,
    STARTER_CHARACTER_NAME,
    STARTER_MINING_MODULE_ID,
    STARTER_SHIP_NAME,
    STARTER_SHIP_TYPE_ID,
)
from alliancesim.domain.events import EventOptionDefinition, event_template_from_snapshot
from alliancesim.domain.identity import Platform

from .models import (
    AllianceRow,
    CharacterRow,
    CharacterSkillRow,
    EventOccurrenceRow,
    InventoryItemRow,
    NotificationOutboxRow,
    PlatformIdentityRow,
    PlayerRow,
    ShipRow,
    TimedActionRow,
)

MAX_NOTIFICATION_ATTEMPTS = 10


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
            skill_rows = (
                await session.scalars(
                    select(CharacterSkillRow)
                    .where(CharacterSkillRow.character_id == character.id)
                    .order_by(CharacterSkillRow.skill_id)
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
                skills=tuple(SkillLevel(row.skill_id, row.level) for row in skill_rows),
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
        if action.yield_quantity is None:
            raise ValueError("mining action is missing its yield snapshot")
        return MiningStarted(
            action_id=action.id,
            finishes_at=_aware_utc(action.finishes_at),
            yield_quantity=action.yield_quantity,
            created=created,
        )

    async def get_skill_level(self, identity: PlatformRef, skill_id: str) -> int:
        async with self._sessions() as session:
            alliance = await self._alliance_for_identity(session, identity)
            if alliance is None:
                raise NotFoundError("create an alliance first")
            character_id = await session.scalar(
                select(CharacterRow.id)
                .where(CharacterRow.alliance_id == alliance.id)
                .order_by(CharacterRow.id)
                .limit(1)
            )
            if character_id is None:
                raise NotFoundError("the alliance has no usable starter character")
            level = await session.scalar(
                select(CharacterSkillRow.level).where(
                    CharacterSkillRow.character_id == character_id,
                    CharacterSkillRow.skill_id == skill_id,
                )
            )
            return level or 0

    @staticmethod
    def _training_started(action: TimedActionRow, *, created: bool) -> TrainingStarted:
        if action.skill_id is None or action.target_level is None:
            raise ValueError("training action is missing its skill snapshot")
        return TrainingStarted(
            action_id=action.id,
            skill_id=action.skill_id,
            target_level=action.target_level,
            finishes_at=_aware_utc(action.finishes_at),
            created=created,
        )

    async def start_training(self, request: StartTrainingRequest) -> TrainingStarted:
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
                    return self._training_started(existing, created=False)
                active = await session.scalar(
                    select(TimedActionRow.id).where(
                        TimedActionRow.alliance_id == alliance.id,
                        TimedActionRow.status == "active",
                    )
                )
                if active is not None:
                    raise ConflictError("the alliance already has an active action")
                character_id = await session.scalar(
                    select(CharacterRow.id)
                    .where(CharacterRow.alliance_id == alliance.id)
                    .order_by(CharacterRow.id)
                    .limit(1)
                )
                if character_id is None:
                    raise NotFoundError("the alliance has no usable starter character")
                action = TimedActionRow(
                    alliance_id=alliance.id,
                    character_id=character_id,
                    ship_id=None,
                    action_type="skill_training",
                    location_id=None,
                    material_id=None,
                    status="active",
                    started_at=request.plan.started_at,
                    finishes_at=request.plan.finishes_at,
                    yield_quantity=None,
                    skill_id=request.plan.skill_id,
                    target_level=request.plan.target_level,
                    rules_version=request.plan.rules_version,
                    idempotency_key=request.idempotency_key,
                    notification_platform=request.identity.platform.value,
                    notification_user_id=request.identity.user_id,
                )
                session.add(action)
                await session.flush()
                return self._training_started(action, created=True)
        except IntegrityError as error:
            if alliance_id is not None:
                async with self._sessions() as session:
                    existing = await self._existing_action(
                        session, alliance_id, request.idempotency_key
                    )
                    if existing is not None:
                        return self._training_started(existing, created=False)
            raise ConflictError("the character is already busy") from error

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
                if action.action_type == "mining":
                    if action.material_id is None or action.yield_quantity is None:
                        raise ValueError("mining action has incomplete result data")
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
                    event_type = "mining_completed"
                    payload: dict[str, object] = {
                        "action_id": str(action.id),
                        "material_id": action.material_id,
                        "quantity": action.yield_quantity,
                    }
                    existing_event = await session.scalar(
                        select(EventOccurrenceRow.id).where(
                            EventOccurrenceRow.alliance_id == action.alliance_id,
                            EventOccurrenceRow.template_id == ORE_DISCOVERY_EVENT.template_id,
                        )
                    )
                    if existing_event is None:
                        occurrence = EventOccurrenceRow(
                            alliance_id=action.alliance_id,
                            source_action_id=action.id,
                            template_id=ORE_DISCOVERY_EVENT.template_id,
                            template_version=ORE_DISCOVERY_EVENT.version,
                            content_snapshot=ORE_DISCOVERY_EVENT.snapshot(),
                            status="pending",
                            triggered_at=now,
                            expires_at=now + ORE_DISCOVERY_EVENT.timeout,
                        )
                        session.add(occurrence)
                        await session.flush()
                        payload["event_occurrence_id"] = str(occurrence.id)
                elif action.action_type == "skill_training":
                    if action.skill_id is None or action.target_level is None:
                        raise ValueError("training action has incomplete result data")
                    skill = await session.get(
                        CharacterSkillRow,
                        (action.character_id, action.skill_id),
                        with_for_update=True,
                    )
                    if skill is None:
                        skill = CharacterSkillRow(
                            character_id=action.character_id,
                            skill_id=action.skill_id,
                            level=0,
                        )
                        session.add(skill)
                    skill.level = max(skill.level, action.target_level)
                    event_type = "skill_training_completed"
                    payload = {
                        "action_id": str(action.id),
                        "skill_id": action.skill_id,
                        "level": action.target_level,
                    }
                else:
                    raise ValueError(f"unsupported timed action type: {action.action_type}")
                action.status = "completed"
                action.completed_at = now
                session.add(
                    NotificationOutboxRow(
                        source_action_id=action.id,
                        platform=action.notification_platform,
                        platform_user_id=action.notification_user_id,
                        event_type=event_type,
                        payload=payload,
                        status="pending",
                        available_at=now,
                    )
                )
                completed.append(action.id)
        return CompletionBatch(tuple(completed))

    @staticmethod
    def _pending_event(row: EventOccurrenceRow) -> PendingEvent:
        template = event_template_from_snapshot(dict(row.content_snapshot))
        return PendingEvent(
            occurrence_id=row.id,
            template_id=row.template_id,
            template_version=row.template_version,
            title=template.title,
            body=template.body,
            expires_at=_aware_utc(row.expires_at),
            options=tuple(
                EventOption(option.option_id, option.label) for option in template.options
            ),
        )

    async def list_pending_events(self, identity: PlatformRef) -> tuple[PendingEvent, ...]:
        async with self._sessions() as session:
            alliance = await self._alliance_for_identity(session, identity)
            if alliance is None:
                raise NotFoundError("create an alliance first")
            rows = (
                await session.scalars(
                    select(EventOccurrenceRow)
                    .where(
                        EventOccurrenceRow.alliance_id == alliance.id,
                        EventOccurrenceRow.status == "pending",
                    )
                    .order_by(EventOccurrenceRow.triggered_at, EventOccurrenceRow.id)
                )
            ).all()
            return tuple(self._pending_event(row) for row in rows)

    @staticmethod
    async def _apply_event_effect(
        session: AsyncSession,
        alliance_id: uuid.UUID,
        option: EventOptionDefinition,
    ) -> None:
        inventory = await session.scalar(
            select(InventoryItemRow)
            .where(
                InventoryItemRow.alliance_id == alliance_id,
                InventoryItemRow.material_id == option.effect.material_id,
            )
            .with_for_update()
        )
        if inventory is None:
            inventory = InventoryItemRow(
                alliance_id=alliance_id,
                material_id=option.effect.material_id,
                quantity=0,
            )
            session.add(inventory)
        inventory.quantity += option.effect.quantity

    async def resolve_event(self, request: ResolveEventRequest, now: datetime) -> EventResolved:
        async with self._sessions() as session, session.begin():
            alliance = await self._alliance_for_identity(session, request.identity)
            if alliance is None:
                raise NotFoundError("create an alliance first")
            row = await session.scalar(
                select(EventOccurrenceRow)
                .where(
                    EventOccurrenceRow.id == request.occurrence_id,
                    EventOccurrenceRow.alliance_id == alliance.id,
                )
                .with_for_update()
            )
            if row is None:
                raise NotFoundError("event occurrence not found")
            template = event_template_from_snapshot(dict(row.content_snapshot))
            option = template.option(request.option_id)
            if row.status != "pending":
                if (
                    row.resolution_idempotency_key == request.idempotency_key
                    and row.selected_option_id == request.option_id
                ):
                    return EventResolved(
                        row.id,
                        option.option_id,
                        option.effect.material_id,
                        option.effect.quantity,
                        applied=False,
                    )
                raise ConflictError("event is no longer pending")
            if _aware_utc(row.expires_at) <= _aware_utc(now):
                raise ConflictError("event has expired and awaits automatic resolution")
            await self._apply_event_effect(session, alliance.id, option)
            row.status = "resolved"
            row.resolved_at = now
            row.selected_option_id = option.option_id
            row.resolution_idempotency_key = request.idempotency_key
            return EventResolved(
                row.id,
                option.option_id,
                option.effect.material_id,
                option.effect.quantity,
                applied=True,
            )

    async def expire_due_events(self, now: datetime, *, limit: int) -> int:
        expired = 0
        async with self._sessions() as session, session.begin():
            rows = (
                await session.scalars(
                    select(EventOccurrenceRow)
                    .where(
                        EventOccurrenceRow.status == "pending",
                        EventOccurrenceRow.expires_at <= now,
                    )
                    .order_by(EventOccurrenceRow.expires_at, EventOccurrenceRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            for row in rows:
                template = event_template_from_snapshot(dict(row.content_snapshot))
                option = template.option(template.default_option_id)
                await self._apply_event_effect(session, row.alliance_id, option)
                row.status = "expired"
                row.resolved_at = now
                row.selected_option_id = option.option_id
                expired += 1
        return expired

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
    ) -> bool:
        async with self._sessions() as session, session.begin():
            row = await session.get(NotificationOutboxRow, outbox_id, with_for_update=True)
            if row is None:
                raise NotFoundError("notification not found")
            terminal = row.attempts >= MAX_NOTIFICATION_ATTEMPTS
            if terminal:
                row.status = "failed"
            else:
                delay_seconds = min(300, 2 ** min(row.attempts, 8))
                row.status = "pending"
                row.available_at = now + timedelta(seconds=delay_seconds)
            row.locked_until = None
            row.last_error = error[:500]
            return terminal
