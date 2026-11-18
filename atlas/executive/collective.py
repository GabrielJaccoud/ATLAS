from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .fractal import MinistryFractal


@dataclass(frozen=True)
class CollectiveInsight:
    insight_id: str
    statement: str
    contributing_ministries: tuple[str, ...]
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    novelty: float = 0.0
    requires_review: bool = False


@dataclass(frozen=True)
class CollectiveState:
    ministry_health: dict[str, float]
    active_research_count: int
    blocked_dependency_count: int
    contradiction_count: int
    proposed_capabilities: tuple[str, ...]
    low_health_ministries: tuple[str, ...]


class CollectiveMind:
    """Integrates ministry self-state without erasing local specialization."""

    def summarize(self, fractals: Iterable[MinistryFractal]) -> CollectiveState:
        items = tuple(fractals)
        health = {f.identity.ministry_id: f.state.normalized_health() for f in items}
        active_research_count = sum(len(f.state.active_research) for f in items)
        blocked_dependency_count = sum(len(f.state.blocked_dependencies) for f in items)
        contradiction_count = sum(len(f.state.unresolved_contradictions) for f in items)
        capabilities = tuple(sorted({
            capability
            for f in items
            for capability in f.state.proposed_capabilities
        }))
        low_health = tuple(sorted(k for k, v in health.items() if v < 0.65))
        return CollectiveState(
            ministry_health=health,
            active_research_count=active_research_count,
            blocked_dependency_count=blocked_dependency_count,
            contradiction_count=contradiction_count,
            proposed_capabilities=capabilities,
            low_health_ministries=low_health,
        )

    def assimilate(self, insights: Iterable[CollectiveInsight]) -> tuple[CollectiveInsight, ...]:
        accepted: list[CollectiveInsight] = []
        for insight in insights:
            if insight.requires_review:
                continue
            if insight.confidence < 0.55:
                continue
            if insight.contradictions and insight.confidence < 0.75:
                continue
            accepted.append(insight)
        return tuple(accepted)
