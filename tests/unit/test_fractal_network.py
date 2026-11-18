from atlas.executive.collective import CollectiveInsight, CollectiveMind
from atlas.executive.council import GrandCouncil
from atlas.executive.fractal import FractalIdentity, MinistryFractal, MinistrySelfState


def fractal(ministry_id: str, **state_kwargs) -> MinistryFractal:
    return MinistryFractal(
        identity=FractalIdentity(
            ministry_id=ministry_id,
            atlas_identity_version="1.8",
            constitutional_invariants=("truthfulness", "human_approval_for_sensitive_actions"),
            ministry_mandate=f"Mandate for {ministry_id}",
        ),
        state=MinistrySelfState(ministry_id=ministry_id, **state_kwargs),
    )


def test_fractal_has_local_autonomy_but_not_constitutional_authority():
    f = fractal("science")
    assert f.may("research")
    assert f.requires_global_review("constitutional_change")


def test_collective_state_aggregates_local_health_and_research():
    mind = CollectiveMind()
    state = mind.summarize((
        fractal("science", active_research=("h1", "h2")),
        fractal("math", active_research=("m1",), recent_errors=("e1",)),
    ))
    assert state.active_research_count == 3
    assert "science" in state.ministry_health
    assert "math" in state.ministry_health


def test_collective_assimilation_filters_weak_or_review_required_insights():
    mind = CollectiveMind()
    insights = (
        CollectiveInsight("a", "strong", ("science",), 0.9),
        CollectiveInsight("b", "weak", ("science",), 0.3),
        CollectiveInsight("c", "review", ("science",), 0.95, requires_review=True),
    )
    accepted = mind.assimilate(insights)
    assert tuple(i.insight_id for i in accepted) == ("a",)


def test_grand_council_collects_discoveries_conflicts_and_capability_proposals():
    council = GrandCouncil()
    report = council.convene((
        fractal(
            "science",
            recent_discoveries=("new result",),
            unresolved_contradictions=("conflict",),
            proposed_capabilities=("biofisico_agent",),
        ),
    ))
    assert report.new_knowledge == ("new result",)
    assert report.unresolved_conflicts == ("conflict",)
    assert report.system_changes_proposed == ("biofisico_agent",)
