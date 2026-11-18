from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class EvidenceStrength(IntEnum):
    UNVERIFIED = 0
    INDIRECT = 1
    EDITED_PRIMARY = 2
    OBJECT_LINKED = 3
    MULTI_SOURCE = 4


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    source_id: str
    claim_fragment: str
    object_id: str | None = None
    text_reference: str | None = None
    transliteration_ref: str | None = None
    translation_ref: str | None = None
    bibliography_refs: tuple[str, ...] = ()
    strength: EvidenceStrength = EvidenceStrength.UNVERIFIED
    notes: str = ""


@dataclass(frozen=True)
class ClaimAssessment:
    claim: str
    status: str
    confidence: float
    supporting_ids: tuple[str, ...]
    contrary_ids: tuple[str, ...]
    reason: str


class EvidenceDossier:
    """Builds auditable claim chains without converting interpretation into proof."""

    def assess(
        self,
        claim: str,
        supporting: tuple[EvidenceItem, ...],
        contrary: tuple[EvidenceItem, ...] = (),
    ) -> ClaimAssessment:
        if not supporting:
            return ClaimAssessment(
                claim,
                "unsupported",
                0.0,
                (),
                tuple(x.evidence_id for x in contrary),
                "No supporting evidence items.",
            )

        strongest = max(int(x.strength) for x in supporting)
        object_linked = sum(x.strength >= EvidenceStrength.OBJECT_LINKED for x in supporting)
        edited = sum(x.strength >= EvidenceStrength.EDITED_PRIMARY for x in supporting)

        confidence = min(
            0.95,
            0.20
            + strongest * 0.15
            + min(0.25, object_linked * 0.10)
            + min(0.15, edited * 0.05),
        )

        if contrary:
            confidence = max(0.05, confidence - min(0.35, 0.10 * len(contrary)))
            status = "contested"
            reason = "Supporting evidence exists, but material contrary evidence remains."
        elif strongest >= EvidenceStrength.OBJECT_LINKED and edited >= 1:
            status = "supported"
            reason = "Claim has object-linked and scholarly-edition support."
        else:
            status = "provisional"
            reason = "Evidence exists but does not yet form a strong object-linked chain."

        return ClaimAssessment(
            claim,
            status,
            confidence,
            tuple(x.evidence_id for x in supporting),
            tuple(x.evidence_id for x in contrary),
            reason,
        )
