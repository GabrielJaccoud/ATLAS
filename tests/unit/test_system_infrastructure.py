from atlas.events import EventBus, EventPriority, EventRecord, EventSubscription
from atlas.homeostasis import HomeostasisController, HomeostasisReading, MetricEnvelope
from atlas.failures import FailureMemory, FailureSignature
from atlas.reflexes import ReflexEngine, ReflexRule
from atlas.modes import GlobalMode, GlobalModeController
from atlas.regeneration import Checkpoint, RegenerationProtocol
from atlas.artifacts.fabric import ArtifactFabric, ArtifactFamily
from atlas.research import ResearchBacklog, ResearchItem, ResearchStatus
from atlas.councils import CouncilCadence, CouncilScheduler


def test_event_bus_filters_by_priority_and_type():
    bus = EventBus()
    bus.subscribe(EventSubscription("support", ("health.alert",), min_priority=EventPriority.HIGH))
    bus.publish(EventRecord("e1", "health.alert", "homeostasis", priority=EventPriority.HIGH))
    bus.publish(EventRecord("e2", "other", "x", priority=EventPriority.CRITICAL))
    assert tuple(e.event_id for e in bus.events_for("support")) == ("e1",)


def test_homeostasis_marks_large_deviation_critical():
    result = HomeostasisController().assess(
        MetricEnvelope("error_rate", healthy_max=0.1),
        HomeostasisReading("error_rate", 0.5),
    )
    assert result.state == "critical"


def test_failure_memory_finds_same_component():
    memory = FailureMemory()
    memory.remember(FailureSignature("f1", "api", ("timeout",), "network", ("retry",)))
    assert memory.find_similar(component="api", symptoms=("timeout",))[0].failure_id == "f1"


def test_reflex_escalates_irreversible_action():
    event = EventRecord("e", "homeostasis.warning", "homeostasis")
    decisions = ReflexEngine().evaluate(
        event, risk=0.2, reversible=False,
        rules=(ReflexRule("r", "homeostasis.warning", 0.5, "restart_worker"),),
    )
    assert decisions[0].escalate is True


def test_global_mode_changes_policy():
    c = GlobalModeController()
    policy = c.set_mode(GlobalMode.RESEARCH_INTENSIVE)
    assert policy.research_depth == 1.0


def test_regeneration_uses_known_good_checkpoint():
    plan = RegenerationProtocol().plan(
        "worker", (Checkpoint("c1", "worker", "1", {"ok": True}, healthy=True),)
    )
    assert plan.source_checkpoint == "c1"


def test_artifact_lineage_preserves_parent_chain():
    fabric = ArtifactFabric()
    a = fabric.new_version(artifact_id="a", version_id="v1", filename="x.png", media_type="image/png", content=b"1")
    b = fabric.new_version(artifact_id="a", version_id="v2", filename="x.jxl", media_type="image/jxl", content=b"2", parent_version_id="v1")
    family = ArtifactFamily("f", "a", (a, b))
    assert tuple(v.version_id for v in fabric.lineage(family, "v2")) == ("v2", "v1")


def test_research_backlog_orders_by_priority():
    b = ResearchBacklog()
    b.add(ResearchItem("a", "science", "A?", ResearchStatus.IDEA, priority=0.2))
    b.add(ResearchItem("b", "science", "B?", ResearchStatus.TESTING, priority=0.9))
    assert b.by_ministry("science")[0].item_id == "b"


def test_crisis_council_includes_guardian_and_support():
    session = CouncilScheduler().create("c", CouncilCadence.CRISIS)
    assert "guardian" in session.required_bodies
    assert "support_cell" in session.required_bodies
