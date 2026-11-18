from atlas.executive import Mission, MinistryOrchestrator, build_default_ministry_registry


def test_registry_contains_core_ministries_and_transversal_bodies():
    registry = build_default_ministry_registry()
    for ministry_id in (
        "math_coherence",
        "science_frontiers",
        "architecture_environment",
        "creation_design",
        "business_ventures",
        "education_human",
        "health_wellbeing",
        "governance_ethics",
        "research_evolution",
        "constitutional_guardian",
        "contexts_worlds",
        "epistemic_council",
        "simulation_chamber",
        "integration_chamber",
        "outcomes_observatory",
    ):
        assert ministry_id in registry


def test_science_mission_routes_to_science_and_research():
    router = MinistryOrchestrator(build_default_ministry_registry())
    route = router.route(Mission(
        mission_id="m1",
        objective="Formalize and test a frontier hypothesis",
        required_skills=("protocol_designer", "evidence_register", "hypothesis_tournament"),
    ))
    assert "science_frontiers" in route.primary_ministries
    assert "constitutional_guardian" in route.transversal_bodies
    assert "epistemic_council" in route.transversal_bodies
    assert route.missing_skills == ()


def test_context_mission_attaches_contexts_worlds():
    router = MinistryOrchestrator(build_default_ministry_registry())
    route = router.route(Mission(
        mission_id="m2",
        objective="Build a portable context capsule",
        required_skills=("context_capsule_builder",),
    ))
    assert "contexts_worlds" in route.transversal_bodies


def test_external_or_high_risk_action_requires_human_approval():
    router = MinistryOrchestrator(build_default_ministry_registry())
    route = router.route(Mission(
        mission_id="m3",
        objective="Perform external write",
        required_skills=("audit",),
        risk=0.8,
        external_action=True,
    ))
    assert route.human_approval_required is True


def test_uncovered_skills_are_explicit():
    router = MinistryOrchestrator(build_default_ministry_registry())
    route = router.route(Mission(
        mission_id="m4",
        objective="Unknown capability",
        required_skills=("nonexistent_skill",),
    ))
    assert route.missing_skills == ("nonexistent_skill",)
