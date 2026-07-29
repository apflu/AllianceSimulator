from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Platform(StrEnum):
    DISCORD = "discord"
    TELEGRAM = "telegram"


@dataclass(frozen=True, slots=True)
class AllianceName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not 2 <= len(normalized) <= 80:
            raise ValueError("alliance name must contain between 2 and 80 characters")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
