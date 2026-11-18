from atlas.artifacts import ArtifactGateway, ArtifactKind, ArtifactRequest


def test_jxl_routes_to_image_pipeline_with_fallback_note():
    plan = ArtifactGateway().plan(ArtifactRequest(
        filename="image.jxl",
        operations=("analyze", "enhance"),
        target_formats=("png", "avif"),
    ))
    assert plan.kind == ArtifactKind.IMAGE
    assert plan.parser == "image_pipeline"
    assert any("fallback" in note.lower() for note in plan.notes)


def test_office_document_routes_to_document_pipeline():
    plan = ArtifactGateway().plan(ArtifactRequest(
        filename="report.docx",
        operations=("summarize", "edit"),
    ))
    assert plan.kind == ArtifactKind.DOCUMENT
    assert plan.parser == "document_pipeline"


def test_unknown_extension_is_quarantined():
    plan = ArtifactGateway().plan(ArtifactRequest(
        filename="mystery.xyzabc",
        operations=("inspect",),
    ))
    assert plan.kind == ArtifactKind.UNKNOWN
    assert plan.parser == "quarantine_and_inspect"
