from atlas.asas import ASASCoordinator
from atlas.executive.models import Mission, MissionRoute
from atlas.knowledge import GlobalKnowledgeGate, KnowledgeCandidate


def test_asas_builds_integrity_checked_context_capsule():
    mission = Mission("m1", "Investigate a hypothesis", ("research",))
    coordinator = ASASCoordinator()
    capsule = coordinator.build_capsule(
        mission,
        identity_kernel={"atlas_version": "1.8"},
        invariants=("truthfulness",),
        uncertainties=("mechanism_unknown",),
    )
    assert capsule.capsule_id == "capsule:m1"
    assert len(capsule.integrity_hash()) == 64


def test_asas_coordinates_primary_ministries_and_integration_owner():
    route = MissionRoute(
        mission_id="m1",
        primary_ministries=("science_frontiers", "math_coherence"),
        transversal_bodies=("epistemic_council",),
        missing_skills=(),
        human_approval_required=False,
        rationale=(),
    )
    coordinator = ASASCoordinator()
    capsule = coordinator.build_capsule(
        Mission("m1", "Investigate", ("research",)),
        identity_kernel={"atlas_version": "1.8"},
        invariants=("truthfulness",),
    )
    plan = coordinator.coordinate(route, capsule)
    assert plan.synthesis_owner == "integration_chamber"
    assert ("science_frontiers", "math_coherence") in plan.dependency_edges


def test_hypothesis_can_enter_only_as_labeled_knowledge():
    gate = GlobalKnowledgeGate()
    decision = gate.evaluate(KnowledgeCandidate(
        candidate_id="k1",
        statement="Frontier claim",
        source_ministry="science_frontiers",
        epistemic_type="hypothesis",
        confidence=0.9,
    ))
    assert decision.status == "assimilate_labeled"


def test_high_impact_unreplicated_observation_requires_review():
    gate = GlobalKnowledgeGate()
    decision = gate.evaluate(KnowledgeCandidate(
        candidate_id="k2",
        statement="High-impact observation",
        source_ministry="science_frontiers",
        epistemic_type="observation",
        confidence=0.9,
        global_impact=0.95,
        replication_count=0,
    ))
    assert decision.status == "review"
