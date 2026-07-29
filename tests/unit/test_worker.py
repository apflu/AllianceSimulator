import asyncio

from alliancesim.bootstrap.worker import Worker


class CountingPoller:
    def __init__(self) -> None:
        self.calls = 0

    async def poll_once(self) -> int:
        self.calls += 1
        return 0


class FlakyPoller:
    def __init__(self) -> None:
        self.calls = 0
        self.recovered = asyncio.Event()

    async def poll_once(self) -> int:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("temporary database outage")
        self.recovered.set()
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


async def test_worker_continues_after_one_poll_failure() -> None:
    poller = FlakyPoller()
    worker = Worker(poller, interval_seconds=0.001)
    task = asyncio.create_task(worker.run())
    await asyncio.wait_for(poller.recovered.wait(), timeout=1)
    worker.stop()
    await asyncio.wait_for(task, timeout=1)
    assert poller.calls >= 2
