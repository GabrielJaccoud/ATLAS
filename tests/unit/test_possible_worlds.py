from atlas.worlds import (
    ExperimentCandidate,
    ObservationPrediction,
    PossibleWorld,
    PossibleWorldsLab,
)


def worlds():
    return (
        PossibleWorld(
            "w0",
            "Conventional model",
            0.6,
            ("No hidden coupling",),
            (
                ObservationPrediction("e-cheap", {"signal": 0.1, "null": 0.9}),
                ObservationPrediction("e-expensive", {"signal": 0.05, "null": 0.95}),
            ),
        ),
        PossibleWorld(
            "w1",
            "Alternative coupling model",
            0.4,
            ("Hidden coupling exists",),
            (
                ObservationPrediction("e-cheap", {"signal": 0.7, "null": 0.3}),
                ObservationPrediction("e-expensive", {"signal": 0.9, "null": 0.1}),
            ),
        ),
    )


def test_minimal_experiment_balances_information_and_cost():
    lab = PossibleWorldsLab()
    experiments = (
        ExperimentCandidate("e-cheap", "Cheap discriminant", cost=1, time=1, risk=0.0),
        ExperimentCandidate("e-expensive", "Strong but expensive", cost=10, time=2, risk=0.0),
    )
    result = lab.minimal_discriminant_experiment(worlds(), experiments)
    assert result is not None
    assert result.experiment_id == "e-cheap"
    assert result.expected_information_gain > 0


def test_observation_updates_world_probabilities():
    lab = PossibleWorldsLab()
    posterior = lab.posterior(worlds(), "e-cheap", "signal")
    assert posterior.probabilities["w1"] > posterior.probabilities["w0"]


def test_reality_gap_flags_bad_prediction():
    lab = PossibleWorldsLab()
    gaps = lab.reality_gaps(worlds(), "e-cheap", "signal")
    by_world = {gap.world_id: gap for gap in gaps}
    assert by_world["w0"].gap > by_world["w1"].gap
