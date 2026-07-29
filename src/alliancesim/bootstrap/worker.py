from __future__ import annotations

import asyncio
from contextlib import suppress

import structlog

from alliancesim.adapters.outbound.notifications.discord import (
    DiscordNotificationSender,
    UnavailableNotificationSender,
)
from alliancesim.adapters.outbound.persistence.database import Database
from alliancesim.adapters.outbound.persistence.game_store import SqlAlchemyGameStore
from alliancesim.application.notifications import ActionWorkerPoller, NotificationSender
from alliancesim.application.ports import WorkPoller
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings

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
            processed = await self.run_once()
            if processed:
                logger.info("worker_poll_completed", processed=processed)
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
    sender: NotificationSender = (
        DiscordNotificationSender(settings.discord_token.get_secret_value())
        if settings.discord_token is not None
        else UnavailableNotificationSender()
    )
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
