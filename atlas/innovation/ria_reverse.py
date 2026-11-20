from __future__ import annotations

from dataclasses import dataclass

from .forge import HypothesisForge, MinistryAssessment, TechnologySeed
from .ministry_router import MinistryInnovationRouter


@dataclass(frozen=True)
class HypothesisSource:
    source_id: str
    title: str
    family: str
    epistemic_class: str
    core_claims: tuple[str, ...]
    source_notes: str = ""


@dataclass(frozen=True)
class ReverseEngineeringCandidate:
    candidate_id: str
    source_ids: tuple[str, ...]
    mechanism: str
    capability: str
    technology_seed: TechnologySeed
    tags: tuple[str, ...]
    assumptions_required: tuple[str, ...] = ()
    useful_if_false: bool = True
    test_protocols: tuple[str, ...] = ()


@dataclass(frozen=True)
class RIAReverseResult:
    candidate_id: str
    ministry_assessments: tuple[MinistryAssessment, ...]
    status: str
    score: float
    requires_human_approval: bool
    required_reviews: tuple[str, ...]
    test_protocols: tuple[str, ...]
    assumptions_required: tuple[str, ...]


class RIAReverseEngineering:
    def __init__(self) -> None:
        self.router = MinistryInnovationRouter()
        self.forge = HypothesisForge()

    def evaluate(self, candidate: ReverseEngineeringCandidate) -> RIAReverseResult:
        route = self.router.route(candidate.technology_seed, candidate.tags)
        decision = self.forge.evaluate_seed(candidate.technology_seed, route.assessments)
        return RIAReverseResult(
            candidate_id=candidate.candidate_id,
            ministry_assessments=route.assessments,
            status=decision.status,
            score=decision.score,
            requires_human_approval=decision.requires_human_approval,
            required_reviews=decision.required_reviews,
            test_protocols=candidate.test_protocols,
            assumptions_required=candidate.assumptions_required,
        )


