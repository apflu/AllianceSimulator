from __future__ import annotations

import uuid
from datetime import UTC, datetime

from alliancesim.application.models import (
    AllianceCreated,
    AllianceStatus,
    CompletionBatch,
    CreateAllianceRequest,
    MiningStarted,
    PendingNotification,
    PlatformRef,
    StartMiningRequest,
)
from alliancesim.application.notifications import ActionWorkerPoller
from alliancesim.domain.identity import Platform

NOW = datetime(2026, 7, 30, tzinfo=UTC)


class WorkerStore:
    def __init__(self) -> None:
        self.sent: list[uuid.UUID] = []
        self.failed: list[uuid.UUID] = []

    async def complete_due_actions(self, now: datetime, *, limit: int) -> CompletionBatch:
        assert now == NOW
        assert limit == 25
        return CompletionBatch((uuid.UUID(int=1),))

    async def claim_notifications(
        self, now: datetime, *, limit: int
    ) -> tuple[PendingNotification, ...]:
        del now, limit
        return (
            PendingNotification(
                uuid.UUID(int=2),
                Platform.DISCORD,
                "42",
                "mining_completed",
                {"quantity": 100, "material_id": "raw-ore"},
            ),
        )

    async def mark_notification_sent(self, outbox_id: uuid.UUID, now: datetime) -> None:
        del now
        self.sent.append(outbox_id)

    async def mark_notification_failed(
        self, outbox_id: uuid.UUID, now: datetime, error: str
    ) -> None:
        del now, error
        self.failed.append(outbox_id)

    async def create_alliance(self, request: CreateAllianceRequest) -> AllianceCreated:
        raise AssertionError(request)

    async def get_status(self, identity: PlatformRef) -> AllianceStatus:
        raise AssertionError(identity)

    async def start_mining(self, request: StartMiningRequest) -> MiningStarted:
        raise AssertionError(request)


class Sender:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.notifications: list[PendingNotification] = []

    async def send(self, notification: PendingNotification) -> None:
        self.notifications.append(notification)
        if self.fail:
            raise RuntimeError("network unavailable")


async def test_worker_completes_actions_and_marks_notifications_sent() -> None:
    store = WorkerStore()
    sender = Sender()
    poller = ActionWorkerPoller(store, sender, clock=lambda: NOW)
    assert await poller.poll_once() == 2
    assert store.sent == [uuid.UUID(int=2)]
    assert store.failed == []


async def test_worker_retries_failed_notification() -> None:
    store = WorkerStore()
    poller = ActionWorkerPoller(store, Sender(fail=True), clock=lambda: NOW)
    assert await poller.poll_once() == 2
    assert store.sent == []
    assert store.failed == [uuid.UUID(int=2)]
