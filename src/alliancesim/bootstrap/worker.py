from __future__ import annotations

import asyncio
from contextlib import suppress
from time import monotonic

import structlog

from alliancesim.adapters.outbound.notifications.discord import (
    DiscordNotificationSender,
)
from alliancesim.adapters.outbound.notifications.telegram import TelegramNotificationSender
from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.application.notifications import (
    ActionWorkerPoller,
    NotificationSender,
    RoutingNotificationSender,
)
from alliancesim.application.ports import WorkPoller
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings
from alliancesim.domain.identity import Platform

logger = structlog.get_logger()


class Worker:
    def __init__(self, poller: WorkPoller, interval_seconds: float) -> None:
        self._poller = poller
        self._interval_seconds = interval_seconds
        self._stop = asyncio.Event()

    async def run_once(self) -> int:
        return await self._poller.poll_once()

    async def run(self) -> None:
        logger.info("worker_started", poll_interval_seconds=self._interval_seconds)
        while not self._stop.is_set():
            started = monotonic()
            try:
                processed = await self.run_once()
            except asyncio.CancelledError:
                raise
            except Exception as error:
                logger.error("worker_poll_failed", error_type=type(error).__name__)
            else:
                if processed:
                    logger.info(
                        "worker_poll_completed",
                        processed=processed,
                        duration_ms=round((monotonic() - started) * 1000, 3),
                    )
            with suppress(TimeoutError):
                await asyncio.wait_for(self._stop.wait(), timeout=self._interval_seconds)
        logger.info("worker_stopped")

    def stop(self) -> None:
        self._stop.set()


async def run_worker() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    database = Database(settings.database_url)
    store = SqlAlchemyGameStore(database.sessions)
    senders: dict[Platform, NotificationSender] = {}
    proxy_url = settings.proxy_url.get_secret_value() if settings.proxy_url is not None else None
    if settings.discord_token is not None:
        senders[Platform.DISCORD] = DiscordNotificationSender(
            settings.discord_token.get_secret_value(), proxy_url=proxy_url
        )
    if settings.telegram_token is not None:
        senders[Platform.TELEGRAM] = TelegramNotificationSender(
            settings.telegram_token.get_secret_value(),
            proxy_url=proxy_url,
        )
    sender = RoutingNotificationSender(senders)
    worker = Worker(
        ActionWorkerPoller(store, sender),
        settings.worker_poll_interval_seconds,
    )
    try:
        await worker.run()
    except asyncio.CancelledError:
        worker.stop()
        raise
    finally:
        await database.close()


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(run_worker())


if __name__ == "__main__":
    main()
