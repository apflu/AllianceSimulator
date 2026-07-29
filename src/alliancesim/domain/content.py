from __future__ import annotations

from datetime import timedelta

from alliancesim.domain.events import EventOptionDefinition, EventTemplate, ResourceEffect
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

ORE_DISCOVERY_EVENT = EventTemplate(
    template_id="ore-discovery",
    version=1,
    title="异常矿石样本",
    body="采矿队在矿带中发现了一批成分异常的样本。联盟需要决定如何处置。",
    options=(
        EventOptionDefinition(
            option_id="refine",
            label="立即精炼",
            effect=ResourceEffect(material_id=STARTER_MATERIAL_ID, quantity=50),
        ),
        EventOptionDefinition(
            option_id="analyze",
            label="交给研究团队",
            effect=ResourceEffect(material_id="research-data", quantity=1),
        ),
    ),
    default_option_id="refine",
    timeout=timedelta(hours=24),
)
