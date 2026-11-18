from atlas.awareness import AwarenessEngine, AwarenessSnapshot, GoalState, ModuleHealth, SelfAssessment


def healthy_snapshot() -> AwarenessSnapshot:
    return AwarenessSnapshot(
        goals=(GoalState("g1", "Research claim", progress=0.7, priority=0.9),),
        modules=(ModuleHealth("research", True, 0.95), ModuleHealth("forecast", True, 0.9)),
        assessment=SelfAssessment(
            confidence=0.75,
            uncertainty=0.25,
            evidence_coverage=0.85,
            goal_alignment=0.9,
            contradiction_load=0.15,
            novelty_load=0.3,
        ),
    )


def test_awareness_score_is_bounded_and_high_for_healthy_state():
    score = AwarenessEngine().awareness_score(healthy_snapshot())
    assert 0.0 <= score <= 1.0
    assert score > 0.7


def test_detects_overconfidence_when_uncertainty_is_also_high():
    snapshot = AwarenessSnapshot(
        assessment=SelfAssessment(0.9, 0.9, 0.8, 0.8, 0.1, 0.2)
    )
    result = AwarenessEngine().detect_drift(snapshot)
    assert "overconfidence_risk" in result["signals"]


def test_detects_context_saturation():
    snapshot = AwarenessSnapshot(context_tokens_used=900, context_tokens_budget=1000)
    result = AwarenessEngine().detect_drift(snapshot)
    assert "context_saturation" in result["signals"]


def test_module_degradation_triggers_route_around_action():
    snapshot = AwarenessSnapshot(
        modules=(ModuleHealth("research", False, 0.4, error_count=5),),
        assessment=SelfAssessment(0.5, 0.5, 0.7, 0.8, 0.1, 0.2),
    )
    result = AwarenessEngine().intervention(snapshot)
    assert "degrade_gracefully_and_route_around_unhealthy_modules" in result["recommended_actions"]


def test_checkpoint_is_deterministic_for_same_snapshot():
    snapshot = healthy_snapshot()
    engine = AwarenessEngine()
    a = engine.checkpoint(snapshot)["checkpoint_hash"]
    b = engine.checkpoint(snapshot)["checkpoint_hash"]
    assert a == b


def test_compare_detects_improvement():
    before = AwarenessSnapshot(
        assessment=SelfAssessment(0.4, 0.8, 0.3, 0.4, 0.6, 0.5),
        modules=(ModuleHealth("research", False, 0.4, 3),),
    )
    after = healthy_snapshot()
    result = AwarenessEngine().compare(before, after)
    assert result["improved"] is True
    assert result["delta"] > 0


def test_blocked_goals_are_detected():
    snapshot = AwarenessSnapshot(
        goals=(GoalState("g1", "Blocked", priority=1.0, blocked=True),),
        assessment=SelfAssessment(0.6, 0.4, 0.8, 0.8, 0.1, 0.1),
    )
    result = AwarenessEngine().detect_drift(snapshot)
    assert "blocked_goals" in result["signals"]
