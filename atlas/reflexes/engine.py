from __future__ import annotations

from dataclasses import dataclass

from atlas.events import EventRecord


@dataclass(frozen=True)
class ReflexRule:
    rule_id: str
    event_type: str
    max_risk: float
    action: str
    reversible_only: bool = True
    require_human_approval: bool = False


@dataclass(frozen=True)
class ReflexDecision:
    rule_id: str
    matched: bool
    action: str | None
    escalate: bool
    reason: str


class ReflexEngine:
    def evaluate(self, event: EventRecord, *, risk: float, reversible: bool, rules: tuple[ReflexRule, ...]) -> tuple[ReflexDecision, ...]:
        out: list[ReflexDecision] = []
        for rule in rules:
            if rule.event_type != event.event_type:
                continue
            if risk > rule.max_risk:
                out.append(ReflexDecision(rule.rule_id, False, None, True, "Risk exceeds threshold."))
            elif rule.reversible_only and not reversible:
                out.append(ReflexDecision(rule.rule_id, False, None, True, "Action is not reversible."))
            elif rule.require_human_approval:
                out.append(ReflexDecision(rule.rule_id, False, None, True, "Human approval required."))
            else:
                out.append(ReflexDecision(rule.rule_id, True, rule.action, False, "Pre-approved reversible reflex."))
        return tuple(out)
