from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewAgentRole:
    role_id: str
    title: str
    focus: str


_COMMON_ROLES = (
    ReviewAgentRole(
        "language_editor",
        "Revisão de linguagem",
        "Check Portuguese spelling, grammar, punctuation, clarity and terminology. Identify exact passages and suggest corrections without changing scientific meaning.",
    ),
    ReviewAgentRole(
        "structure_method",
        "Estrutura e método",
        "Review the scientific structure, question, assumptions, method, results, uncertainty, limitations and whether the conclusions follow from the reported work.",
    ),
    ReviewAgentRole(
        "evidence_red_team",
        "Evidências e contraevidências",
        "Challenge the strongest claims, identify missing evidence, alternative explanations, internal contradictions and references that require external verification. Do not invent sources or say you checked a source that was not provided.",
    ),
)

_DOMAIN_ROLES = {
    "mathematical_result": ReviewAgentRole(
        "formal_proof",
        "Revisão matemática",
        "Check definitions, assumptions, logical dependencies, proof gaps, counterexamples and whether the stated result follows from the proof. Do not certify a proof; show the exact step that needs a human mathematician's attention.",
    ),
    "theoretical_physics": ReviewAgentRole(
        "physical_model",
        "Revisão de modelo físico",
        "Check dimensional consistency, assumptions, compatibility with stated physical principles, testability and whether predictions are distinguishable. Keep theoretical viability separate from experimental confirmation.",
    ),
    "empirical_result": ReviewAgentRole(
        "empirical_methods",
        "Revisão empírica",
        "Review design, sampling, controls, measurements, uncertainty, statistics, reproducibility and possible confounders. Do not infer causality from association without justification.",
    ),
}


def roles_for_work(work_type: str) -> tuple[ReviewAgentRole, ...]:
    domain_role = _DOMAIN_ROLES.get(work_type)
    return (*_COMMON_ROLES, *((domain_role,) if domain_role else ()))
