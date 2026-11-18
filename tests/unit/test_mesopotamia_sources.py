from atlas.evidence import EvidenceDossier, EvidenceItem, EvidenceStrength
from atlas.knowledge.sources import SourceRegistry, SourceTier


def test_anunnaki_sources_include_reference_layers():
    sources = SourceRegistry().by_scope("anunnaki")
    assert sources
    assert any(s.tier == SourceTier.SCHOLARLY_REFERENCE for s in sources)


def test_royal_inscriptions_have_primary_edition_source():
    sources = SourceRegistry().by_scope("royal_inscriptions")
    assert any(s.source_id == "etcsri" for s in sources)


def test_evidence_dossier_rewards_object_linked_support():
    item = EvidenceItem(
        "e1",
        "cdli",
        "A named ruler is attested on an object.",
        object_id="P000001",
        strength=EvidenceStrength.OBJECT_LINKED,
    )
    assessment = EvidenceDossier().assess("Ruler attested", (item,))
    assert assessment.status in {"supported", "provisional"}
    assert assessment.confidence > 0.5
