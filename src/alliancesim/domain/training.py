from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta


@dataclass(frozen=True, slots=True)
class SkillRules:
    skill_id: str
    duration_per_level: timedelta
    max_level: int
    bonus_basis_points_per_level: int
    rules_version: str = "skills-v1"

    def __post_init__(self) -> None:
        if self.duration_per_level <= timedelta(0):
            raise ValueError("training duration must be positive")
        if self.max_level <= 0:
            raise ValueError("maximum skill level must be positive")
        if self.bonus_basis_points_per_level < 0:
            raise ValueError("skill bonus cannot be negative")


@dataclass(frozen=True, slots=True)
class TrainingPlan:
    skill_id: str
    target_level: int
    started_at: datetime
    finishes_at: datetime
    rules_version: str


def plan_training(started_at: datetime, current_level: int, rules: SkillRules) -> TrainingPlan:
    if started_at.tzinfo is None or started_at.utcoffset() is None:
        raise ValueError("training start time must be timezone-aware")
    if not 0 <= current_level < rules.max_level:
        raise ValueError("skill is already at maximum level")
    target_level = current_level + 1
    normalized_start = started_at.astimezone(UTC)
    return TrainingPlan(
        skill_id=rules.skill_id,
        target_level=target_level,
        started_at=normalized_start,
        finishes_at=normalized_start + rules.duration_per_level * target_level,
        rules_version=rules.rules_version,
    )
