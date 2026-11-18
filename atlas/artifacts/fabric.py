from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from typing import Iterable


@dataclass(frozen=True)
class ArtifactVersion:
    artifact_id: str
    version_id: str
    filename: str
    media_type: str
    byte_length: int
    checksum_sha256: str
    parent_version_id: str | None = None
    derived_from: tuple[str, ...] = ()
    transformations: tuple[str, ...] = ()
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ArtifactFamily:
    family_id: str
    canonical_artifact_id: str
    versions: tuple[ArtifactVersion, ...]


class ArtifactFabric:
    def checksum(self, content: bytes) -> str:
        return sha256(content).hexdigest()

    def new_version(
        self,
        *,
        artifact_id: str,
        version_id: str,
        filename: str,
        media_type: str,
        content: bytes,
        parent_version_id: str | None = None,
        derived_from: Iterable[str] = (),
        transformations: Iterable[str] = (),
        metadata: dict[str, object] | None = None,
    ) -> ArtifactVersion:
        return ArtifactVersion(
            artifact_id=artifact_id,
            version_id=version_id,
            filename=filename,
            media_type=media_type,
            byte_length=len(content),
            checksum_sha256=self.checksum(content),
            parent_version_id=parent_version_id,
            derived_from=tuple(derived_from),
            transformations=tuple(transformations),
            metadata=metadata or {},
        )

    def lineage(self, family: ArtifactFamily, version_id: str) -> tuple[ArtifactVersion, ...]:
        by_id = {v.version_id: v for v in family.versions}
        out: list[ArtifactVersion] = []
        current = by_id.get(version_id)
        while current:
            out.append(current)
            current = by_id.get(current.parent_version_id) if current.parent_version_id else None
        return tuple(out)
