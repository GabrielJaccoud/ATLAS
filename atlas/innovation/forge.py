from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HypothesisWorld:
    hypothesis_id: str
    title: str
    source_traditions: tuple[str, ...]
    premises: tuple[str, ...]
    epistemic_status: str
    evidence_refs: tuple[str, ...] = ()
    contrary_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class MechanismCandidate:
    mechanism_id: str
    hypothesis_id: str
    name: str
    description: str
    domains: tuple[str, ...]
    observable_predictions: tuple[str, ...] = ()
    engineering_analogues: tuple[str, ...] = ()
    requires_hypothesis_truth: bool = False


@dataclass(frozen=True)
class TechnologySeed:
    seed_id: str
    name: str
    mechanism_ids: tuple[str, ...]
    purpose: str
    target_ministries: tuple[str, ...]
    novelty: float
    testability: float
    reversibility: float
    evidence_readiness: float
    safety_risk: float
    regulatory_risk: float = 0.0
    claims: tuple[str, ...] = ()
    acceptance_tests: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class MinistryAssessment:
    ministry_id: str
    relevance: float
    expected_value: float
    required_capabilities: tuple[str, ...] = ()
    concerns: tuple[str, ...] = ()


@dataclass(frozen=True)
class InnovationDecision:
    seed_id: str
    status: str
    score: float
    requires_human_approval: bool
    requires_sandbox: bool
    required_reviews: tuple[str, ...]
    reason: str


class HypothesisForge:
    """Turns provisional world-models into testable mechanisms and bounded R&D proposals."""

    def evaluate_seed(
        self,
        seed: TechnologySeed,
        ministry_assessments: tuple[MinistryAssessment, ...] = (),
    ) -> InnovationDecision:
        ministry_value = 0.0
        if ministry_assessments:
            ministry_value = sum(
                x.relevance * x.expected_value for x in ministry_assessments
            ) / len(ministry_assessments)

        score = (
            0.20 * seed.novelty
            + 0.25 * seed.testability
            + 0.20 * seed.reversibility
            + 0.15 * seed.evidence_readiness
            + 0.20 * ministry_value
            - 0.25 * seed.safety_risk
            - 0.20 * seed.regulatory_risk
        )
        score = max(0.0, min(1.0, score))

        reviews = {"epistemic_council", "integration_chamber", "outcomes_observatory"}
        if seed.safety_risk >= 0.4 or seed.regulatory_risk >= 0.4:
            reviews.add("guardian")
            reviews.add("red_team")
        if seed.target_ministries:
            reviews.update(seed.target_ministries)

        approval = (
            seed.safety_risk >= 0.55
            or seed.regulatory_risk >= 0.55
            or "health_wellbeing" in seed.target_ministries
        )

        if seed.testability < 0.25:
            status = "hold"
            reason = "Too weakly testable; formalize discriminant predictions first."
        elif seed.safety_risk >= 0.8 or seed.regulatory_risk >= 0.8:
            status = "review"
            reason = "High safety/regulatory risk requires explicit review before experimentation."
        elif score >= 0.55:
            status = "sandbox"
            reason = "Sufficient expected value and testability for reversible sandbox R&D."
        else:
            status = "research"
            reason = "Promising but needs stronger evidence, reversibility or ministry value."

        return InnovationDecision(
            seed_id=seed.seed_id,
            status=status,
            score=score,
            requires_human_approval=approval,
            requires_sandbox=True,
            required_reviews=tuple(sorted(reviews)),
            reason=reason,
        )
