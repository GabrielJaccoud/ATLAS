from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GlobalMode(str, Enum):
    NORMAL = "normal"
    RESEARCH_INTENSIVE = "research_intensive"
    RESOURCE_SAVING = "resource_saving"
    CRISIS = "crisis"
    EXPLORATION = "exploration"
    MAINTENANCE = "maintenance"


@dataclass(frozen=True)
class ModePolicy:
    mode: GlobalMode
    research_depth: float
    verification_depth: float
    external_action_limit: float
    resource_budget_multiplier: float
    proactive_alerts: bool


class GlobalModeController:
    DEFAULTS = {
        GlobalMode.NORMAL: ModePolicy(GlobalMode.NORMAL, 0.6, 0.6, 0.5, 1.0, True),
        GlobalMode.RESEARCH_INTENSIVE: ModePolicy(GlobalMode.RESEARCH_INTENSIVE, 1.0, 0.9, 0.4, 1.4, True),
        GlobalMode.RESOURCE_SAVING: ModePolicy(GlobalMode.RESOURCE_SAVING, 0.4, 0.6, 0.3, 0.6, False),
        GlobalMode.CRISIS: ModePolicy(GlobalMode.CRISIS, 0.7, 1.0, 0.2, 1.2, True),
        GlobalMode.EXPLORATION: ModePolicy(GlobalMode.EXPLORATION, 0.9, 0.7, 0.3, 1.2, True),
        GlobalMode.MAINTENANCE: ModePolicy(GlobalMode.MAINTENANCE, 0.2, 0.9, 0.1, 0.8, False),
    }

    def __init__(self, initial: GlobalMode = GlobalMode.NORMAL) -> None:
        self._mode = initial

    @property
    def mode(self) -> GlobalMode:
        return self._mode

    def set_mode(self, mode: GlobalMode) -> ModePolicy:
        self._mode = mode
        return self.DEFAULTS[mode]

    def policy(self) -> ModePolicy:
        return self.DEFAULTS[self._mode]
