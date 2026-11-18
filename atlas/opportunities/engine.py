from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Opportunity:
    opportunity_id: str
    title: str
    domains: tuple[str, ...]
    requirements: tuple[str, ...]
    value_score: float
    deadline_urgency: float = 0.0
    source_ref: str | None = None


@dataclass(frozen=True)
class OpportunityMatch:
    opportunity_id: str
    target_id: str
    score: float
    reasons: tuple[str, ...]


class OpportunityEngine:
    def match(self, opportunity: Opportunity, *, target_id: str, target_domains: tuple[str, ...], target_capabilities: tuple[str, ...]) -> OpportunityMatch:
        domain_overlap = set(opportunity.domains).intersection(target_domains)
        requirement_overlap = set(opportunity.requirements).intersection(target_capabilities)
        domain_score = len(domain_overlap) / max(1, len(set(opportunity.domains)))
        requirement_score = len(requirement_overlap) / max(1, len(set(opportunity.requirements)))
        score = min(1.0, 0.35 * domain_score + 0.35 * requirement_score + 0.2 * opportunity.value_score + 0.1 * opportunity.deadline_urgency)
        reasons = tuple([
            *(f"domain:{x}" for x in sorted(domain_overlap)),
            *(f"capability:{x}" for x in sorted(requirement_overlap)),
        ])
        return OpportunityMatch(opportunity.opportunity_id, target_id, score, reasons)
