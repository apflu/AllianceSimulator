from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from alliancesim.application.models import PendingNotification
from alliancesim.application.ports import GameStore
from alliancesim.domain.identity import Platform


class NotificationSender(Protocol):
    async def send(self, notification: PendingNotification) -> None: ...


class RoutingNotificationSender:
    def __init__(self, senders: dict[Platform, NotificationSender]) -> None:
        self._senders = dict(senders)

    async def send(self, notification: PendingNotification) -> None:
        sender = self._senders.get(notification.platform)
        if sender is None:
            raise RuntimeError(f"no sender configured for {notification.platform}")
        await sender.send(notification)


class ActionWorkerPoller:
    def __init__(
        self,
        store: GameStore,
        sender: NotificationSender,
        *,
        clock: Callable[[], datetime] | None = None,
        batch_size: int = 25,
    ) -> None:
        self._store = store
        self._sender = sender
        self._clock = clock or (lambda: datetime.now(UTC))
        self._batch_size = batch_size

    async def poll_once(self) -> int:
        now = self._clock()
        completions = await self._store.complete_due_actions(now, limit=self._batch_size)
        notifications = await self._store.claim_notifications(now, limit=self._batch_size)
        for notification in notifications:
            try:
                await self._sender.send(notification)
            except Exception as error:
                await self._store.mark_notification_failed(
                    notification.outbox_id, now, f"{type(error).__name__}: {error}"
                )
            else:
                await self._store.mark_notification_sent(notification.outbox_id, now)
        return completions.count + len(notifications)
