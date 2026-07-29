from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from alliancesim.application.models import (
    AllianceCreated,
    AllianceStatus,
    CompletionBatch,
    CreateAllianceRequest,
    EventResolved,
    MiningStarted,
    PendingEvent,
    PendingNotification,
    PlatformRef,
    ResolveEventRequest,
    StartMiningRequest,
    StartTrainingRequest,
    TrainingStarted,
)


class DatabaseProbe(Protocol):
    async def probe(self) -> bool: ...


class WorkPoller(Protocol):
    async def poll_once(self) -> int: ...


class GameStore(Protocol):
    async def create_alliance(self, request: CreateAllianceRequest) -> AllianceCreated: ...

    async def get_status(self, identity: PlatformRef) -> AllianceStatus: ...

    async def start_mining(self, request: StartMiningRequest) -> MiningStarted: ...

    async def get_skill_level(self, identity: PlatformRef, skill_id: str) -> int: ...

    async def start_training(self, request: StartTrainingRequest) -> TrainingStarted: ...

    async def list_pending_events(self, identity: PlatformRef) -> tuple[PendingEvent, ...]: ...

    async def resolve_event(self, request: ResolveEventRequest, now: datetime) -> EventResolved: ...

    async def expire_due_events(self, now: datetime, *, limit: int) -> int: ...

    async def complete_due_actions(self, now: datetime, *, limit: int) -> CompletionBatch: ...

    async def claim_notifications(
        self, now: datetime, *, limit: int
    ) -> tuple[PendingNotification, ...]: ...

    async def mark_notification_sent(self, outbox_id: uuid.UUID, now: datetime) -> None: ...

    async def mark_notification_failed(
        self, outbox_id: uuid.UUID, now: datetime, error: str
    ) -> None: ...
