from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _clip(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class GoalState:
    goal_id: str
    description: str
    progress: float = 0.0
    priority: float = 0.5
    blocked: bool = False

    def normalized(self) -> "GoalState":
        return GoalState(
            goal_id=self.goal_id,
            description=self.description,
            progress=_clip(self.progress),
            priority=_clip(self.priority),
            blocked=self.blocked,
        )


@dataclass(frozen=True)
class ModuleHealth:
    module: str
    healthy: bool = True
    confidence: float = 1.0
    error_count: int = 0
    latency_ms: float | None = None
    note: str | None = None

    def score(self) -> float:
        base = _clip(self.confidence)
        if not self.healthy:
            base *= 0.35
        base *= 1.0 / (1.0 + max(0, self.error_count) * 0.15)
        return _clip(base)


@dataclass(frozen=True)
class SelfAssessment:
    confidence: float
    uncertainty: float
    evidence_coverage: float
    goal_alignment: float
    contradiction_load: float
    novelty_load: float

    def normalized(self) -> "SelfAssessment":
        return SelfAssessment(
            confidence=_clip(self.confidence),
            uncertainty=_clip(self.uncertainty),
            evidence_coverage=_clip(self.evidence_coverage),
            goal_alignment=_clip(self.goal_alignment),
            contradiction_load=_clip(self.contradiction_load),
            novelty_load=_clip(self.novelty_load),
        )


@dataclass(frozen=True)
class AwarenessSnapshot:
    goals: tuple[GoalState, ...] = ()
    modules: tuple[ModuleHealth, ...] = ()
    assessment: SelfAssessment = field(
        default_factory=lambda: SelfAssessment(0.5, 0.5, 0.5, 0.5, 0.0, 0.0)
    )
    active_hypotheses: tuple[str, ...] = ()
    active_tests: tuple[str, ...] = ()
    recent_errors: tuple[str, ...] = ()
    known_unknowns: tuple[str, ...] = ()
    context_tokens_used: int | None = None
    context_tokens_budget: int | None = None
    checkpoint_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def context_pressure(self) -> float:
        if not self.context_tokens_budget or self.context_tokens_used is None:
            return 0.0
        if self.context_tokens_budget <= 0:
            return 1.0
        return _clip(self.context_tokens_used / self.context_tokens_budget)