def default_reverse_engineering_candidates() -> tuple[ReverseEngineeringCandidate, ...]:
    return (
        ReverseEngineeringCandidate(
            candidate_id="miudinho-translation-integrity",
            source_ids=("honorio-miudinho", "bereshit-severino", "torah", "quran"),
            mechanism="Microscopic textual decomposition and translation-variant comparison.",
            capability="translation_integrity_engine",
            technology_seed=TechnologySeed(
                "seed-translation-integrity",
                "Translation Integrity Engine",
                ("microtext-analysis",),
                "Trace meaning changes from source language through translation and commentary.",
                ("education_human", "research_evolution", "math_coherence"),
                0.75, 0.95, 1.0, 0.9, 0.05,
                acceptance_tests=("recover_source_term_lineage", "detect_semantic_drift"),
            ),
            tags=("language", "symbol", "hypothesis", "causal"),
            test_protocols=("parallel_translation_benchmark", "expert_blind_review"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="einstein-plato-reference-invariants",
            source_ids=("einstein", "plato", "kant"),
            mechanism="Change representation or reference frame and isolate invariants.",
            capability="reference_frame_invariant_finder",
            technology_seed=TechnologySeed(
                "seed-invariant-finder",
                "Invariant Finder",
                ("reference-frame", "formal-model"),
                "Detect conclusions that survive changes in observer, encoding or model.",
                ("math_coherence", "science_frontiers", "research_evolution"),
                0.85, 0.95, 1.0, 0.9, 0.02,
                acceptance_tests=("known_invariant_recovery", "false_invariant_rejection"),
            ),
            tags=("math", "causal", "hypothesis", "metascience"),
            test_protocols=("synthetic_reference_frame_suite",),
        ),
        ReverseEngineeringCandidate(
            candidate_id="tesla-resonance-coupling",
            source_ids=("tesla", "crookes", "haramein", "keshe"),
            mechanism="Search measurable oscillation, coupling, coherence and resonance before interpreting causes.",
            capability="resonance_coupling_mapper",
            technology_seed=TechnologySeed(
                "seed-resonance",
                "Resonance & Coupling Mapper",
                ("spectral-analysis", "coupling"),
                "Identify spectral structure, phase-locking and cross-sensor coupling.",
                ("math_coherence", "science_frontiers", "health_wellbeing"),
                0.82, 0.90, 0.95, 0.75, 0.25, 0.15,
                acceptance_tests=("recover_known_coupling", "control_false_discovery_rate"),
            ),
            tags=("signal", "spectral", "physics", "sensor", "body"),
            assumptions_required=("None for ordinary signal analysis.",),
            test_protocols=("negative_controls", "surrogate_data", "blinded_sensor_tests"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="jung-myth-symbolic-compression",
            source_ids=("jung", "torah", "quran", "apocrypha", "sumerian", "plato"),
            mechanism="Compress recurring relational motifs without assuming common supernatural origin.",
            capability="symbolic_structural_compression",
            technology_seed=TechnologySeed(
                "seed-symbolic-compression",
                "Symbolic Knowledge Compression",
                ("archetype-structure", "graph-compression"),
                "Represent recurring motifs as reusable graph primitives.",
                ("education_human", "creation_design", "research_evolution"),
                0.83, 0.82, 1.0, 0.7, 0.05,
                acceptance_tests=("cross_corpus_retrieval_gain", "avoid_false_universalization"),
            ),
            tags=("symbol", "cognition", "compression", "hypothesis"),
            test_protocols=("cross_cultural_holdout", "dependency_control"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="kardec-latent-mediator",
            source_ids=("kardec-genesis", "jung", "lipton"),
            mechanism="Model unobserved mediators between cause, context and measured effect.",
            capability="latent_mediator_discovery",
            technology_seed=TechnologySeed(
                "seed-latent-mediator",
                "Latent Mediator Discovery",
                ("latent-variable", "causal-inference"),
                "Propose and test hidden intermediate variables without presuming metaphysical identity.",
                ("math_coherence", "research_evolution", "health_wellbeing"),
                0.78, 0.90, 0.95, 0.75, 0.25, 0.25,
                acceptance_tests=("recover_hidden_mediator_synthetic", "out_of_sample_causal_gain"),
            ),
            tags=("causal", "biology", "health", "hypothesis"),
            assumptions_required=("Metaphysical interpretation not required for the computational method.",),
            test_protocols=("causal_graph_ablation", "intervention_test"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="saba-egypt-resilience",
            source_ids=("saba-marib", "egypt-pyramids"),
            mechanism="Treat infrastructure as flow + maintenance + governance + logistics.",
            capability="civilizational_resilience_simulator",
            technology_seed=TechnologySeed(
                "seed-civilizational-resilience",
                "Civilizational Resilience Simulator",
                ("resource-flow", "maintenance", "logistics"),
                "Model maintenance debt, bottlenecks, failures and recovery across long horizons.",
                ("architecture_environment", "business_ventures", "research_evolution"),
                0.80, 0.92, 1.0, 0.9, 0.08,
                acceptance_tests=("historical_failure_reconstruction", "scenario_sensitivity"),
            ),
            tags=("environment", "spatial", "product", "experiment"),
            test_protocols=("historical_backtest", "counterfactual_scenarios"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="wakanda-material-platform",
            source_ids=("wakanda-fiction",),
            mechanism="A programmable multifunctional material acts as a shared technological substrate.",
            capability="programmable_material_platform_research",
            technology_seed=TechnologySeed(
                "seed-programmable-material",
                "Programmable Multifunctional Material Platform",
                ("smart-materials", "energy-management", "embedded-sensing"),
                "Explore real materials that combine sensing, damping, energy storage and communication.",
                ("science_frontiers", "creation_design", "research_evolution"),
                0.96, 0.65, 0.85, 0.45, 0.30, 0.20,
                acceptance_tests=("multi_function_material_benchmark", "energy_balance"),
            ),
            tags=("materials", "sensor", "physics", "image"),
            assumptions_required=("Vibranium is fictional; only functional requirements are transferred.",),
            test_protocols=("materials_screening", "finite_element_simulation", "prototype_benchmark"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="wakanda-kimoyo-personal-node",
            source_ids=("wakanda-fiction",),
            mechanism="Wearable identity, communication, sensing and context node.",
            capability="personal_context_node",
            technology_seed=TechnologySeed(
                "seed-personal-context-node",
                "ATLAS Personal Context Node",
                ("wearable", "identity", "sensor-fusion"),
                "Create a privacy-preserving wearable/mobile edge node for ATLAS.",
                ("creation_design", "science_frontiers", "governance_ethics"),
                0.88, 0.90, 0.95, 0.85, 0.20, 0.30,
                acceptance_tests=("offline_identity", "encrypted_sensor_sync", "consent_controls"),
            ),
            tags=("interface", "sensor", "privacy", "product"),
            test_protocols=("threat_model", "battery_latency_benchmark"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="flower-life-geometry-search",
            source_ids=("flower-of-life-v1", "flower-of-life-v2", "plato", "haramein"),
            mechanism="Generate geometric hypotheses and test them against measured structures instead of assuming sacred causation.",
            capability="geometry_hypothesis_search",
            technology_seed=TechnologySeed(
                "seed-geometry-search",
                "Geometry Hypothesis Search",
                ("geometric-generator", "multiscale-search"),
                "Test candidate symmetries, ratios, tilings and transforms against data.",
                ("math_coherence", "creation_design", "science_frontiers"),
                0.80, 0.92, 1.0, 0.55, 0.05,
                acceptance_tests=("recover_known_symmetry", "multiple_testing_correction"),
            ),
            tags=("geometry", "math", "image", "physics"),
            assumptions_required=("Sacred or consciousness claims are not required for geometric testing.",),
            test_protocols=("null_model_comparison", "out_of_sample_geometry_fit"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="atlantis-lemuria-mythic-residual",
            source_ids=("plato-atlantis", "lemuria-sclater", "lemuria-blavatsky"),
            mechanism="Separate literary, obsolete scientific and esoteric layers; search only for independently testable residuals.",
            capability="mythic_residual_engine",
            technology_seed=TechnologySeed(
                "seed-mythic-residual",
                "Mythic Residual Engine",
                ("source-genealogy", "geospatial-evidence"),
                "Generate archaeological/geological tests from myths without treating myths as measurements.",
                ("research_evolution", "science_frontiers", "education_human"),
                0.72, 0.84, 1.0, 0.65, 0.05,
                acceptance_tests=("source_dependency_detection", "known_event_recovery"),
            ),
            tags=("hypothesis", "space", "environment", "language"),
            test_protocols=("source_genealogy", "geospatial_cross_validation", "negative_controls"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="dimensions-layer-model",
            source_ids=("cern-extra-dimensions", "flower-of-life-v2", "kardec-genesis"),
            mechanism="Keep mathematical dimensions, hidden-state dimensions and metaphysical dimensions in separate ontologies.",
            capability="dimensional_ontology_and_projection_engine",
            technology_seed=TechnologySeed(
                "seed-dimensional-ontology",
                "Dimensional Ontology & Projection Engine",
                ("dimension-types", "projection", "hidden-state"),
                "Model high-dimensional systems and projections without conflating physics with metaphysics.",
                ("math_coherence", "science_frontiers", "research_evolution"),
                0.90, 0.95, 1.0, 0.85, 0.05,
                acceptance_tests=("dimension_type_separation", "projection_reconstruction"),
            ),
            tags=("math", "physics", "causal", "hypothesis"),
            test_protocols=("synthetic_manifold_tests", "physics_vs_metaphysics_label_audit"),
        ),
        ReverseEngineeringCandidate(
            candidate_id="semantic-image-codec",
            source_ids=("shannon", "flower-of-life-v1", "predictive-processing"),
            mechanism="Combine rate-distortion, multiscale geometry and semantic salience.",
            capability="experimental_semantic_image_codec",
            technology_seed=TechnologySeed(
                "seed-image-codec",
                "Multiscale Semantic Image Codec",
                ("rate-distortion", "multiscale", "semantic-salience"),
                "Research an image codec that may outperform existing codecs on selected workloads.",
                ("math_coherence", "creation_design", "research_evolution"),
                0.95, 0.92, 1.0, 0.65, 0.05,
                acceptance_tests=(
                    "benchmark_against_jxl",
                    "benchmark_against_avif",
                    "lossless_roundtrip_when_claimed",
                    "decode_cost_budget",
                ),
            ),
            tags=("compression", "image", "math", "experiment"),
            test_protocols=("public_dataset_benchmark", "blind_perceptual_test", "rate_distortion_curve"),
        ),
    )
