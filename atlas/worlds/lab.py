from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Iterable


_EPSILON = 1e-12


def _normalize(values: dict[str, float]) -> dict[str, float]:
    total = sum(max(0.0, value) for value in values.values())
    if total <= 0:
        raise ValueError("Probability mass must be positive.")
    return {key: max(0.0, value) / total for key, value in values.items()}


def _entropy(probabilities: Iterable[float]) -> float:
    return -sum(p * log2(p) for p in probabilities if p > 0)


@dataclass(frozen=True)
class ObservationPrediction:
    experiment_id: str
    outcome_probabilities: dict[str, float]

    def normalized(self) -> dict[str, float]:
        return _normalize(self.outcome_probabilities)


@dataclass(frozen=True)
class PossibleWorld:
    world_id: str
    title: str
    prior: float
    assumptions: tuple[str, ...]
    predictions: tuple[ObservationPrediction, ...]
    source_refs: tuple[str, ...] = ()
    epistemic_label: str = "hypothesis"

    def prediction_for(self, experiment_id: str) -> dict[str, float] | None:
        for prediction in self.predictions:
            if prediction.experiment_id == experiment_id:
                return prediction.normalized()
        return None


@dataclass(frozen=True)
class ExperimentCandidate:
    experiment_id: str
    title: str
    cost: float = 1.0
    time: float = 1.0
    risk: float = 0.0
    feasibility: float = 1.0
    representativeness: float = 1.0
    robustness: float = 1.0
    reversible: bool = True
    requires_human_approval: bool = False
    metadata: dict[str, object] | None = None


@dataclass(frozen=True)
class ExperimentScore:
    experiment_id: str
    expected_information_gain: float
    discrimination_power: float
    efficiency: float
    expected_posterior_entropy: float
    prior_entropy: float
    identifiable_world_pairs: tuple[tuple[str, str], ...]
    indistinguishable_world_pairs: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class WorldPosterior:
    observed_experiment_id: str
    observed_outcome: str
    probabilities: dict[str, float]
    surprise_bits: float
    entropy_bits: float


@dataclass(frozen=True)
class RealityGap:
    world_id: str
    experiment_id: str
    outcome: str
    predicted_probability: float
    gap: float
    severity: str


