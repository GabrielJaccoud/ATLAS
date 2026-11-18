from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringMission:
    mission_id: str
    objective: str
    repository: str
    branch: str
    acceptance_tests: tuple[str, ...]
    context_capsule_id: str
    privileged_change: bool = False


@dataclass(frozen=True)
class EngineeringPlan:
    mission_id: str
    executor: str
    require_pull_request: bool
    require_tests: bool
    require_ria: bool
    require_human_approval: bool


def plan_engineering(mission: EngineeringMission) -> EngineeringPlan:
    return EngineeringPlan(
        mission_id=mission.mission_id,
        executor="codex",
        require_pull_request=True,
        require_tests=True,
        require_ria=True,
        require_human_approval=mission.privileged_change,
    )
