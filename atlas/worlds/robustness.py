from __future__ import annotations

from dataclasses import dataclass

from .lab import ExperimentCandidate, ObservationPrediction, PossibleWorld, PossibleWorldsLab


@dataclass(frozen=True)
class CounterevidenceTarget:
    world_id: str
    experiment_id: str
    outcome: str
    target_probability: float
    alternative_probability: float
    falsification_pressure: float


@dataclass(frozen=True)
class ResidualWorldTrigger:
    should_spawn: bool
    reason: str
    surprise_bits: float
    maximum_observed_probability: float


class WorldRobustness:
    def __init__(self) -> None:
        self.lab = PossibleWorldsLab()

    def with_unknown_reserve(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiments: tuple[ExperimentCandidate, ...],
        *,
        reserve: float = 0.10,
    ) -> tuple[PossibleWorld, ...]:
        if not 0 < reserve < 1:
            raise ValueError("Unknown reserve must be between zero and one.")

        scaled = tuple(
            PossibleWorld(
                world.world_id,
                world.title,
                world.prior * (1.0 - reserve),
                world.assumptions,
                world.predictions,
                world.source_refs,
                world.epistemic_label,
            )
            for world in worlds
        )

        predictions: list[ObservationPrediction] = []
        for experiment in experiments:
            outcomes: set[str] = set()
            for world in worlds:
                prediction = world.prediction_for(experiment.experiment_id)
                if prediction:
                    outcomes.update(prediction)
            if outcomes:
                probability = 1.0 / len(outcomes)
                predictions.append(
                    ObservationPrediction(
                        experiment.experiment_id,
                        {outcome: probability for outcome in sorted(outcomes)},
                    )
                )

        unknown = PossibleWorld(
            "unknown-world-reserve",
            "None of the current models is adequate",
            reserve,
            ("Current model family may be misspecified.",),
            tuple(predictions),
            epistemic_label="unknown_residual",
        )
        return scaled + (unknown,)

    def counterevidence(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiments: tuple[ExperimentCandidate, ...],
        target_world_id: str,
    ) -> tuple[CounterevidenceTarget, ...]:
        target = next(
            (world for world in worlds if world.world_id == target_world_id),
            None,
        )
        if target is None:
            raise KeyError(target_world_id)

        priors = self.lab._priors(worlds)
        alternatives = [world for world in worlds if world.world_id != target_world_id]
        results: list[CounterevidenceTarget] = []

        for experiment in experiments:
            target_prediction = target.prediction_for(experiment.experiment_id)
            if not target_prediction:
                continue
            outcomes = set(target_prediction)
            for alternative in alternatives:
                prediction = alternative.prediction_for(experiment.experiment_id)
                if prediction:
                    outcomes.update(prediction)

            for outcome in outcomes:
                target_p = target_prediction.get(outcome, 0.0)
                alt_mass = sum(
                    priors[alternative.world_id]
                    * (
                        alternative.prediction_for(experiment.experiment_id) or {}
                    ).get(outcome, 0.0)
                    for alternative in alternatives
                )
                alternative_prior = sum(priors[a.world_id] for a in alternatives)
                alt_p = alt_mass / alternative_prior if alternative_prior > 0 else 0.0
                pressure = max(0.0, alt_p - target_p)
                if pressure > 0:
                    results.append(
                        CounterevidenceTarget(
                            target_world_id,
                            experiment.experiment_id,
                            outcome,
                            target_p,
                            alt_p,
                            pressure,
                        )
                    )

        return tuple(
            sorted(
                results,
                key=lambda item: (
                    -item.falsification_pressure,
                    item.experiment_id,
                    item.outcome,
                ),
            )
        )

    def residual_trigger(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiment_id: str,
        outcome: str,
        *,
        surprise_threshold_bits: float = 3.0,
        max_probability_threshold: float = 0.20,
    ) -> ResidualWorldTrigger:
        posterior = self.lab.posterior(worlds, experiment_id, outcome)
        observed_probabilities = []
        for world in worlds:
            prediction = world.prediction_for(experiment_id)
            observed_probabilities.append(
                prediction.get(outcome, 0.0) if prediction else 0.0
            )
        maximum = max(observed_probabilities, default=0.0)
        should_spawn = (
            posterior.surprise_bits >= surprise_threshold_bits
            and maximum <= max_probability_threshold
        )
        reason = (
            "Observed outcome is improbable under every current world; create a residual hypothesis."
            if should_spawn
            else "Current world family can still accommodate the observation."
        )
        return ResidualWorldTrigger(
            should_spawn,
            reason,
            posterior.surprise_bits,
            maximum,
        )
