from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from alliancesim.application.models import (
    AllianceCreated,
    AllianceStatus,
    CreateAllianceRequest,
    MiningStarted,
    PlatformRef,
    StartMiningRequest,
)
from alliancesim.application.ports import GameStore
from alliancesim.domain.content import (
    STARTER_LOCATION_ID,
    STARTER_MATERIAL_ID,
    STARTER_MINING_RULES,
)
from alliancesim.domain.identity import AllianceName, Platform
from alliancesim.domain.mining import MiningRules, plan_mining


class GameService:
    def __init__(
        self,
        store: GameStore,
        *,
        clock: Callable[[], datetime] | None = None,
        mining_rules: MiningRules = STARTER_MINING_RULES,
    ) -> None:
        self._store = store
        self._clock = clock or (lambda: datetime.now(UTC))
        self._mining_rules = mining_rules

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
        plan = plan_mining(self._clock(), self._mining_rules)
        return await self._store.start_mining(
            StartMiningRequest(
                identity=PlatformRef(platform, platform_user_id),
                idempotency_key=idempotency_key,
                plan=plan,
                location_id=STARTER_LOCATION_ID,
                material_id=STARTER_MATERIAL_ID,
            )
        )