class PossibleWorldsLab:
    """Compares possible worlds and chooses low-cost experiments that distinguish them."""

    def _priors(self, worlds: tuple[PossibleWorld, ...]) -> dict[str, float]:
        return _normalize({world.world_id: world.prior for world in worlds})

    def posterior(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiment_id: str,
        outcome: str,
    ) -> WorldPosterior:
        priors = self._priors(worlds)
        likelihoods: dict[str, float] = {}
        for world in worlds:
            prediction = world.prediction_for(experiment_id)
            likelihoods[world.world_id] = (
                prediction.get(outcome, _EPSILON) if prediction else _EPSILON
            )

        evidence = sum(priors[wid] * likelihoods[wid] for wid in priors)
        posterior = _normalize(
            {
                wid: priors[wid] * likelihoods[wid]
                for wid in priors
            }
        )
        surprise = -log2(max(evidence, _EPSILON))
        return WorldPosterior(
            observed_experiment_id=experiment_id,
            observed_outcome=outcome,
            probabilities=posterior,
            surprise_bits=surprise,
            entropy_bits=_entropy(posterior.values()),
        )

    def reality_gaps(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiment_id: str,
        outcome: str,
    ) -> tuple[RealityGap, ...]:
        gaps: list[RealityGap] = []
        for world in worlds:
            prediction = world.prediction_for(experiment_id)
            probability = prediction.get(outcome, 0.0) if prediction else 0.0
            gap = 1.0 - probability
            if gap >= 0.9:
                severity = "critical"
            elif gap >= 0.65:
                severity = "high"
            elif gap >= 0.35:
                severity = "moderate"
            else:
                severity = "low"
            gaps.append(
                RealityGap(
                    world.world_id,
                    experiment_id,
                    outcome,
                    probability,
                    gap,
                    severity,
                )
            )
        return tuple(gaps)

    def score_experiment(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiment: ExperimentCandidate,
        *,
        distinguish_threshold: float = 0.20,
    ) -> ExperimentScore:
        priors = self._priors(worlds)
        prior_entropy = _entropy(priors.values())

        all_outcomes: set[str] = set()
        predictions: dict[str, dict[str, float]] = {}
        for world in worlds:
            prediction = world.prediction_for(experiment.experiment_id)
            if prediction:
                predictions[world.world_id] = prediction
                all_outcomes.update(prediction)

        if not all_outcomes:
            return ExperimentScore(
                experiment.experiment_id,
                0.0,
                0.0,
                0.0,
                prior_entropy,
                prior_entropy,
                (),
                tuple(
                    (a.world_id, b.world_id)
                    for i, a in enumerate(worlds)
                    for b in worlds[i + 1 :]
                ),
            )

        predictive_outcome_probability: dict[str, float] = {}
        for outcome in all_outcomes:
            predictive_outcome_probability[outcome] = sum(
                priors[world.world_id]
                * predictions.get(world.world_id, {}).get(outcome, 0.0)
                for world in worlds
            )

        expected_posterior_entropy = 0.0
        for outcome, outcome_probability in predictive_outcome_probability.items():
            if outcome_probability <= 0:
                continue
            posterior = self.posterior(worlds, experiment.experiment_id, outcome)
            expected_posterior_entropy += outcome_probability * posterior.entropy_bits

        information_gain = max(0.0, prior_entropy - expected_posterior_entropy)

        identifiable: list[tuple[str, str]] = []
        indistinguishable: list[tuple[str, str]] = []
        pair_distances: list[float] = []
        for i, left in enumerate(worlds):
            left_dist = predictions.get(left.world_id, {})
            for right in worlds[i + 1 :]:
                right_dist = predictions.get(right.world_id, {})
                outcomes = set(left_dist) | set(right_dist)
                total_variation = 0.5 * sum(
                    abs(left_dist.get(o, 0.0) - right_dist.get(o, 0.0))
                    for o in outcomes
                )
                pair_distances.append(total_variation)
                pair = (left.world_id, right.world_id)
                if total_variation >= distinguish_threshold:
                    identifiable.append(pair)
                else:
                    indistinguishable.append(pair)

        discrimination_power = (
            sum(pair_distances) / len(pair_distances) if pair_distances else 0.0
        )

        penalty = (
            max(0.05, experiment.cost)
            * max(0.05, experiment.time)
            * (1.0 + 2.0 * max(0.0, experiment.risk))
        )
        quality = (
            max(0.0, experiment.feasibility)
            * max(0.0, experiment.representativeness)
            * max(0.0, experiment.robustness)
        )
        efficiency = information_gain * discrimination_power * quality / penalty

        return ExperimentScore(
            experiment.experiment_id,
            information_gain,
            discrimination_power,
            efficiency,
            expected_posterior_entropy,
            prior_entropy,
            tuple(identifiable),
            tuple(indistinguishable),
        )

    def minimal_discriminant_experiment(
        self,
        worlds: tuple[PossibleWorld, ...],
        experiments: tuple[ExperimentCandidate, ...],
        *,
        min_information_gain: float = 0.01,
    ) -> ExperimentScore | None:
        scores = [
            self.score_experiment(worlds, experiment)
            for experiment in experiments
            if experiment.feasibility > 0
            and experiment.reversible
            and not experiment.requires_human_approval
        ]
        viable = [
            score for score in scores
            if score.expected_information_gain >= min_information_gain
        ]
        if not viable:
            return None
        return max(
            viable,
            key=lambda score: (
                score.efficiency,
                score.expected_information_gain,
                score.discrimination_power,
            ),
        )
