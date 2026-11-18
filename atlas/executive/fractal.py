from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json


@dataclass(frozen=True)
class FractalIdentity:
    ministry_id: str
    atlas_identity_version: str
    constitutional_invariants: tuple[str, ...]
    ministry_mandate: str
    local_priorities: tuple[str, ...] = ()
    allowed_autonomy: tuple[str, ...] = (
        "research",
        "analyze",
        "simulate",
        "draft",
        "propose",
    )

    def continuity_hash(self) -> str:
        payload = {
            "ministry_id": self.ministry_id,
            "atlas_identity_version": self.atlas_identity_version,
            "constitutional_invariants": self.constitutional_invariants,
            "ministry_mandate": self.ministry_mandate,
            "local_priorities": self.local_priorities,
            "allowed_autonomy": self.allowed_autonomy,
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MinistrySelfState:
    ministry_id: str
    health: float = 1.0
    confidence: float = 0.5
    uncertainty: float = 0.5
    evidence_coverage: float = 0.5
    queue_depth: int = 0
    blocked_dependencies: tuple[str, ...] = ()
    unresolved_contradictions: tuple[str, ...] = ()
    active_research: tuple[str, ...] = ()
    recent_discoveries: tuple[str, ...] = ()
    recent_errors: tuple[str, ...] = ()
    proposed_capabilities: tuple[str, ...] = ()
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def normalized_health(self) -> float:
        penalty = min(0.6, len(self.recent_errors) * 0.08 + len(self.blocked_dependencies) * 0.05)
        return max(0.0, min(1.0, self.health - penalty))


@dataclass(frozen=True)
class MinistryFractal:
    identity: FractalIdentity
    state: MinistrySelfState

    def may(self, action: str) -> bool:
        return action in self.identity.allowed_autonomy

    def requires_global_review(self, action: str) -> bool:
        return action not in self.identity.allowed_autonomy or action in {
            "external_write",
            "irreversible_action",
            "constitutional_change",
            "permission_elevation",
            "self_modify_runtime",
        }
