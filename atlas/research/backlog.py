from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ResearchStatus(str, Enum):
    IDEA = "idea"
    FORMALIZING = "formalizing"
    TESTING = "testing"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETE = "complete"


@dataclass(frozen=True)
class ResearchItem:
    item_id: str
    ministry_id: str
    question: str
    status: ResearchStatus
    priority: float = 0.5
    evidence_refs: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    next_experiment: str | None = None


class ResearchBacklog:
    def __init__(self) -> None:
        self._items: dict[str, ResearchItem] = {}

    def add(self, item: ResearchItem) -> None:
        self._items[item.item_id] = item

    def by_ministry(self, ministry_id: str) -> tuple[ResearchItem, ...]:
        return tuple(sorted(
            (x for x in self._items.values() if x.ministry_id == ministry_id),
            key=lambda x: (-x.priority, x.item_id),
        ))

    def blocked(self) -> tuple[ResearchItem, ...]:
        return tuple(x for x in self._items.values() if x.status == ResearchStatus.BLOCKED)
