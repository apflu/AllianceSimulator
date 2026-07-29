from __future__ import annotations

import asyncio
from contextlib import suppress

import structlog

from alliancesim.application.ports import WorkPoller
from alliancesim.bootstrap.logging import configure_logging
from alliancesim.bootstrap.settings import get_settings

logger = structlog.get_logger()


class EmptyPoller:
    async def poll_once(self) -> int:
        return 0


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
    worker = Worker(EmptyPoller(), settings.worker_poll_interval_seconds)
    try:
        await worker.run()
    except asyncio.CancelledError:
        worker.stop()
        raise


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(run_worker())


if __name__ == "__main__":
    main()
