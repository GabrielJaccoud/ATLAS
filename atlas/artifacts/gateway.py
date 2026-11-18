from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ArtifactKind(str, Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    ARCHIVE = "archive"
    DATASET = "dataset"
    CODE = "code"
    UNKNOWN = "unknown"


DOCUMENT_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".odt", ".rtf", ".txt", ".md", ".epub",
    ".ppt", ".pptx", ".odp", ".xls", ".xlsx", ".ods", ".csv", ".tsv",
}
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".tif", ".tiff",
    ".bmp", ".svg", ".heic", ".heif", ".jxl", ".dng", ".raw",
}
AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".gz", ".tgz", ".7z"}
DATA_EXTENSIONS = {".json", ".jsonl", ".parquet", ".feather", ".xml", ".yaml", ".yml"}
CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".cpp",
    ".c", ".h", ".html", ".css", ".sql", ".sh",
}


@dataclass(frozen=True)
class ArtifactRequest:
    filename: str
    operations: tuple[str, ...]
    preserve_original: bool = True
    target_formats: tuple[str, ...] = ()
    private: bool = True


@dataclass(frozen=True)
class ArtifactPlan:
    kind: ArtifactKind
    extension: str
    parser: str
    preserve_original: bool
    operations: tuple[str, ...]
    conversion_targets: tuple[str, ...]
    requires_sandbox: bool
    notes: tuple[str, ...]


class ArtifactGateway:
    """Routes uploaded artifacts to safe, format-aware processing pipelines."""

    def classify(self, filename: str) -> ArtifactKind:
        ext = Path(filename).suffix.lower()
        if ext in DOCUMENT_EXTENSIONS:
            return ArtifactKind.DOCUMENT
        if ext in IMAGE_EXTENSIONS:
            return ArtifactKind.IMAGE
        if ext in AUDIO_EXTENSIONS:
            return ArtifactKind.AUDIO
        if ext in VIDEO_EXTENSIONS:
            return ArtifactKind.VIDEO
        if ext in ARCHIVE_EXTENSIONS:
            return ArtifactKind.ARCHIVE
        if ext in DATA_EXTENSIONS:
            return ArtifactKind.DATASET
        if ext in CODE_EXTENSIONS:
            return ArtifactKind.CODE
        return ArtifactKind.UNKNOWN

    def plan(self, request: ArtifactRequest) -> ArtifactPlan:
        ext = Path(request.filename).suffix.lower()
        kind = self.classify(request.filename)

        parser = {
            ArtifactKind.DOCUMENT: "document_pipeline",
            ArtifactKind.IMAGE: "image_pipeline",
            ArtifactKind.AUDIO: "audio_pipeline",
            ArtifactKind.VIDEO: "video_pipeline",
            ArtifactKind.ARCHIVE: "archive_pipeline",
            ArtifactKind.DATASET: "data_pipeline",
            ArtifactKind.CODE: "code_pipeline",
            ArtifactKind.UNKNOWN: "quarantine_and_inspect",
        }[kind]

        notes: list[str] = []
        if ext == ".jxl":
            notes.extend([
                "Use JPEG XL capable codec such as libjxl/ImageMagick/libvips.",
                "Preserve ICC/HDR/metadata when requested.",
                "Generate AVIF/WebP/JPEG fallback for clients without JXL support.",
            ])

        if kind == ArtifactKind.ARCHIVE:
            notes.append("Inspect archive contents before extraction and enforce size/path limits.")

        if kind == ArtifactKind.UNKNOWN:
            notes.append("Do not execute unknown content; inspect MIME/signature first.")

        return ArtifactPlan(
            kind=kind,
            extension=ext,
            parser=parser,
            preserve_original=request.preserve_original,
            operations=request.operations,
            conversion_targets=request.target_formats,
            requires_sandbox=True,
            notes=tuple(notes),
        )
