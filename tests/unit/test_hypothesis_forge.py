from atlas.innovation import HypothesisForge, TechnologySeed
from atlas.innovation.ministry_router import MinistryInnovationRouter


def test_reversible_testable_seed_reaches_sandbox():
    seed = TechnologySeed(
        seed_id="codec-x",
        name="Multiscale Semantic Codec",
        mechanism_ids=("m1",),
        purpose="Explore a new image representation.",
        target_ministries=("math_coherence", "creation_design", "research_evolution"),
        novelty=0.9,
        testability=0.9,
        reversibility=1.0,
        evidence_readiness=0.6,
        safety_risk=0.05,
        acceptance_tests=("beat_baseline_on_quality_per_bit",),
    )
    route = MinistryInnovationRouter().route(seed, ("compression", "image", "math"))
    decision = HypothesisForge().evaluate_seed(seed, route.assessments)
    assert decision.status == "sandbox"
    assert "creation_design" in decision.required_reviews


def test_health_seed_requires_human_approval():
    seed = TechnologySeed(
        seed_id="bio-sense",
        name="Weak-field multimodal physiology research",
        mechanism_ids=("m2",),
        purpose="Explore non-invasive multimodal physiological sensing.",
        target_ministries=("health_wellbeing", "science_frontiers"),
        novelty=0.8,
        testability=0.7,
        reversibility=0.8,
        evidence_readiness=0.4,
        safety_risk=0.45,
        regulatory_risk=0.6,
    )
    decision = HypothesisForge().evaluate_seed(seed)
    assert decision.requires_human_approval is True
    assert "guardian" in decision.required_reviews
