from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FailureSignature:
    failure_id: str
    component: str
    symptoms: tuple[str, ...]
    root_cause: str | None
    resolution: tuple[str, ...]
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class FailureMatch:
    failure_id: str
    score: float
    resolution: tuple[str, ...]


class FailureMemory:
    def __init__(self) -> None:
        self._items: dict[str, FailureSignature] = {}

    def remember(self, signature: FailureSignature) -> None:
        self._items[signature.failure_id] = signature

    def find_similar(self, *, component: str, symptoms: tuple[str, ...], tags: tuple[str, ...] = ()) -> tuple[FailureMatch, ...]:
        symptom_set, tag_set = set(symptoms), set(tags)
        matches: list[FailureMatch] = []
        for item in self._items.values():
            score = 0.5 if item.component == component else 0.0
            union = symptom_set.union(item.symptoms)
            if union:
                score += 0.35 * len(symptom_set.intersection(item.symptoms)) / len(union)
            union_tags = tag_set.union(item.tags)
            if union_tags:
                score += 0.15 * len(tag_set.intersection(item.tags)) / len(union_tags)
            if score > 0:
                matches.append(FailureMatch(item.failure_id, min(1.0, score), item.resolution))
        return tuple(sorted(matches, key=lambda x: (-x.score, x.failure_id)))
