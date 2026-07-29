from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class MiningRules:
    duration: timedelta
    base_yield: int
    rules_version: str = "mining-v1"

    def __post_init__(self) -> None:
        if self.duration <= timedelta(0):
            raise ValueError("mining duration must be positive")
        if self.base_yield <= 0:
            raise ValueError("mining yield must be positive")


@dataclass(frozen=True, slots=True)
class MiningPlan:
    started_at: datetime
    finishes_at: datetime
    yield_quantity: int
    rules_version: str


def plan_mining(
    started_at: datetime,
    rules: MiningRules,
    *,
    yield_bonus_basis_points: int = 0,
) -> MiningPlan:
    if started_at.tzinfo is None or started_at.utcoffset() is None:
        raise ValueError("mining start time must be timezone-aware")
    if yield_bonus_basis_points < 0:
        raise ValueError("mining yield bonus cannot be negative")
    normalized_start = started_at.astimezone(UTC)
    quantity = rules.base_yield * (10_000 + yield_bonus_basis_points) // 10_000
    return MiningPlan(
        started_at=normalized_start,
        finishes_at=normalized_start + rules.duration,
        yield_quantity=quantity,
        rules_version=rules.rules_version,
    )
