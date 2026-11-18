from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskProfile:
    task_id: str
    sensitivity: float
    reasoning_depth: float
    latency_priority: float
    offline_required: bool = False
    modality: str = "text"


@dataclass(frozen=True)
class ModelEndpoint:
    endpoint_id: str
    location: str
    modalities: tuple[str, ...]
    max_reasoning: float
    privacy_score: float
    latency_score: float
    available: bool = True


@dataclass(frozen=True)
class RuntimeDecision:
    task_id: str
    endpoint_id: str
    score: float
    rationale: tuple[str, ...]


class HybridRuntime:
    def choose(self, task: TaskProfile, endpoints: tuple[ModelEndpoint, ...]) -> RuntimeDecision:
        candidates: list[tuple[float, ModelEndpoint, list[str]]] = []
        for ep in endpoints:
            if not ep.available or task.modality not in ep.modalities:
                continue
            if task.offline_required and ep.location != "local":
                continue
            score = (
                0.35 * min(ep.max_reasoning, max(task.reasoning_depth, 0.1))
                + 0.30 * ep.privacy_score * task.sensitivity
                + 0.25 * ep.latency_score * task.latency_priority
                + 0.10 * (1.0 if ep.location == "local" and task.sensitivity > 0.7 else 0.5)
            )
            reasons = [f"location:{ep.location}", f"modality:{task.modality}"]
            candidates.append((score, ep, reasons))
        if not candidates:
            raise ValueError("No compatible runtime endpoint.")
        score, ep, reasons = max(candidates, key=lambda x: x[0])
        return RuntimeDecision(task.task_id, ep.endpoint_id, score, tuple(reasons))
