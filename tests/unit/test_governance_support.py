from atlas.governance import GovernanceBody, GovernanceNetwork, GovernanceRequest
from atlas.support import SupportCell, SupportRequest, SupportService


def test_governance_routes_maintenance_to_support_cell():
    response = GovernanceNetwork().route(GovernanceRequest(
        request_id="g1",
        source="science_frontiers",
        purpose="Need a new analysis tool",
        categories=("tooling", "capability_gap"),
    ))
    assert GovernanceBody.SUPPORT_CELL in response.routed_to
    assert GovernanceBody.ASAS in response.routed_to


def test_governance_routes_memory_issues_to_mnemosyne():
    response = GovernanceNetwork().route(GovernanceRequest(
        request_id="g2",
        source="research",
        purpose="Resolve duplicate memories",
        categories=("memory", "duplicate"),
    ))
    assert GovernanceBody.MNEMOSYNE in response.routed_to


def test_support_cell_sends_capability_build_through_codex_and_ria():
    plan = SupportCell().plan(SupportRequest(
        request_id="s1",
        requester="math_coherence",
        symptom="Missing specialized solver",
        desired_outcome="Add solver",
        requested_services=(SupportService.CAPABILITY_BUILD,),
        requires_code_change=True,
    ))
    assert plan.route_to_codex is True
    assert plan.route_to_ria is True
    assert plan.sandbox_required is True


def test_constitutional_support_requires_guardian_and_human_approval():
    plan = SupportCell().plan(SupportRequest(
        request_id="s2",
        requester="constitutional_guardian",
        symptom="Invariant schema change proposed",
        desired_outcome="Evaluate change",
        requested_services=(SupportService.MIGRATION,),
        touches_constitution=True,
    ))
    assert plan.route_to_guardian is True
    assert plan.human_approval_required is True
