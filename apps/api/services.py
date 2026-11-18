from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import httpx

from atlas.artifacts import ArtifactGateway, ArtifactRequest
from atlas.executive import Mission, MinistryOrchestrator, build_default_ministry_registry
from atlas.governance import GovernanceNetwork, GovernanceRequest
from atlas.modes import GlobalModeController
from atlas.opportunities import Opportunity, OpportunityEngine
from atlas.personal import MyWorldGraph, WorldEdge, WorldNode
from atlas.research import ResearchBacklog, ResearchItem, ResearchStatus
from atlas.voice import VoiceGateway

from .settings import settings


registry = build_default_ministry_registry()
orchestrator = MinistryOrchestrator(registry)
governance = GovernanceNetwork()
artifact_gateway = ArtifactGateway()
research_backlog = ResearchBacklog()
world = MyWorldGraph()
opportunity_engine = OpportunityEngine()
voice_gateway = VoiceGateway()
mode_controller = GlobalModeController()


async def atlas_chat(message: str, context: dict[str, object] | None = None) -> dict[str, object]:
    mission = Mission(
        mission_id=f"chat:{uuid4().hex[:12]}",
        objective=message,
        required_skills=("research", "analysis"),
        metadata=context or {},
    )
    route = orchestrator.route(mission)

    if not settings.openai_api_key:
        return {
            "mode": "local",
            "text": (
                "ATLAS está operacional em modo local, mas o provedor de linguagem em nuvem "
                "ainda não foi configurado. A missão foi roteada internamente e pode ser "
                "acompanhada pelos ministérios."
            ),
            "route": {
                "primary_ministries": route.primary_ministries,
                "transversal_bodies": route.transversal_bodies,
                "missing_skills": route.missing_skills,
            },
        }

    instructions = (
        "You are ATLAS, a governed multidisciplinary research and decision system. "
        "Distinguish observations, inference, models, hypotheses, simulations and traditions. "
        "Be concise, useful and explicit about uncertainty. "
        f"Primary ministries for this request: {', '.join(route.primary_ministries) or 'general'}."
    )
    payload = {
        "model": settings.openai_model,
        "input": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": message},
        ],
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{settings.openai_base_url}/responses",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    text_parts: list[str] = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") in {"output_text", "text"} and part.get("text"):
                    text_parts.append(part["text"])
    return {
        "mode": "cloud",
        "text": "\n".join(text_parts).strip(),
        "response_id": data.get("id"),
        "route": {
            "primary_ministries": route.primary_ministries,
            "transversal_bodies": route.transversal_bodies,
        },
    }


def save_artifact_bytes(filename: str, content: bytes) -> dict[str, object]:
    root = Path(settings.artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    artifact_id = uuid4().hex
    safe_name = Path(filename).name
    destination = root / f"{artifact_id}-{safe_name}"
    destination.write_bytes(content)
    plan = artifact_gateway.plan(ArtifactRequest(filename=safe_name, operations=("ingest",)))
    return {
        "artifact_id": artifact_id,
        "filename": safe_name,
        "path": str(destination),
        "size": len(content),
        "kind": plan.kind.value,
        "parser": plan.parser,
        "notes": plan.notes,
    }
