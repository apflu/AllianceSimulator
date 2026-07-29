from datetime import timedelta

import pytest

from alliancesim.domain.events import (
    EventOptionDefinition,
    EventTemplate,
    ResourceEffect,
    event_template_from_snapshot,
)


def test_event_snapshot_round_trip_preserves_resolvable_content() -> None:
    template = EventTemplate(
        "test-event",
        3,
        "Title",
        "Body",
        (EventOptionDefinition("take", "Take", ResourceEffect("ore", 7)),),
        "take",
        timedelta(hours=1),
    )
    restored = event_template_from_snapshot(template.snapshot())
    assert restored == template


def test_event_rejects_missing_default_option() -> None:
    with pytest.raises(ValueError, match="default"):
        EventTemplate(
            "invalid",
            1,
            "Title",
            "Body",
            (EventOptionDefinition("take", "Take", ResourceEffect("ore", 1)),),
            "missing",
            timedelta(hours=1),
        )
