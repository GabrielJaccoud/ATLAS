from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SupportService(str, Enum):
    DIAGNOSE = "diagnose"
    REPAIR = "repair"
    MAINTAIN = "maintain"
    TOOLING = "tooling"
    CAPABILITY_BUILD = "capability_build"
    CAPABILITY_EXPANSION = "capability_expansion"
    TESTING = "testing"
    MIGRATION = "migration"
    DOCUMENTATION = "documentation"
    OBSERVABILITY = "observability"
    RECOVERY = "recovery"


@dataclass(frozen=True)
class SupportRequest:
    request_id: str
    requester: str
    symptom: str
    desired_outcome: str
    requested_services: tuple[SupportService, ...]
    severity: float = 0.0
    requires_code_change: bool = False
    requires_new_tool: bool = False
    touches_constitution: bool = False
    external_effect: bool = False


@dataclass(frozen=True)
class SupportPlan:
    request_id: str
    services: tuple[SupportService, ...]
    route_to_codex: bool
    route_to_guardian: bool
    route_to_ria: bool
    sandbox_required: bool
    human_approval_required: bool
    steps: tuple[str, ...]


class SupportCell:
    """Internal service/repair/capability workshop for all ATLAS ministries and organs."""

    def plan(self, request: SupportRequest) -> SupportPlan:
        services = tuple(dict.fromkeys(request.requested_services))
        code = request.requires_code_change or any(
            s in services for s in (
                SupportService.REPAIR,
                SupportService.TOOLING,
                SupportService.CAPABILITY_BUILD,
                SupportService.CAPABILITY_EXPANSION,
                SupportService.MIGRATION,
            )
        )

        guardian = request.touches_constitution
        ria = any(
            s in services for s in (
                SupportService.CAPABILITY_BUILD,
                SupportService.CAPABILITY_EXPANSION,
                SupportService.TOOLING,
            )
        )
        sandbox = code or request.severity >= 0.5
        approval = (
            request.touches_constitution
            or request.external_effect
            or request.severity >= 0.8
        )

        steps = [
            "diagnose_request_and_capture_current_state",
            "identify_root_cause_or_capability_gap",
            "select_minimal_reversible_intervention",
        ]
        if code:
            steps.append("delegate_engineering_work_to_codex_or_equivalent")
        if ria:
            steps.append("evaluate_new_capability_with_RIA")
        if sandbox:
            steps.append("test_in_sandbox_and_compare_against_baseline")
        steps.extend([
            "verify_no_regression",
            "update_documentation_and_event_ledger",
            "report_result_to_requester_and_awareness",
        ])

        return SupportPlan(
            request_id=request.request_id,
            services=services,
            route_to_codex=code,
            route_to_guardian=guardian,
            route_to_ria=ria,
            sandbox_required=sandbox,
            human_approval_required=approval,
            steps=tuple(steps),
        )
