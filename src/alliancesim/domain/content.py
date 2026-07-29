from __future__ import annotations

from datetime import timedelta

from alliancesim.domain.mining import MiningRules

STARTER_CHARACTER_NAME = "New Capsuleer"
STARTER_SHIP_NAME = "Pioneer"
STARTER_SHIP_TYPE_ID = "starter-frigate"
STARTER_MINING_MODULE_ID = "civilian-miner"
STARTER_LOCATION_ID = "calm-asteroid-belt"
STARTER_MATERIAL_ID = "raw-ore"

STARTER_MINING_RULES = MiningRules(duration=timedelta(minutes=1), base_yield=100)
