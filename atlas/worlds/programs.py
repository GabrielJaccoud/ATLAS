from __future__ import annotations

from atlas.innovation.ria_reverse import default_reverse_engineering_candidates

from .lab import ExperimentCandidate, ObservationPrediction, PossibleWorld
from .synthesis import WorldResearchProgram


def _candidate(candidate_id: str):
    return next(
        candidate
        for candidate in default_reverse_engineering_candidates()
        if candidate.candidate_id == candidate_id
    )


def semantic_codec_program() -> WorldResearchProgram:
    worlds = (
        PossibleWorld(
            "codec-baseline",
            "Existing codecs remain Pareto-optimal",
            0.50,
            ("Current JXL/AVIF/WebP trade-offs dominate practical workloads.",),
            (
                ObservationPrediction(
                    "codec-public-benchmark",
                    {"beats_baseline": 0.10, "ties": 0.35, "loses": 0.55},
                ),
                ObservationPrediction(
                    "codec-blind-perceptual",
                    {"preferred": 0.20, "neutral": 0.35, "not_preferred": 0.45},
                ),
            ),
            epistemic_label="baseline",
        ),
        PossibleWorld(
            "codec-multiscale-gain",
            "Multiscale semantic representation yields selective gains",
            0.35,
            ("Semantic salience can improve rate-distortion on selected image classes.",),
            (
                ObservationPrediction(
                    "codec-public-benchmark",
                    {"beats_baseline": 0.60, "ties": 0.25, "loses": 0.15},
                ),
                ObservationPrediction(
                    "codec-blind-perceptual",
                    {"preferred": 0.65, "neutral": 0.20, "not_preferred": 0.15},
                ),
            ),
        ),
        PossibleWorld(
            "codec-overfit",
            "Apparent gain is dataset or metric overfit",
            0.15,
            ("Prototype performs well only on development distributions.",),
            (
                ObservationPrediction(
                    "codec-public-benchmark",
                    {"beats_baseline": 0.45, "ties": 0.25, "loses": 0.30},
                ),
                ObservationPrediction(
                    "codec-blind-perceptual",
                    {"preferred": 0.25, "neutral": 0.30, "not_preferred": 0.45},
                ),
            ),
            epistemic_label="artifact_model",
        ),
    )
    experiments = (
        ExperimentCandidate(
            "codec-public-benchmark",
            "Public corpus rate-distortion benchmark",
            cost=1.0,
            time=1.0,
            risk=0.0,
            representativeness=0.85,
            robustness=0.85,
        ),
        ExperimentCandidate(
            "codec-blind-perceptual",
            "Blinded perceptual comparison",
            cost=2.0,
            time=2.0,
            risk=0.0,
            representativeness=0.95,
            robustness=0.95,
        ),
    )
    return WorldResearchProgram(
        "program-semantic-codec",
        worlds,
        experiments,
        (_candidate("semantic-image-codec"),),
    )


def space_anomaly_program() -> WorldResearchProgram:
    worlds = (
        PossibleWorld(
            "space-sensor-artifact",
            "Sensor/processing artifact explains anomaly",
            0.50,
            ("At least one sensor or processing pipeline is biased.",),
            (
                ObservationPrediction(
                    "cross-sensor-coincidence",
                    {"persists": 0.10, "disappears": 0.90},
                ),
                ObservationPrediction(
                    "reference-frame-reconstruction",
                    {"kinematic_anomaly": 0.10, "ordinary_motion": 0.90},
                ),
            ),
            epistemic_label="control",
        ),
        PossibleWorld(
            "space-ordinary-phenomenon",
            "Real but ordinary physical phenomenon",
            0.35,
            ("The observation is real but follows known physics.",),
            (
                ObservationPrediction(
                    "cross-sensor-coincidence",
                    {"persists": 0.70, "disappears": 0.30},
                ),
                ObservationPrediction(
                    "reference-frame-reconstruction",
                    {"kinematic_anomaly": 0.15, "ordinary_motion": 0.85},
                ),
            ),
        ),
        PossibleWorld(
            "space-unknown-mechanism",
            "Residual unknown mechanism",
            0.15,
            ("A real observation remains anomalous after sensor and frame controls.",),
            (
                ObservationPrediction(
                    "cross-sensor-coincidence",
                    {"persists": 0.85, "disappears": 0.15},
                ),
                ObservationPrediction(
                    "reference-frame-reconstruction",
                    {"kinematic_anomaly": 0.75, "ordinary_motion": 0.25},
                ),
            ),
            epistemic_label="residual_hypothesis",
        ),
    )
    experiments = (
        ExperimentCandidate(
            "cross-sensor-coincidence",
            "Independent cross-sensor persistence test",
            cost=1.0,
            time=1.0,
            risk=0.0,
            representativeness=0.95,
            robustness=0.95,
        ),
        ExperimentCandidate(
            "reference-frame-reconstruction",
            "Reference-frame and calibration reconstruction",
            cost=1.5,
            time=1.5,
            risk=0.0,
            representativeness=0.9,
            robustness=1.0,
        ),
    )
    return WorldResearchProgram(
        "program-space-anomaly",
        worlds,
        experiments,
        (),
    )


