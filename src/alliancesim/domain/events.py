from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import cast


@dataclass(frozen=True, slots=True)
class ResourceEffect:
    material_id: str
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("event resource quantity must be positive")


@dataclass(frozen=True, slots=True)
class EventOptionDefinition:
    option_id: str
    label: str
    effect: ResourceEffect


@dataclass(frozen=True, slots=True)
class EventTemplate:
    template_id: str
    version: int
    title: str
    body: str
    options: tuple[EventOptionDefinition, ...]
    default_option_id: str
    timeout: timedelta

    def __post_init__(self) -> None:
        if self.timeout <= timedelta(0):
            raise ValueError("event timeout must be positive")
        option_ids = {option.option_id for option in self.options}
        if len(option_ids) != len(self.options):
            raise ValueError("event option ids must be unique")
        if self.default_option_id not in option_ids:
            raise ValueError("default event option does not exist")

    def option(self, option_id: str) -> EventOptionDefinition:
        for option in self.options:
            if option.option_id == option_id:
                return option
        raise ValueError(f"unknown event option: {option_id}")

    def snapshot(self) -> dict[str, object]:
        return {
            "template_id": self.template_id,
            "version": self.version,
            "title": self.title,
            "body": self.body,
            "default_option_id": self.default_option_id,
            "timeout_seconds": int(self.timeout.total_seconds()),
            "options": [
                {
                    "option_id": option.option_id,
                    "label": option.label,
                    "effect": {
                        "material_id": option.effect.material_id,
                        "quantity": option.effect.quantity,
                    },
                }
                for option in self.options
            ],
        }


def event_template_from_snapshot(snapshot: dict[str, object]) -> EventTemplate:
    raw_options = cast(list[dict[str, object]], snapshot["options"])
    options: list[EventOptionDefinition] = []
    for raw_option in raw_options:
        raw_effect = cast(dict[str, object], raw_option["effect"])
        options.append(
            EventOptionDefinition(
                option_id=str(raw_option["option_id"]),
                label=str(raw_option["label"]),
                effect=ResourceEffect(
                    material_id=str(raw_effect["material_id"]),
                    quantity=int(cast(int, raw_effect["quantity"])),
                ),
            )
        )
    return EventTemplate(
        template_id=str(snapshot["template_id"]),
        version=int(cast(int, snapshot["version"])),
        title=str(snapshot["title"]),
        body=str(snapshot["body"]),
        options=tuple(options),
        default_option_id=str(snapshot["default_option_id"]),
        timeout=timedelta(seconds=int(cast(int, snapshot["timeout_seconds"]))),
    )
