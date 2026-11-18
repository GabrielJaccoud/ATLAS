from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CivilizationalPattern:
    pattern_id: str
    civilization: str
    problem: str
    solution: str
    evidence_refs: tuple[str, ...]
    domains: tuple[str, ...]
    durability_years: int | None = None
    maintenance_model: str | None = None
    transfer_candidates: tuple[str, ...] = ()


@dataclass(frozen=True)
class TechnologyLineage:
    lineage_id: str
    concept: str
    nodes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    independent_invention_possible: bool = True
    confidence: float = 0.5


class CivilizationalReconstructionEngine:
    """Extracts reusable mechanisms from historically evidenced civilizational systems."""

    def transferable_capabilities(
        self,
        pattern: CivilizationalPattern,
    ) -> tuple[str, ...]:
        capabilities: list[str] = []
        domains = set(pattern.domains)

        if "water" in domains or "infrastructure" in domains:
            capabilities.extend(
                (
                    "resource_flow_modeling",
                    "maintenance_scheduling",
                    "failure_cascade_simulation",
                    "resilience_planning",
                )
            )
        if "trade" in domains or "logistics" in domains:
            capabilities.extend(
                (
                    "route_intelligence",
                    "supply_network_modeling",
                    "bottleneck_detection",
                    "cross_region_exchange_graph",
                )
            )
        if "governance" in domains:
            capabilities.extend(
                (
                    "distributed_maintenance_governance",
                    "institutional_memory_modeling",
                    "resource_obligation_tracking",
                )
            )
        if "inscriptions" in domains or "writing" in domains:
            capabilities.extend(
                (
                    "durable_event_ledger",
                    "provenance_graph",
                    "long_horizon_record_reconciliation",
                )
            )

        return tuple(dict.fromkeys(capabilities))
