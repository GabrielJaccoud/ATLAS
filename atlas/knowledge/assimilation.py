from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeCandidate:
    candidate_id: str
    statement: str
    source_ministry: str
    epistemic_type: str
    confidence: float
    evidence_refs: tuple[str, ...] = ()
    contrary_refs: tuple[str, ...] = ()
    replication_count: int = 0
    requires_human_review: bool = False
    global_impact: float = 0.0


@dataclass(frozen=True)
class AssimilationDecision:
    candidate_id: str
    status: str
    reason: str
    confidence: float


class GlobalKnowledgeGate:
    """Prevents local ministry outputs from silently becoming global truth."""

    VALID_TYPES = {
        "observation",
        "inference",
        "model",
        "hypothesis",
        "experience",
        "tradition",
        "simulation",
        "theorem",
    }

    def evaluate(self, candidate: KnowledgeCandidate) -> AssimilationDecision:
        if candidate.epistemic_type not in self.VALID_TYPES:
            return AssimilationDecision(
                candidate.candidate_id,
                "reject",
                "Unknown epistemic type.",
                candidate.confidence,
            )

        if candidate.requires_human_review:
            return AssimilationDecision(
                candidate.candidate_id,
                "review",
                "Explicit human review required.",
                candidate.confidence,
            )

        if candidate.epistemic_type in {"hypothesis", "experience", "tradition", "simulation"}:
            return AssimilationDecision(
                candidate.candidate_id,
                "assimilate_labeled",
                "May enter global memory only with epistemic label preserved.",
                candidate.confidence,
            )

        if candidate.confidence < 0.55:
            return AssimilationDecision(
                candidate.candidate_id,
                "hold",
                "Confidence below assimilation threshold.",
                candidate.confidence,
            )

        if candidate.contrary_refs and candidate.confidence < 0.75:
            return AssimilationDecision(
                candidate.candidate_id,
                "hold",
                "Material contrary evidence remains unresolved.",
                candidate.confidence,
            )

        if candidate.global_impact >= 0.8 and candidate.replication_count < 1:
            return AssimilationDecision(
                candidate.candidate_id,
                "review",
                "High-impact claim needs replication or explicit review.",
                candidate.confidence,
            )

        return AssimilationDecision(
            candidate.candidate_id,
            "assimilate",
            "Meets current global assimilation criteria.",
            candidate.confidence,
        )