def physiology_program() -> WorldResearchProgram:
    worlds = (
        PossibleWorld(
            "physiology-no-added-value",
            "Additional weak-field channels add no reliable information",
            0.55,
            ("Standard validated modalities capture the useful signal.",),
            (
                ObservationPrediction(
                    "multimodal-blind-validation",
                    {"generalizes": 0.10, "no_gain": 0.90},
                ),
            ),
            epistemic_label="baseline",
        ),
        PossibleWorld(
            "physiology-multimodal-gain",
            "Multimodal fusion yields reproducible non-diagnostic state information",
            0.35,
            ("Independent low-intensity modalities contain complementary signal.",),
            (
                ObservationPrediction(
                    "multimodal-blind-validation",
                    {"generalizes": 0.70, "no_gain": 0.30},
                ),
            ),
        ),
        PossibleWorld(
            "physiology-artifact",
            "Apparent signal is leakage, motion or contextual artifact",
            0.10,
            ("Development data contain confounds.",),
            (
                ObservationPrediction(
                    "multimodal-blind-validation",
                    {"generalizes": 0.20, "no_gain": 0.80},
                ),
            ),
            epistemic_label="artifact_model",
        ),
    )
    experiments = (
        ExperimentCandidate(
            "multimodal-blind-validation",
            "Blinded held-out multimodal validation",
            cost=3.0,
            time=3.0,
            risk=0.15,
            feasibility=0.8,
            representativeness=0.95,
            robustness=0.95,
            requires_human_approval=True,
        ),
    )
    return WorldResearchProgram(
        "program-physiology-multimodal",
        worlds,
        experiments,
        (_candidate("tesla-resonance-coupling"), _candidate("kardec-latent-mediator")),
    )


def ancient_knowledge_program() -> WorldResearchProgram:
    worlds = (
        PossibleWorld(
            "ancient-independent-symbolic",
            "Similar motifs arise independently from common human/environmental constraints",
            0.45,
            ("Convergent cultural evolution explains similarities.",),
            (
                ObservationPrediction(
                    "textual-dependency-test",
                    {"documented_dependency": 0.25, "independent": 0.75},
                ),
                ObservationPrediction(
                    "archaeological-residual-test",
                    {"independent_residual": 0.20, "no_residual": 0.80},
                ),
            ),
            epistemic_label="baseline",
        ),
        PossibleWorld(
            "ancient-cultural-transmission",
            "Historical transmission explains a significant motif subset",
            0.40,
            ("Trade, migration or textual contact transmitted motifs.",),
            (
                ObservationPrediction(
                    "textual-dependency-test",
                    {"documented_dependency": 0.75, "independent": 0.25},
                ),
                ObservationPrediction(
                    "archaeological-residual-test",
                    {"independent_residual": 0.35, "no_residual": 0.65},
                ),
            ),
        ),
        PossibleWorld(
            "ancient-unresolved-residual",
            "A subset remains unexplained after dependency and convergence controls",
            0.15,
            ("Some residual pattern has no adequate current account.",),
            (
                ObservationPrediction(
                    "textual-dependency-test",
                    {"documented_dependency": 0.35, "independent": 0.65},
                ),
                ObservationPrediction(
                    "archaeological-residual-test",
                    {"independent_residual": 0.80, "no_residual": 0.20},
                ),
            ),
            epistemic_label="residual_hypothesis",
        ),
    )
    experiments = (
        ExperimentCandidate(
            "textual-dependency-test",
            "Chronology and textual-dependency reconstruction",
            cost=1.0,
            time=2.0,
            risk=0.0,
            representativeness=0.9,
            robustness=0.95,
        ),
        ExperimentCandidate(
            "archaeological-residual-test",
            "Independent archaeological residual test",
            cost=4.0,
            time=5.0,
            risk=0.05,
            feasibility=0.6,
            representativeness=0.95,
            robustness=1.0,
        ),
    )
    return WorldResearchProgram(
        "program-ancient-knowledge",
        worlds,
        experiments,
        (
            _candidate("miudinho-translation-integrity"),
            _candidate("jung-myth-symbolic-compression"),
            _candidate("atlantis-lemuria-mythic-residual"),
        ),
    )


def default_world_programs() -> tuple[WorldResearchProgram, ...]:
    return (
        semantic_codec_program(),
        space_anomaly_program(),
        physiology_program(),
        ancient_knowledge_program(),
    )
