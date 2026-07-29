from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

import structlog

from alliancesim.application.models import PendingNotification
from alliancesim.application.ports import GameStore
from alliancesim.domain.identity import Platform

logger = structlog.get_logger()


class NotificationDeliveryError(RuntimeError):
    """A delivery failure whose message is safe to persist and log."""


class NotificationSender(Protocol):
    async def send(self, notification: PendingNotification) -> None: ...


class RoutingNotificationSender:
    def __init__(self, senders: dict[Platform, NotificationSender]) -> None:
        self._senders = dict(senders)

    async def send(self, notification: PendingNotification) -> None:
        sender = self._senders.get(notification.platform)
        if sender is None:
            raise NotificationDeliveryError(
                f"no sender configured for {notification.platform.value}"
            )
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
        for action_id in completions.completed_action_ids:
            logger.info("timed_action_completed", action_id=str(action_id))
        expired_events = await self._store.expire_due_events(now, limit=self._batch_size)
        if expired_events:
            logger.info("alliance_events_expired", count=expired_events)
        notifications = await self._store.claim_notifications(now, limit=self._batch_size)
        for notification in notifications:
            try:
                await self._sender.send(notification)
            except Exception as error:
                detail = (
                    str(error)
                    if isinstance(error, NotificationDeliveryError)
                    else type(error).__name__
                )
                terminal = await self._store.mark_notification_failed(
                    notification.outbox_id, now, detail
                )
                log = logger.error if terminal else logger.warning
                log(
                    "notification_delivery_failed" if terminal else "notification_retry_scheduled",
                    outbox_id=str(notification.outbox_id),
                    platform=notification.platform.value,
                    event_type=notification.event_type,
                    error=detail,
                )
            else:
                await self._store.mark_notification_sent(notification.outbox_id, now)
                logger.info(
                    "notification_sent",
                    outbox_id=str(notification.outbox_id),
                    platform=notification.platform.value,
                    event_type=notification.event_type,
                )
        return completions.count + expired_events + len(notifications)
