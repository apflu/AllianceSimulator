from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from alliancesim.domain.identity import Platform
from alliancesim.domain.mining import MiningPlan
from alliancesim.domain.training import TrainingPlan


@dataclass(frozen=True, slots=True)
class PlatformRef:
    platform: Platform
    user_id: str


@dataclass(frozen=True, slots=True)
class CreateAllianceRequest:
    identity: PlatformRef
    alliance_name: str
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class AllianceCreated:
    alliance_id: uuid.UUID
    name: str
    created: bool


@dataclass(frozen=True, slots=True)
class InventoryItem:
    material_id: str
    quantity: int


@dataclass(frozen=True, slots=True)
class ActiveAction:
    action_id: uuid.UUID
    action_type: str
    finishes_at: datetime


@dataclass(frozen=True, slots=True)
class AllianceStatus:
    alliance_id: uuid.UUID
    name: str
    character_id: uuid.UUID
    character_name: str
    ship_id: uuid.UUID
    ship_name: str
    inventory: tuple[InventoryItem, ...]
    active_action: ActiveAction | None
    skills: tuple[SkillLevel, ...] = ()


@dataclass(frozen=True, slots=True)
class SkillLevel:
    skill_id: str
    level: int


@dataclass(frozen=True, slots=True)
class StartMiningRequest:
    identity: PlatformRef
    idempotency_key: str
    plan: MiningPlan
    location_id: str
    material_id: str


@dataclass(frozen=True, slots=True)
class MiningStarted:
    action_id: uuid.UUID
    finishes_at: datetime
    yield_quantity: int
    created: bool


@dataclass(frozen=True, slots=True)
class StartTrainingRequest:
    identity: PlatformRef
    idempotency_key: str
    plan: TrainingPlan


@dataclass(frozen=True, slots=True)
class TrainingStarted:
    action_id: uuid.UUID
    skill_id: str
    target_level: int
    finishes_at: datetime
    created: bool


@dataclass(frozen=True, slots=True)
class PendingNotification:
    outbox_id: uuid.UUID
    platform: Platform
    platform_user_id: str
    event_type: str
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class CompletionBatch:
    completed_action_ids: tuple[uuid.UUID, ...]

    @property
    def count(self) -> int:
        return len(self.completed_action_ids)
