from atlas.worlds import ExperimentCandidate, ObservationPrediction, PossibleWorld
from atlas.worlds.robustness import WorldRobustness


def base_worlds():
    return (
        PossibleWorld(
            "w-a",
            "A",
            0.7,
            (),
            (ObservationPrediction("e", {"a": 0.9, "b": 0.1, "c": 0.0}),),
        ),
        PossibleWorld(
            "w-b",
            "B",
            0.3,
            (),
            (ObservationPrediction("e", {"a": 0.2, "b": 0.8, "c": 0.0}),),
        ),
    )


def test_unknown_world_reserve_is_explicit():
    robust = WorldRobustness()
    worlds = robust.with_unknown_reserve(
        base_worlds(),
        (ExperimentCandidate("e", "test"),),
        reserve=0.1,
    )
    assert any(world.world_id == "unknown-world-reserve" for world in worlds)


def test_counterevidence_search_targets_target_world_weakness():
    robust = WorldRobustness()
    targets = robust.counterevidence(
        base_worlds(),
        (ExperimentCandidate("e", "test"),),
        "w-a",
    )
    assert targets
    assert targets[0].outcome == "b"


def test_surprising_unpredicted_outcome_spawns_residual_trigger():
    robust = WorldRobustness()
    trigger = robust.residual_trigger(base_worlds(), "e", "c")
    assert trigger.should_spawn is True
