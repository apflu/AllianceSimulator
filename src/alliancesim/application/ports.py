from __future__ import annotations

from typing import Protocol


class DatabaseProbe(Protocol):
    async def probe(self) -> bool: ...


class WorkPoller(Protocol):
    async def poll_once(self) -> int: ...
