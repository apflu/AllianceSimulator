from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ViewField:
    name: str
    value: str
    inline: bool = False


@dataclass(frozen=True, slots=True)
class ViewAction:
    action_id: str
    label: str


@dataclass(frozen=True, slots=True)
class MessageView:
    title: str
    body: str
    fields: tuple[ViewField, ...] = ()
    actions: tuple[ViewAction, ...] = ()
    is_error: bool = False

    def as_plain_text(self) -> str:
        sections = [f"**{self.title}**", self.body]
        sections.extend(f"**{field.name}**\n{field.value}" for field in self.fields)
        return "\n\n".join(section for section in sections if section)
