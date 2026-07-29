from __future__ import annotations

from datetime import timedelta

from alliancesim.domain.mining import MiningRules
from alliancesim.domain.training import SkillRules

STARTER_CHARACTER_NAME = "New Capsuleer"
STARTER_SHIP_NAME = "Pioneer"
STARTER_SHIP_TYPE_ID = "starter-frigate"
STARTER_MINING_MODULE_ID = "civilian-miner"
STARTER_LOCATION_ID = "calm-asteroid-belt"
STARTER_MATERIAL_ID = "raw-ore"

STARTER_MINING_RULES = MiningRules(duration=timedelta(minutes=1), base_yield=100)

MINING_OPERATIONS_SKILL_ID = "mining-operations"
MINING_OPERATIONS_RULES = SkillRules(
    skill_id=MINING_OPERATIONS_SKILL_ID,
    duration_per_level=timedelta(minutes=2),
    max_level=5,
    bonus_basis_points_per_level=1_000,
)
