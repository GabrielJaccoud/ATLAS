from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CouncilCadence(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    PERIODIC = "periodic"
    CRISIS = "crisis"


@dataclass(frozen=True)
class CouncilSession:
    session_id: str
    cadence: CouncilCadence
    agenda: tuple[str, ...]
    required_bodies: tuple[str, ...]


class CouncilScheduler:
    DEFAULT_AGENDAS = {
        CouncilCadence.DAILY: (
            "discoveries", "anomalies", "blockers", "cross_ministry_requests", "urgent_opportunities"
        ),
        CouncilCadence.WEEKLY: (
            "belief_changes", "contradictions", "cross_domain_patterns", "new_hypotheses", "next_tests"
        ),
        CouncilCadence.PERIODIC: (
            "system_identity", "knowledge_gain", "hypothesis_weights", "architecture_changes", "capability_gaps"
        ),
        CouncilCadence.CRISIS: (
            "incident_scope", "containment", "evidence_conflict", "recovery", "human_decision"
        ),
    }

    def create(self, session_id: str, cadence: CouncilCadence) -> CouncilSession:
        required = ("asas", "integration_chamber", "epistemic_council", "outcomes_observatory")
        if cadence == CouncilCadence.CRISIS:
            required = required + ("guardian", "red_team", "support_cell")
        return CouncilSession(session_id, cadence, self.DEFAULT_AGENDAS[cadence], required)
