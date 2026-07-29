import pytest
from hypothesis import given
from hypothesis import strategies as st

from alliancesim.domain.identity import AllianceName


def test_alliance_name_is_trimmed() -> None:
    assert AllianceName("  Brave Collective  ").value == "Brave Collective"


@given(
    st.text(alphabet="abc123", max_size=1) | st.text(alphabet="abc123", min_size=81, max_size=120)
)
def test_invalid_alliance_name_lengths_are_rejected(value: str) -> None:
    with pytest.raises(ValueError, match="between 2 and 80"):
        AllianceName(value)
