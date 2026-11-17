from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from typing import Any

from .models import AwarenessSnapshot


def _mean(values: list[float], default: float = 1.0) -> float:
    return sum(values) / len(values) if values else default


class AwarenessEngine:
    """Operational self-awareness for ATLAS.

    This module models self-state, uncertainty, health, goal alignment, drift,
    checkpoints and intervention policy. It does not claim subjective or
    phenomenal consciousness.
    """

    def system_health(self, snapshot: AwarenessSnapshot) -> float:
        return _mean([m.score() for m in snapshot.modules])

    def blocked_goal_pressure(self, snapshot: AwarenessSnapshot) -> float:
        if not snapshot.goals:
            return 0.0
        total_weight = sum(max(0.01, g.normalized().priority) for g in snapshot.goals)
        blocked = sum(
            max(0.01, g.normalized().priority)
            for g in snapshot.goals
            if g.blocked
        )
        return blocked / total_weight if total_weight else 0.0

    def awareness_score(self, snapshot: AwarenessSnapshot) -> float:
        a = snapshot.assessment.normalized()
        health = self.system_health(snapshot)
        blocked = self.blocked_goal_pressure(snapshot)
        context_penalty = snapshot.context_pressure()
        error_penalty = min(1.0, len(snapshot.recent_errors) / 5.0)
        score = (
            0.22 * a.evidence_coverage
            + 0.20 * a.goal_alignment
            + 0.18 * health
            + 0.15 * a.confidence
            + 0.10 * (1.0 - a.uncertainty)
            + 0.08 * (1.0 - a.contradiction_load)
            + 0.07 * (1.0 - blocked)
            - 0.08 * context_penalty
            - 0.07 * error_penalty
        )
        return max(0.0, min(1.0, score))

    def detect_drift(self, snapshot: AwarenessSnapshot) -> dict[str, Any]:
        a = snapshot.assessment.normalized()
        signals: list[str] = []
        severity = 0.0
        if a.goal_alignment < 0.55:
            signals.append("goal_drift")
            severity += 0.25
        if a.evidence_coverage < 0.50:
            signals.append("evidence_gap")
            severity += 0.20
        if a.contradiction_load > 0.55:
            signals.append("contradiction_overload")
            severity += 0.20
        if a.uncertainty > 0.70 and a.confidence > 0.70:
            signals.append("overconfidence_risk")
            severity += 0.30
        if self.system_health(snapshot) < 0.65:
            signals.append("module_degradation")
            severity += 0.25
        if self.blocked_goal_pressure(snapshot) > 0.50:
            signals.append("blocked_goals")
            severity += 0.15
        if snapshot.context_pressure() > 0.85:
            signals.append("context_saturation")
            severity += 0.20
        if len(snapshot.recent_errors) >= 3:
            signals.append("error_accumulation")
            severity += 0.20
        return {
            "drift_detected": bool(signals),
            "severity": min(1.0, severity),
            "signals": signals,
        }

    def intervention(self, snapshot: AwarenessSnapshot) -> dict[str, Any]:
        drift = self.detect_drift(snapshot)
        a = snapshot.assessment.normalized()
        actions: list[str] = []
        if "goal_drift" in drift["signals"]:
            actions.append("restate_primary_goal_and_constraints")
        if "evidence_gap" in drift["signals"]:
            actions.append("research_or_request_missing_evidence")
        if "contradiction_overload" in drift["signals"]:
            actions.append("run_competing_hypotheses_review")
        if "overconfidence_risk" in drift["signals"]:
            actions.append("lower_confidence_and_seek_disconfirming_evidence")
        if "module_degradation" in drift["signals"]:
            actions.append("degrade_gracefully_and_route_around_unhealthy_modules")
        if "blocked_goals" in drift["signals"]:
            actions.append("replan_blocked_goals")
        if "context_saturation" in drift["signals"]:
            actions.append("checkpoint_and_compact_context")
        if "error_accumulation" in drift["signals"]:
            actions.append("pause_autonomous_promotion_and_run_error_review")
        if a.novelty_load > 0.80:
            actions.append("increase_verification_depth")
        if not actions:
            actions.append("continue")
        human_review = drift["severity"] >= 0.75
        return {
            "awareness_score": self.awareness_score(snapshot),
            "drift": drift,
            "recommended_actions": actions,
            "human_review_recommended": human_review,
        }

    def checkpoint(self, snapshot: AwarenessSnapshot) -> dict[str, Any]:
        payload = asdict(snapshot)
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        digest = sha256(canonical.encode("utf-8")).hexdigest()
        return {
            "checkpoint_hash": digest,
            "state": payload,
            "awareness_score": self.awareness_score(snapshot),
            "intervention": self.intervention(snapshot),
        }

    def compare(self, before: AwarenessSnapshot, after: AwarenessSnapshot) -> dict[str, Any]:
        before_score = self.awareness_score(before)
        after_score = self.awareness_score(after)
        return {
            "before_score": before_score,
            "after_score": after_score,
            "delta": after_score - before_score,
            "improved": after_score > before_score,
            "before_drift": self.detect_drift(before),
            "after_drift": self.detect_drift(after),
        }
