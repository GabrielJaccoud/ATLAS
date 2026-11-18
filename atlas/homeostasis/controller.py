from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricEnvelope:
    metric: str
    healthy_min: float | None = None
    healthy_max: float | None = None
    warning_margin: float = 0.10
    critical_margin: float = 0.25


@dataclass(frozen=True)
class HomeostasisReading:
    metric: str
    value: float


@dataclass(frozen=True)
class HomeostasisAssessment:
    metric: str
    value: float
    state: str
    deviation: float
    recommended_event: str | None


class HomeostasisController:
    def assess(self, envelope: MetricEnvelope, reading: HomeostasisReading) -> HomeostasisAssessment:
        if reading.metric != envelope.metric:
            raise ValueError("Reading metric does not match envelope metric.")

        deviation = 0.0
        if envelope.healthy_min is not None and reading.value < envelope.healthy_min:
            deviation = (envelope.healthy_min - reading.value) / max(abs(envelope.healthy_min), 1.0)
        elif envelope.healthy_max is not None and reading.value > envelope.healthy_max:
            deviation = (reading.value - envelope.healthy_max) / max(abs(envelope.healthy_max), 1.0)

        if deviation <= 0:
            state, event = "healthy", None
        elif deviation <= envelope.warning_margin:
            state, event = "warning", "homeostasis.warning"
        elif deviation <= envelope.critical_margin:
            state, event = "degraded", "homeostasis.degraded"
        else:
            state, event = "critical", "homeostasis.critical"

        return HomeostasisAssessment(reading.metric, reading.value, state, deviation, event)
