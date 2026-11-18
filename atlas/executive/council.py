from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .fractal import MinistryFractal


@dataclass(frozen=True)
class CouncilReport:
    generated_at: str
    changed_beliefs: tuple[str, ...]
    new_knowledge: tuple[str, ...]
    hypotheses_up: tuple[str, ...]
    hypotheses_down: tuple[str, ...]
    cross_domain_connections: tuple[str, ...]
    system_changes_proposed: tuple[str, ...]
    unresolved_conflicts: tuple[str, ...]


class GrandCouncil:
    """Produces a structured synthesis from ministry state.

    This is intentionally deterministic scaffolding. Future LLM agents may
    draft candidate summaries, but promotion into system state remains governed.
    """

    def convene(self, fractals: tuple[MinistryFractal, ...]) -> CouncilReport:
        discoveries = tuple(
            discovery
            for fractal in fractals
            for discovery in fractal.state.recent_discoveries
        )
        conflicts = tuple(
            conflict
            for fractal in fractals
            for conflict in fractal.state.unresolved_contradictions
        )
        proposals = tuple(sorted({
            proposal
            for fractal in fractals
            for proposal in fractal.state.proposed_capabilities
        }))
        return CouncilReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            changed_beliefs=(),
            new_knowledge=discoveries,
            hypotheses_up=(),
            hypotheses_down=(),
            cross_domain_connections=(),
            system_changes_proposed=proposals,
            unresolved_conflicts=conflicts,
        )
