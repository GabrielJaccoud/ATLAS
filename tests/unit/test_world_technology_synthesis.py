from atlas.worlds.synthesis import WorldResearchProgram, WorldTechnologySynthesizer
from atlas.worlds import ExperimentCandidate, ObservationPrediction, PossibleWorld


def test_program_selects_next_discriminant_experiment():
    program = WorldResearchProgram(
        "p1",
        (
            PossibleWorld(
                "a", "A", 0.5, (), (ObservationPrediction("e", {"yes": 0.9, "no": 0.1}),)
            ),
            PossibleWorld(
                "b", "B", 0.5, (), (ObservationPrediction("e", {"yes": 0.1, "no": 0.9}),)
            ),
        ),
        (ExperimentCandidate("e", "Minimal test", cost=1, time=1),),
        (),
    )
    decision = WorldTechnologySynthesizer().evaluate(program)
    assert decision.next_experiment is not None
    assert decision.next_experiment.experiment_id == "e"
