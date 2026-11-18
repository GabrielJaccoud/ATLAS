from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Authority(str, Enum):
    READ = "read"
    PROPOSE = "propose"
    SIMULATE = "simulate"
    EXECUTE_REVERSIBLE = "execute_reversible"
    EXECUTE_EXTERNAL = "execute_external"
    CONSTITUTIONAL_CHANGE = "constitutional_change"


@dataclass(frozen=True)
class AgentRole:
    role_id: str
    title: str
    purpose: str
    skills: tuple[str, ...] = ()
    authorities: tuple[Authority, ...] = (Authority.READ, Authority.PROPOSE)
    requires_human_approval: bool = False


@dataclass(frozen=True)
class Ministry:
    ministry_id: str
    name: str
    mandate: str
    ontology: tuple[str, ...]
    skills: tuple[str, ...]
    allowed_tools: tuple[str, ...] = ()
    memory_scope: tuple[str, ...] = ()
    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    indicators: tuple[str, ...] = ()
    relationships: tuple[str, ...] = ()
    roles: tuple[AgentRole, ...] = ()
    transversal: bool = False
    budget_weight: float = 1.0


@dataclass(frozen=True)
class Mission:
    mission_id: str
    objective: str
    required_skills: tuple[str, ...]
    domains: tuple[str, ...] = ()
    risk: float = 0.0
    external_action: bool = False
    irreversible: bool = False
    context_capsule_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class MissionRoute:
    mission_id: str
    primary_ministries: tuple[str, ...]
    transversal_bodies: tuple[str, ...]
    missing_skills: tuple[str, ...]
    human_approval_required: bool
    rationale: tuple[str, ...]
