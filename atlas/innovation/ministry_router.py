from __future__ import annotations

from dataclasses import dataclass

from .forge import MinistryAssessment, TechnologySeed


MINISTRY_TAGS: dict[str, set[str]] = {
    "math_coherence": {"math", "geometry", "signal", "compression", "spectral", "causal"},
    "science_frontiers": {"physics", "space", "fields", "sensor", "anomaly", "biology"},
    "architecture_environment": {"environment", "geometry", "spatial", "materials"},
    "creation_design": {"image", "audio", "codec", "interface", "symbol", "generative"},
    "business_ventures": {"product", "market", "platform", "commercialization"},
    "education_human": {"learning", "language", "symbol", "philosophy", "cognition"},
    "health_wellbeing": {"body", "health", "biofield", "imaging", "physiology", "neural"},
    "governance_ethics": {"ethics", "privacy", "risk", "consent", "regulation"},
    "research_evolution": {"hypothesis", "experiment", "replication", "metascience", "invention"},
}


@dataclass(frozen=True)
class InnovationRoute:
    seed_id: str
    assessments: tuple[MinistryAssessment, ...]


class MinistryInnovationRouter:
    def route(
        self,
        seed: TechnologySeed,
        tags: tuple[str, ...],
    ) -> InnovationRoute:
        tagset = set(tags)
        out: list[MinistryAssessment] = []
        for ministry, vocabulary in MINISTRY_TAGS.items():
            overlap = tagset.intersection(vocabulary)
            if not overlap and ministry not in seed.target_ministries:
                continue
            relevance = min(1.0, 0.35 + 0.15 * len(overlap))
            if ministry in seed.target_ministries:
                relevance = max(relevance, 0.8)
            expected_value = max(0.0, min(1.0, seed.novelty * seed.testability))
            concerns: list[str] = []
            if ministry == "health_wellbeing" and seed.safety_risk > 0.3:
                concerns.append("medical_validation_required")
            if ministry == "governance_ethics" and seed.regulatory_risk > 0.3:
                concerns.append("regulatory_review_required")
            out.append(
                MinistryAssessment(
                    ministry,
                    relevance,
                    expected_value,
                    concerns=tuple(concerns),
                )
            )
        return InnovationRoute(seed.seed_id, tuple(out))
