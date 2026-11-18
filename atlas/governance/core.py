from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class GovernanceBody(str, Enum):
    ASAS = "asas"
    GUARDIAN = "guardian"
    EPISTEMIC_COUNCIL = "epistemic_council"
    MNEMOSYNE = "mnemosyne"
    OPERATIONS_GOVERNOR = "operations_governor"
    OUTCOMES_OBSERVATORY = "outcomes_observatory"
    RED_TEAM = "red_team"
    INTEGRATION_CHAMBER = "integration_chamber"
    SUPPORT_CELL = "support_cell"


@dataclass(frozen=True)
class GovernanceRequest:
    request_id: str
    source: str
    purpose: str
    categories: tuple[str, ...]
    risk: float = 0.0
    external_action: bool = False
    irreversible: bool = False
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class GovernanceResponse:
    request_id: str
    routed_to: tuple[GovernanceBody, ...]
    human_approval_required: bool
    rationale: tuple[str, ...]


class GovernanceNetwork:
    """Routes internal support/governance needs without creating competing ATLAS identities."""

    def route(self, request: GovernanceRequest) -> GovernanceResponse:
        targets: list[GovernanceBody] = [GovernanceBody.ASAS]
        reasons: list[str] = ["ASAS coordinates context and cross-system routing."]

        cats = set(request.categories)

        if cats & {"identity", "permissions", "security", "constitution", "consent"}:
            targets.append(GovernanceBody.GUARDIAN)
            reasons.append("Guardian protects identity, permissions, consent and invariants.")

        if cats & {"evidence", "claim", "uncertainty", "contradiction", "hypothesis"}:
            targets.append(GovernanceBody.EPISTEMIC_COUNCIL)
            reasons.append("Epistemic Council governs evidence status and uncertainty.")

        if cats & {"memory", "context", "history", "versioning", "duplicate"}:
            targets.append(GovernanceBody.MNEMOSYNE)
            reasons.append("Mnemosyne curates memory, continuity and retrieval.")

        if cats & {"health", "cost", "latency", "queue", "resource", "capacity"}:
            targets.append(GovernanceBody.OPERATIONS_GOVERNOR)
            reasons.append("Operations Governor manages resources and operational health.")

        if cats & {"outcome", "calibration", "regression", "forecast_error", "learning"}:
            targets.append(GovernanceBody.OUTCOMES_OBSERVATORY)
            reasons.append("Outcomes Observatory compares predictions and results.")

        if cats & {"challenge", "red_team", "failure_mode", "adversarial_review"}:
            targets.append(GovernanceBody.RED_TEAM)
            reasons.append("Red Team searches for failure modes and overconfidence.")

        if cats & {"conflict", "cross_ministry", "synthesis", "dependency"}:
            targets.append(GovernanceBody.INTEGRATION_CHAMBER)
            reasons.append("Integration Chamber resolves cross-ministry conflicts.")

        if cats & {"repair", "maintenance", "tooling", "build", "upgrade", "capability_gap", "support"}:
            targets.append(GovernanceBody.SUPPORT_CELL)
            reasons.append("Support Cell repairs, maintains and helps build new capabilities.")

        targets = list(dict.fromkeys(targets))

        approval = (
            request.risk >= 0.70
            or request.external_action
            or request.irreversible
            or "constitution" in cats
            or "permissions" in cats
        )

        return GovernanceResponse(
            request_id=request.request_id,
            routed_to=tuple(targets),
            human_approval_required=approval,
            rationale=tuple(reasons),
        )
