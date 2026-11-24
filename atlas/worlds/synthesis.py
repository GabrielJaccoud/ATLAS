from __future__ import annotations

from dataclasses import dataclass

from atlas.innovation.ria_reverse import (
    RIAReverseEngineering,
    ReverseEngineeringCandidate,
)

from .lab import ExperimentCandidate, ExperimentScore, PossibleWorld, PossibleWorldsLab


@dataclass(frozen=True)
class WorldResearchProgram:
    program_id: str
    worlds: tuple[PossibleWorld, ...]
    experiments: tuple[ExperimentCandidate, ...]
    technology_candidates: tuple[ReverseEngineeringCandidate, ...]


@dataclass(frozen=True)
class ProgramDecision:
    program_id: str
    next_experiment: ExperimentScore | None
    technology_results: tuple[object, ...]
    unresolved_world_pairs: tuple[tuple[str, str], ...]


class WorldTechnologySynthesizer:
    def __init__(self) -> None:
        self.worlds_lab = PossibleWorldsLab()
        self.ria = RIAReverseEngineering()

    def evaluate(self, program: WorldResearchProgram) -> ProgramDecision:
        next_experiment = self.worlds_lab.minimal_discriminant_experiment(
            program.worlds,
            program.experiments,
        )
        technology_results = tuple(
            self.ria.evaluate(candidate)
            for candidate in program.technology_candidates
        )
        unresolved = (
            next_experiment.indistinguishable_world_pairs
            if next_experiment
            else tuple(
                (a.world_id, b.world_id)
                for i, a in enumerate(program.worlds)
                for b in program.worlds[i + 1 :]
            )
        )
        return ProgramDecision(
            program.program_id,
            next_experiment,
            technology_results,
            unresolved,
        )
