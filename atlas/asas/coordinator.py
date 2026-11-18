from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Iterable

from atlas.executive.models import Mission, MissionRoute


@dataclass(frozen=True)
class ContextCapsule:
    capsule_id: str
    objective: str
    identity_kernel: dict[str, object]
    invariants: tuple[str, ...]
    relevant_memory: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()
    open_tasks: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    schema_version: str = "1.0"

    def integrity_hash(self) -> str:
        canonical = json.dumps({
            "capsule_id": self.capsule_id,
            "objective": self.objective,
            "identity_kernel": self.identity_kernel,
            "invariants": self.invariants,
            "relevant_memory": self.relevant_memory,
            "evidence_refs": self.evidence_refs,
            "uncertainties": self.uncertainties,
            "open_tasks": self.open_tasks,
            "permissions": self.permissions,
            "schema_version": self.schema_version,
        }, sort_keys=True, ensure_ascii=False, default=str)
        return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CoordinationPlan:
    mission_id: str
    capsule_id: str
    primary_ministries: tuple[str, ...]
    transversal_bodies: tuple[str, ...]
    dependency_edges: tuple[tuple[str, str], ...]
    synthesis_owner: str
    approval_required: bool
    unresolved_capabilities: tuple[str, ...] = ()


class ASASCoordinator:
    """Connective tissue between ATLAS, ministries and context.

    ASAS does not replace ministry expertise. It preserves the mission context,
    routes dependencies and returns a single integration path.
    """

    def build_capsule(
        self,
        mission: Mission,
        *,
        identity_kernel: dict[str, object],
        invariants: Iterable[str],
        relevant_memory: Iterable[str] = (),
        evidence_refs: Iterable[str] = (),
        uncertainties: Iterable[str] = (),
        open_tasks: Iterable[str] = (),
        permissions: Iterable[str] = (),
    ) -> ContextCapsule:
        return ContextCapsule(
            capsule_id=f"capsule:{mission.mission_id}",
            objective=mission.objective,
            identity_kernel=identity_kernel,
            invariants=tuple(invariants),
            relevant_memory=tuple(relevant_memory),
            evidence_refs=tuple(evidence_refs),
            uncertainties=tuple(uncertainties),
            open_tasks=tuple(open_tasks),
            permissions=tuple(permissions),
        )

    def coordinate(self, route: MissionRoute, capsule: ContextCapsule) -> CoordinationPlan:
        dependencies: list[tuple[str, str]] = []
        primaries = route.primary_ministries
        for i, source in enumerate(primaries):
            for target in primaries[i + 1:]:
                dependencies.append((source, target))

        return CoordinationPlan(
            mission_id=route.mission_id,
            capsule_id=capsule.capsule_id,
            primary_ministries=route.primary_ministries,
            transversal_bodies=route.transversal_bodies,
            dependency_edges=tuple(dependencies),
            synthesis_owner="integration_chamber",
            approval_required=route.human_approval_required,
            unresolved_capabilities=route.missing_skills,
        )
