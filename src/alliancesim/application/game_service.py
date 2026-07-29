from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from alliancesim.application.models import (
    AllianceCreated,
    AllianceStatus,
    CreateAllianceRequest,
    EventResolved,
    MiningStarted,
    PendingEvent,
    PlatformRef,
    ResolveEventRequest,
    StartMiningRequest,
    StartTrainingRequest,
    TrainingStarted,
)
from alliancesim.application.ports import GameStore
from alliancesim.domain.content import (
    MINING_OPERATIONS_RULES,
    STARTER_LOCATION_ID,
    STARTER_MATERIAL_ID,
    STARTER_MINING_RULES,
)
from alliancesim.domain.identity import AllianceName, Platform
from alliancesim.domain.mining import MiningRules, plan_mining
from alliancesim.domain.training import SkillRules, plan_training


class GameService:
    def __init__(
        self,
        store: GameStore,
        *,
        clock: Callable[[], datetime] | None = None,
        mining_rules: MiningRules = STARTER_MINING_RULES,
        skill_rules: SkillRules = MINING_OPERATIONS_RULES,
    ) -> None:
        self._store = store
        self._clock = clock or (lambda: datetime.now(UTC))
        self._mining_rules = mining_rules
        self._skill_rules = skill_rules

    async def create_alliance(
        self,
        platform: Platform,
        platform_user_id: str,
        alliance_name: str,
        idempotency_key: str,
    ) -> AllianceCreated:
        name = AllianceName(alliance_name)
        return await self._store.create_alliance(
            CreateAllianceRequest(
                identity=PlatformRef(platform, platform_user_id),
                alliance_name=name.value,
                idempotency_key=idempotency_key,
            )
        )

    async def get_status(self, platform: Platform, platform_user_id: str) -> AllianceStatus:
        return await self._store.get_status(PlatformRef(platform, platform_user_id))

    async def start_mining(
        self,
        platform: Platform,
        platform_user_id: str,
        idempotency_key: str,
    ) -> MiningStarted:
        skill_level = await self._store.get_skill_level(
            PlatformRef(platform, platform_user_id), self._skill_rules.skill_id
        )
        plan = plan_mining(
            self._clock(),
            self._mining_rules,
            yield_bonus_basis_points=(skill_level * self._skill_rules.bonus_basis_points_per_level),
        )
        return await self._store.start_mining(
            StartMiningRequest(
                identity=PlatformRef(platform, platform_user_id),
                idempotency_key=idempotency_key,
                plan=plan,
                location_id=STARTER_LOCATION_ID,
                material_id=STARTER_MATERIAL_ID,
            )
        )

    async def start_training(
        self,
        platform: Platform,
        platform_user_id: str,
        idempotency_key: str,
    ) -> TrainingStarted:
        identity = PlatformRef(platform, platform_user_id)
        current_level = await self._store.get_skill_level(identity, self._skill_rules.skill_id)
        plan = plan_training(self._clock(), current_level, self._skill_rules)
        return await self._store.start_training(
            StartTrainingRequest(identity=identity, idempotency_key=idempotency_key, plan=plan)
        )

    async def list_pending_events(
        self, platform: Platform, platform_user_id: str
    ) -> tuple[PendingEvent, ...]:
        return await self._store.list_pending_events(PlatformRef(platform, platform_user_id))

    async def resolve_event(
        self,
        platform: Platform,
        platform_user_id: str,
        occurrence_id: uuid.UUID,
        option_id: str,
        idempotency_key: str,
    ) -> EventResolved:
        return await self._store.resolve_event(
            ResolveEventRequest(
                identity=PlatformRef(platform, platform_user_id),
                occurrence_id=occurrence_id,
                option_id=option_id,
                idempotency_key=idempotency_key,
            ),
            self._clock(),
        )
