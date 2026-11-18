from __future__ import annotations

from collections import Counter

from .models import Mission, MissionRoute, Ministry


class MinistryOrchestrator:
    """Deterministic router for ministry collaboration.

    Language-model agents may later serve roles inside ministries, but routing,
    permissions and cross-cutting controls remain explicit and testable.
    """

    def __init__(self, registry: dict[str, Ministry]):
        self.registry = registry

    def route(self, mission: Mission, max_primary: int = 4) -> MissionRoute:
        required = set(mission.required_skills)
        scores: Counter[str] = Counter()

        for ministry in self.registry.values():
            if ministry.transversal:
                continue
            overlap = required.intersection(ministry.skills)
            if overlap:
                scores[ministry.ministry_id] = len(overlap)

        primary = tuple(
            ministry_id
            for ministry_id, _ in sorted(
                scores.items(),
                key=lambda item: (-item[1], item[0]),
            )[:max_primary]
        )

        covered: set[str] = set()
        for ministry_id in primary:
            covered.update(self.registry[ministry_id].skills)

        missing = tuple(sorted(required - covered))

        transversal: list[str] = [
            "constitutional_guardian",
            "epistemic_council",
            "integration_chamber",
            "outcomes_observatory",
        ]

        if any(skill in required for skill in (
            "world_compiler", "context_compiler", "context_capsule_builder",
            "signature_builder", "transition_planner", "admissibility_check",
        )):
            transversal.append("contexts_worlds")

        if any(skill in required for skill in (
            "counterfactual_simulation", "scenario_analysis", "simulation",
        )):
            transversal.append("simulation_chamber")

        if any(skill in required for skill in (
            "formalization", "bayesian_update", "spectral_coherence",
            "coherence_audit", "simulation",
        )):
            transversal.append("math_coherence")

        transversal = list(dict.fromkeys(transversal))

        human_approval = (
            mission.external_action
            or mission.irreversible
            or mission.risk >= 0.70
        )

        rationale = [
            f"Matched {len(required) - len(missing)}/{len(required)} required skills.",
            "Constitutional, epistemic, integration and outcome controls are always attached.",
        ]
        if human_approval:
            rationale.append("Human approval required by risk/action policy.")
        if missing:
            rationale.append(f"Uncovered skills: {', '.join(missing)}.")

        return MissionRoute(
            mission_id=mission.mission_id,
            primary_ministries=primary,
            transversal_bodies=tuple(transversal),
            missing_skills=missing,
            human_approval_required=human_approval,
            rationale=tuple(rationale),
        )
