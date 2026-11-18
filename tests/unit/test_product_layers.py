from atlas.personal import MyWorldGraph, WorldEdge, WorldNode
from atlas.opportunities import Opportunity, OpportunityEngine
from atlas.runtime import HybridRuntime, ModelEndpoint, TaskProfile
from atlas.voice import VoiceGateway, VoiceTurn
from atlas.engineering.missions import EngineeringMission, plan_engineering


def test_my_world_connects_projects():
    g = MyWorldGraph()
    g.add_node(WorldNode("me", "person", "User", {}))
    g.add_node(WorldNode("p", "project", "Project", {}))
    g.connect(WorldEdge("me", "created", "p"))
    assert g.neighbors("me")[0].node_id == "p"


def test_opportunity_engine_matches_domain_and_capability():
    o = Opportunity("o", "Grant", ("education",), ("proposal",), 0.9)
    m = OpportunityEngine().match(o, target_id="p", target_domains=("education",), target_capabilities=("proposal",))
    assert m.score > 0.7


def test_hybrid_runtime_can_force_local():
    decision = HybridRuntime().choose(
        TaskProfile("t", 0.9, 0.5, 0.5, offline_required=True),
        (
            ModelEndpoint("cloud", "cloud", ("text",), 1.0, 0.5, 0.9),
            ModelEndpoint("local", "local", ("text",), 0.7, 1.0, 0.6),
        ),
    )
    assert decision.endpoint_id == "local"


def test_voice_gateway_supports_research_mode():
    g = VoiceGateway()
    s = g.open_session("s", mode="research")
    g.add_turn(s, VoiceTurn("t", "audio", "investigue isso"))
    assert s.turns[0].transcript == "investigue isso"


def test_engineering_mission_requires_pr_and_tests():
    p = plan_engineering(EngineeringMission("e", "build", "repo", "branch", ("pytest",), "capsule"))
    assert p.require_pull_request and p.require_tests and p.require_ria
