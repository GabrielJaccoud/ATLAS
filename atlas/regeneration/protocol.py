from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True)
class Checkpoint:
    checkpoint_id: str
    component: str
    version: str
    state: dict[str, object]
    healthy: bool = True

    def digest(self) -> str:
        payload = json.dumps({
            "component": self.component,
            "version": self.version,
            "state": self.state,
            "healthy": self.healthy,
        }, sort_keys=True, default=str)
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RegenerationPlan:
    component: str
    source_checkpoint: str
    isolate: bool
    steps: tuple[str, ...]
    requires_human_approval: bool


class RegenerationProtocol:
    def plan(self, failed_component: str, checkpoints: tuple[Checkpoint, ...], *, risk: float = 0.0) -> RegenerationPlan:
        healthy = [c for c in checkpoints if c.component == failed_component and c.healthy]
        if not healthy:
            raise ValueError("No healthy checkpoint available for component.")
        source = healthy[-1]
        return RegenerationPlan(
            component=failed_component,
            source_checkpoint=source.checkpoint_id,
            isolate=True,
            steps=(
                "isolate_failed_component",
                "capture_failure_state",
                "restore_known_good_checkpoint",
                "reapply_safe_delta_if_available",
                "run_regression_tests",
                "observe_post_recovery_health",
                "record_incident_and_resolution",
            ),
            requires_human_approval=risk >= 0.7,
        )
