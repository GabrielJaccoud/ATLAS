from atlas.worlds.programs import default_world_programs
from atlas.worlds.synthesis import WorldTechnologySynthesizer


def test_default_world_programs_have_distinguishable_experiments():
    synthesizer = WorldTechnologySynthesizer()
    programs = default_world_programs()
    assert len(programs) >= 4
    decisions = [synthesizer.evaluate(program) for program in programs]
    assert any(decision.next_experiment is not None for decision in decisions)


def test_physio_program_remains_approval_gated():
    program = next(
        p for p in default_world_programs()
        if p.program_id == "program-physiology-multimodal"
    )
    assert all(exp.requires_human_approval for exp in program.experiments)
