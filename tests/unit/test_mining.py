from datetime import UTC, datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from alliancesim.domain.mining import MiningRules, plan_mining


def test_mining_plan_freezes_deadline_and_yield() -> None:
    start = datetime(2026, 7, 30, tzinfo=UTC)
    rules = MiningRules(duration=timedelta(minutes=5), base_yield=100)
    plan = plan_mining(start, rules, yield_bonus_basis_points=2_500)
    assert plan.finishes_at == start + timedelta(minutes=5)
    assert plan.yield_quantity == 125
    assert plan.rules_version == "mining-v1"


def test_mining_rejects_naive_start_time() -> None:
    rules = MiningRules(duration=timedelta(minutes=1), base_yield=100)
    with pytest.raises(ValueError, match="timezone-aware"):
        plan_mining(datetime(2026, 7, 30), rules)


@given(st.integers(min_value=1, max_value=1_000_000), st.integers(min_value=0, max_value=50_000))
def test_mining_yield_is_positive_integer(base_yield: int, bonus: int) -> None:
    plan = plan_mining(
        datetime(2026, 7, 30, tzinfo=UTC),
        MiningRules(duration=timedelta(seconds=1), base_yield=base_yield),
        yield_bonus_basis_points=bonus,
    )
    assert isinstance(plan.yield_quantity, int)
    assert plan.yield_quantity >= base_yield
