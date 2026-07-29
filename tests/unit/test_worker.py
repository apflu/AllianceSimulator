import asyncio

from alliancesim.bootstrap.worker import Worker


class CountingPoller:
    def __init__(self) -> None:
        self.calls = 0

    async def poll_once(self) -> int:
        self.calls += 1
        return 0


async def test_worker_can_poll_once() -> None:
    poller = CountingPoller()
    worker = Worker(poller, interval_seconds=0.01)
    assert await worker.run_once() == 0
    assert poller.calls == 1


async def test_idle_worker_stops_cleanly() -> None:
    poller = CountingPoller()
    worker = Worker(poller, interval_seconds=0.01)
    task = asyncio.create_task(worker.run())
    await asyncio.sleep(0)
    worker.stop()
    await asyncio.wait_for(task, timeout=1)
    assert poller.calls >= 1
