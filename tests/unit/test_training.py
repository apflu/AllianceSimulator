from datetime import UTC, datetime, timedelta

import pytest

from alliancesim.domain.training import SkillRules, plan_training


def test_training_duration_scales_with_target_level() -> None:
    rules = SkillRules("mining", timedelta(minutes=2), 5, 1_000)
    start = datetime(2026, 7, 30, tzinfo=UTC)
    first = plan_training(start, 0, rules)
    third = plan_training(start, 2, rules)
    assert first.target_level == 1
    assert first.finishes_at == start + timedelta(minutes=2)
    assert third.target_level == 3
    assert third.finishes_at == start + timedelta(minutes=6)


def test_training_rejects_max_level() -> None:
    rules = SkillRules("mining", timedelta(minutes=2), 5, 1_000)
    with pytest.raises(ValueError, match="maximum"):
        plan_training(datetime(2026, 7, 30, tzinfo=UTC), 5, rules)
