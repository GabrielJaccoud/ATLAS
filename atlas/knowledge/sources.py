from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SourceTier(str, Enum):
    PRIMARY_OBJECT = "primary_object"
    PRIMARY_EDITION = "primary_edition"
    SCHOLARLY_REFERENCE = "scholarly_reference"
    SECONDARY_SYNTHESIS = "secondary_synthesis"
    MODERN_INTERPRETATION = "modern_interpretation"
    FRINGE_CLAIM = "fringe_claim"


@dataclass(frozen=True)
class ResearchSource:
    source_id: str
    name: str
    base_url: str
    tier: SourceTier
    scope: tuple[str, ...]
    notes: str = ""
    active: bool = True


MESOPOTAMIA_SOURCES: tuple[ResearchSource, ...] = (
    ResearchSource(
        "cdli",
        "Cuneiform Digital Library Initiative",
        "https://cdli.earth/",
        SourceTier.PRIMARY_OBJECT,
        (
            "cuneiform_objects",
            "photos",
            "museum_metadata",
            "transliterations",
            "bibliography",
            "provenance",
            "king_list",
        ),
        "Core object-level registry. Prefer P/Q numbers and museum/accession identifiers.",
    ),
    ResearchSource(
        "etcsl",
        "Electronic Text Corpus of Sumerian Literature",
        "https://etcsl.orinst.ox.ac.uk/",
        SourceTier.PRIMARY_EDITION,
        (
            "sumerian_literature",
            "transliteration",
            "translation",
            "myth",
            "royal_poetry",
            "letters",
            "laments",
            "proverbs",
            "king_list",
        ),
        "Composite scholarly editions; preserve lacunae and variant-source uncertainty.",
    ),
    ResearchSource(
        "etcsri",
        "Electronic Text Corpus of Sumerian Royal Inscriptions",
        "https://oracc.museum.upenn.edu/etcsri/",
        SourceTier.PRIMARY_EDITION,
        (
            "royal_inscriptions",
            "sumerian",
            "rulers",
            "temples",
            "wars",
            "building_inscriptions",
            "gudea",
            "ur_iii",
        ),
        "Lemmatized corpus linked to RIME and CDLI identifiers.",
    ),
    ResearchSource(
        "epsd2",
        "Electronic Pennsylvania Sumerian Dictionary 2",
        "https://oracc.museum.upenn.edu/epsd2/",
        SourceTier.SCHOLARLY_REFERENCE,
        (
            "lexicon",
            "lemma",
            "word_forms",
            "divine_names",
            "proper_names",
            "period_attestations",
            "anunnaki",
        ),
        "Use for lexical claims and occurrence counts; retain spelling and period distinctions.",
    ),
    ResearchSource(
        "oracc_amgg",
        "Ancient Mesopotamian Gods and Goddesses",
        "https://oracc.museum.upenn.edu/amgg/",
        SourceTier.SCHOLARLY_REFERENCE,
        (
            "deities",
            "anunna",
            "anunnaki",
            "genealogy",
            "cult",
            "iconography",
            "bibliography",
        ),
        "Use alongside primary-text attestations.",
    ),
    ResearchSource(
        "oracc_cams",
        "Corpus of Ancient Mesopotamian Scholarship",
        "https://oracc.museum.upenn.edu/cams/",
        SourceTier.PRIMARY_EDITION,
        (
            "scholarly_texts",
            "omens",
            "rituals",
            "astral_science",
            "commentaries",
            "magic",
            "anunnaki",
        ),
        "Important for later Mesopotamian learned traditions.",
    ),
    ResearchSource(
        "rime",
        "Royal Inscriptions of Mesopotamia — Early Periods",
        "https://oracc.museum.upenn.edu/etcsri/",
        SourceTier.SCHOLARLY_REFERENCE,
        (
            "presargonic",
            "sargonic",
            "gutian",
            "neo_sumerian",
            "old_babylonian",
            "royal_inscriptions",
        ),
        "Canonical edition family cross-referenced by ETCSRI.",
    ),
)


class SourceRegistry:
    def __init__(self, sources: tuple[ResearchSource, ...] = MESOPOTAMIA_SOURCES) -> None:
        self._sources = {s.source_id: s for s in sources}

    def get(self, source_id: str) -> ResearchSource:
        return self._sources[source_id]

    def by_scope(self, scope: str) -> tuple[ResearchSource, ...]:
        return tuple(
            source
            for source in self._sources.values()
            if scope in source.scope and source.active
        )

    def all(self) -> tuple[ResearchSource, ...]:
        return tuple(self._sources.values())
