from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from atlas.councils import CouncilCadence, CouncilScheduler
from atlas.executive import Mission
from atlas.modes import GlobalMode
from atlas.events import EventPriority, EventRecord
from atlas.governance import GovernanceNetwork, GovernanceRequest
from atlas.support import SupportCell, SupportRequest, SupportService
from atlas.opportunities import Opportunity
from atlas.research import ResearchStatus

from .db import get_record, init_db, list_record_dicts, save_record
from .ops import export_backup, metrics_snapshot, write_backup_file
from .services import (
    atlas_chat,
    mode_controller,
    opportunity_engine,
    orchestrator,
    registry,
    save_artifact_bytes,
    create_realtime_client_secret,
)
from .settings import settings


app = FastAPI(
    title="ATLAS API",
    version="1.8.0",
    description="ATLAS Fractal Cognitive Network API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = f"Bearer {settings.api_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid ATLAS API token.")


class ChatRequest(BaseModel):
    message: str
    context: dict[str, object] = Field(default_factory=dict)


class MissionRequest(BaseModel):
    objective: str
    required_skills: list[str]
    risk: float = 0.0
    external_action: bool = False
    irreversible: bool = False


class ResearchRequest(BaseModel):
    ministry_id: str
    question: str
    priority: float = 0.5


class WorldNodeRequest(BaseModel):
    kind: str
    name: str
    attributes: dict[str, object] = Field(default_factory=dict)


class WorldEdgeRequest(BaseModel):
    source: str
    relation: str
    target: str
    weight: float = 1.0


class OpportunityRequest(BaseModel):
    title: str
    domains: list[str]
    requirements: list[str]
    value_score: float
    deadline_urgency: float = 0.0


class EventRequest(BaseModel):
    event_type: str
    source: str
    payload: dict[str, object] = Field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    tags: list[str] = Field(default_factory=list)


class GovernanceRouteRequest(BaseModel):
    source: str
    purpose: str
    categories: list[str]
    risk: float = 0.0
    external_action: bool = False
    irreversible: bool = False


class SupportPlanRequest(BaseModel):
    requester: str
    symptom: str
    desired_outcome: str
    requested_services: list[SupportService]
    severity: float = 0.0
    requires_code_change: bool = False
    requires_new_tool: bool = False
    touches_constitution: bool = False
    external_effect: bool = False


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "version": "1.8.0",
        "environment": settings.environment,
        "mode": mode_controller.mode.value,
        "cloud_language_model": bool(settings.openai_api_key),
        "local_language_model": bool(settings.ollama_url),
        "database": "postgres" if settings.database_url.startswith("postgres") else "sqlite",
    }


@app.post("/voice/realtime-token", dependencies=[Depends(require_token)])
async def realtime_token() -> dict[str, object]:
    try:
        return await create_realtime_client_secret()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/status", dependencies=[Depends(require_token)])
def status() -> dict[str, object]:
    research = list_record_dicts("research")
    nodes = list_record_dicts("world_node")
    edges = list_record_dicts("world_edge")
    return {
        "mode": mode_controller.policy().__dict__,
        "ministries": [
            {
                "id": m.ministry_id,
                "name": m.name,
                "transversal": m.transversal,
                "skills": m.skills,
            }
            for m in registry.values()
        ],
        "research": {
            "total": len(research),
            "blocked": sum(1 for x in research if x["data"].get("status") == "blocked"),
        },
        "my_world": {"nodes": len(nodes), "edges": len(edges)},
        "artifacts": len(list_record_dicts("artifact")),
    }


@app.post("/chat", dependencies=[Depends(require_token)])
async def chat(request: ChatRequest) -> dict[str, object]:
    interaction_id = f"chat:{uuid4().hex[:12]}"
    save_record(
        "chat_input",
        interaction_id,
        body=request.message,
        data={"context": request.context},
    )
    result = await atlas_chat(request.message, request.context)
    save_record(
        "chat_output",
        interaction_id,
        body=str(result.get("text", "")),
        data={"mode": result.get("mode"), "route": result.get("route", {})},
    )
    return result


@app.post("/missions/route", dependencies=[Depends(require_token)])
def route_mission(request: MissionRequest) -> dict[str, object]:
    mission = Mission(
        mission_id=f"mission:{uuid4().hex[:12]}",
        objective=request.objective,
        required_skills=tuple(request.required_skills),
        risk=request.risk,
        external_action=request.external_action,
        irreversible=request.irreversible,
    )
    route = orchestrator.route(mission)
    payload = route.__dict__
    save_record(
        "mission",
        mission.mission_id,
        title=request.objective,
        data={
            "required_skills": request.required_skills,
            "risk": request.risk,
            "external_action": request.external_action,
            "irreversible": request.irreversible,
            "route": payload,
        },
    )
    return payload


@app.post("/research", dependencies=[Depends(require_token)])
def add_research(request: ResearchRequest) -> dict[str, object]:
    item_id = f"research:{uuid4().hex[:12]}"
    data = {
        "item_id": item_id,
        "ministry_id": request.ministry_id,
        "question": request.question,
        "status": ResearchStatus.IDEA.value,
        "priority": request.priority,
        "evidence_refs": [],
        "dependencies": [],
        "next_experiment": None,
    }
    save_record("research", item_id, title=request.question, data=data)
    return data


@app.get("/research/{ministry_id}", dependencies=[Depends(require_token)])
def list_research(ministry_id: str) -> list[dict[str, object]]:
    rows = list_record_dicts("research")
    items = [x["data"] for x in rows if x["data"].get("ministry_id") == ministry_id]
    return sorted(items, key=lambda x: (-float(x.get("priority", 0)), str(x.get("item_id", ""))))


@app.post("/world/nodes", dependencies=[Depends(require_token)])
def add_world_node(request: WorldNodeRequest) -> dict[str, object]:
    node_id = f"node:{uuid4().hex[:12]}"
    data = {
        "node_id": node_id,
        "kind": request.kind,
        "name": request.name,
        "attributes": request.attributes,
    }
    save_record("world_node", node_id, title=request.name, data=data)
    return data


@app.post("/world/edges", dependencies=[Depends(require_token)])
def add_world_edge(request: WorldEdgeRequest) -> dict[str, object]:
    if not get_record("world_node", request.source) or not get_record("world_node", request.target):
        raise HTTPException(status_code=404, detail="Both My World nodes must exist.")
    edge_id = f"edge:{uuid4().hex[:12]}"
    data = {
        "edge_id": edge_id,
        "source": request.source,
        "relation": request.relation,
        "target": request.target,
        "weight": request.weight,
    }
    save_record("world_edge", edge_id, title=request.relation, data=data)
    return data


@app.get("/world", dependencies=[Depends(require_token)])
def get_world() -> dict[str, object]:
    return {
        "nodes": [x["data"] for x in list_record_dicts("world_node")],
        "edges": [x["data"] for x in list_record_dicts("world_edge")],
    }


@app.post("/opportunities/match/{target_id}", dependencies=[Depends(require_token)])
def match_opportunity(target_id: str, request: OpportunityRequest) -> dict[str, object]:
    target_row = get_record("world_node", target_id)
    if target_row is None:
        raise HTTPException(status_code=404, detail="Target not found in My World.")
    target = target_row["data"]
    attrs = target.get("attributes", {})
    opp = Opportunity(
        f"opp:{uuid4().hex[:12]}",
        request.title,
        tuple(request.domains),
        tuple(request.requirements),
        request.value_score,
        request.deadline_urgency,
    )
    match = opportunity_engine.match(
        opp,
        target_id=target_id,
        target_domains=tuple(attrs.get("domains", [])),
        target_capabilities=tuple(attrs.get("capabilities", [])),
    )
    save_record(
        "opportunity_match",
        match.opportunity_id,
        title=request.title,
        data=match.__dict__,
    )
    return match.__dict__


@app.get("/councils/{cadence}", dependencies=[Depends(require_token)])
def council_template(cadence: CouncilCadence) -> dict[str, object]:
    session = CouncilScheduler().create(f"council:{uuid4().hex[:12]}", cadence)
    save_record("council", session.session_id, title=cadence.value, data=session.__dict__)
    return session.__dict__


@app.post("/mode/{mode}", dependencies=[Depends(require_token)])
def set_mode(mode: GlobalMode) -> dict[str, object]:
    policy = mode_controller.set_mode(mode)
    save_record("mode_change", f"mode:{uuid4().hex[:12]}", title=mode.value, data=policy.__dict__)
    return policy.__dict__


@app.post("/artifacts", dependencies=[Depends(require_token)])
async def upload_artifact(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Artifact exceeds 100 MB limit.")
    result = save_artifact_bytes(file.filename or "upload.bin", content)
    save_record(
        "artifact",
        str(result["artifact_id"]),
        title=str(result["filename"]),
        data=result,
    )
    return result



@app.post("/events", dependencies=[Depends(require_token)])
def publish_event(request: EventRequest) -> dict[str, object]:
    event = EventRecord(
        event_id=f"event:{uuid4().hex[:12]}",
        event_type=request.event_type,
        source=request.source,
        payload=request.payload,
        priority=request.priority,
        tags=tuple(request.tags),
    )
    data = {
        "event_id": event.event_id,
        "event_type": event.event_type,
        "source": event.source,
        "payload": event.payload,
        "priority": int(event.priority),
        "tags": list(event.tags),
        "created_at": event.created_at,
    }
    save_record("event", event.event_id, title=event.event_type, data=data)
    return data


@app.get("/events", dependencies=[Depends(require_token)])
def list_events() -> list[dict[str, object]]:
    return [x["data"] for x in list_record_dicts("event")]


@app.post("/governance/route", dependencies=[Depends(require_token)])
def governance_route(request: GovernanceRouteRequest) -> dict[str, object]:
    response = GovernanceNetwork().route(GovernanceRequest(
        request_id=f"governance:{uuid4().hex[:12]}",
        source=request.source,
        purpose=request.purpose,
        categories=tuple(request.categories),
        risk=request.risk,
        external_action=request.external_action,
        irreversible=request.irreversible,
    ))
    data = {
        "request_id": response.request_id,
        "routed_to": [x.value for x in response.routed_to],
        "human_approval_required": response.human_approval_required,
        "rationale": list(response.rationale),
    }
    save_record("governance", response.request_id, title=request.purpose, data=data)
    return data


@app.post("/support/plan", dependencies=[Depends(require_token)])
def support_plan(request: SupportPlanRequest) -> dict[str, object]:
    result = SupportCell().plan(SupportRequest(
        request_id=f"support:{uuid4().hex[:12]}",
        requester=request.requester,
        symptom=request.symptom,
        desired_outcome=request.desired_outcome,
        requested_services=tuple(request.requested_services),
        severity=request.severity,
        requires_code_change=request.requires_code_change,
        requires_new_tool=request.requires_new_tool,
        touches_constitution=request.touches_constitution,
        external_effect=request.external_effect,
    ))
    data = {
        "request_id": result.request_id,
        "services": [x.value for x in result.services],
        "route_to_codex": result.route_to_codex,
        "route_to_guardian": result.route_to_guardian,
        "route_to_ria": result.route_to_ria,
        "sandbox_required": result.sandbox_required,
        "human_approval_required": result.human_approval_required,
        "steps": list(result.steps),
    }
    save_record("support_request", result.request_id, title=request.symptom, data=data)
    return data


@app.get("/metrics", dependencies=[Depends(require_token)])
def metrics() -> dict[str, object]:
    return metrics_snapshot()


@app.get("/backup", dependencies=[Depends(require_token)])
def backup() -> dict[str, object]:
    return export_backup()


@app.post("/backup/write", dependencies=[Depends(require_token)])
def backup_write() -> dict[str, object]:
    path = write_backup_file()
    save_record("backup", f"backup:{uuid4().hex[:12]}", title="logical-backup", data={"path": path})
    return {"path": path}


@app.get("/records/{kind}", dependencies=[Depends(require_token)])
def list_records(kind: str) -> list[dict[str, object]]:
    return list_record_dicts(kind)
