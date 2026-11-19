from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import httpx

from atlas.artifacts import ArtifactGateway, ArtifactRequest
from atlas.executive import Mission, MinistryOrchestrator, build_default_ministry_registry
from atlas.governance import GovernanceNetwork
from atlas.modes import GlobalModeController
from atlas.opportunities import OpportunityEngine
from atlas.voice import VoiceGateway

from .settings import settings


registry = build_default_ministry_registry()
orchestrator = MinistryOrchestrator(registry)
governance = GovernanceNetwork()
artifact_gateway = ArtifactGateway()
opportunity_engine = OpportunityEngine()
voice_gateway = VoiceGateway()
mode_controller = GlobalModeController()


def _route_payload(route) -> dict[str, object]:
    return {
        "primary_ministries": route.primary_ministries,
        "transversal_bodies": route.transversal_bodies,
        "missing_skills": route.missing_skills,
    }


def _fallback_text(message: str, route_data: dict[str, object], reason: str) -> str:
    ministries = ", ".join(route_data.get("primary_ministries", ()) or ()) or "geral"
    return (
        "Recebi sua mensagem e ela foi registrada no ATLAS. "
        f"Neste momento o provedor de IA está indisponível ({reason}), então não vou fingir "
        "uma resposta generativa que não foi produzida. "
        f"A solicitação foi roteada para: {ministries}. "
        "Tente novamente em instantes ou use o modo local quando ele estiver configurado."
    )


async def _ollama_chat(message: str, instructions: str, history: list[dict[str, str]]) -> str:
    if not settings.ollama_url:
        raise RuntimeError("Ollama is not configured.")
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            f"{settings.ollama_url.rstrip('/')}/api/chat",
            json={
                "model": settings.ollama_model,
                "stream": False,
                "messages": [
                    {"role": "system", "content": instructions},
                    *history,
                    {"role": "user", "content": message},
                ],
            },
        )
        response.raise_for_status()
        data = response.json()
    return str(data.get("message", {}).get("content", "")).strip()


async def _openai_chat(message: str, instructions: str, history: list[dict[str, str]]) -> tuple[str, str | None]:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI is not configured.")
    payload = {
        "model": settings.openai_model,
        "input": [
            {"role": "system", "content": instructions},
            *history,
            {"role": "user", "content": message},
        ],
    }
    async with httpx.AsyncClient(timeout=90) as client:
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
    return "\n".join(text_parts).strip(), data.get("id")


async def atlas_chat(
    message: str,
    context: dict[str, object] | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, object]:
    mission = Mission(
        mission_id=f"chat:{uuid4().hex[:12]}",
        objective=message,
        required_skills=("research", "analysis"),
        metadata=context or {},
    )
    route = orchestrator.route(mission)
    route_data = _route_payload(route)
    conversation = [
        {"role": turn["role"], "content": turn["content"][:6000]}
        for turn in (history or [])[-20:]
        if turn.get("role") in {"user", "assistant"} and isinstance(turn.get("content"), str)
    ]

    instructions = (
        "You are ATLAS, a governed multidisciplinary research and decision system. "
        "Distinguish observations, inference, models, hypotheses, simulations and traditions. "
        "Be concise, useful and explicit about uncertainty. "
        f"Primary ministries for this request: {', '.join(route.primary_ministries) or 'general'}."
    )

    openai_error: str | None = None

    if settings.openai_api_key:
        try:
            text, response_id = await _openai_chat(message, instructions, conversation)
            return {
                "mode": "cloud",
                "provider": "openai",
                "text": text,
                "response_id": response_id,
                "route": route_data,
            }
        except httpx.HTTPStatusError as exc:
            openai_error = f"OpenAI HTTP {exc.response.status_code}"
        except httpx.HTTPError:
            openai_error = "OpenAI network error"

    if settings.ollama_url:
        try:
            text = await _ollama_chat(message, instructions, conversation)
            return {
                "mode": "local",
                "provider": "ollama",
                "text": text,
                "route": route_data,
                "fallback_from": openai_error,
            }
        except (httpx.HTTPError, RuntimeError):
            pass

    reason = openai_error or "nenhum modelo generativo configurado"
    return {
        "mode": "local",
        "provider": "deterministic",
        "text": _fallback_text(message, route_data, reason),
        "route": route_data,
        "provider_error": openai_error,
    }


async def create_realtime_client_secret() -> dict[str, object]:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI API key is not configured.")
    payload = {
        "expires_after": {"anchor": "created_at", "seconds": 600},
        "session": {
            "type": "realtime",
            "model": settings.openai_realtime_model,
            "output_modalities": ["audio"],
            "instructions": (
                "You are ATLAS. Speak naturally in Brazilian Portuguese unless the user requests "
                "another language. Be concise and distinguish fact, inference and hypothesis."
            ),
        },
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{settings.openai_base_url}/realtime/client_secrets",
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()
        return response.json()


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
