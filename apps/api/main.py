from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select

from atlas.councils import CouncilCadence, CouncilScheduler
from atlas.executive import Mission
from atlas.governance import GovernanceRequest
from atlas.modes import GlobalMode
from atlas.opportunities import Opportunity
from atlas.personal import WorldEdge, WorldNode
from atlas.research import ResearchItem, ResearchStatus

from .db import Record, SessionLocal, init_db
from .services import (
    atlas_chat,
    governance,
    mode_controller,
    opportunity_engine,
    orchestrator,
    registry,
    research_backlog,
    save_artifact_bytes,
    world,
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
    context: dict[str, object] = {}


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
    attributes: dict[str, object] = {}


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
    }


@app.get("/status", dependencies=[Depends(require_token)])
def status() -> dict[str, object]:
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
            "blocked": len(research_backlog.blocked()),
        },
        "my_world": {
            "nodes": len(world.nodes),
            "edges": len(world.edges),
        },
    }


@app.post("/chat", dependencies=[Depends(require_token)])
async def chat(request: ChatRequest) -> dict[str, object]:
    return await atlas_chat(request.message, request.context)


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
    return orchestrator.route(mission).__dict__


@app.post("/research", dependencies=[Depends(require_token)])
def add_research(request: ResearchRequest) -> dict[str, object]:
    item = ResearchItem(
        item_id=f"research:{uuid4().hex[:12]}",
        ministry_id=request.ministry_id,
        question=request.question,
        status=ResearchStatus.IDEA,
        priority=request.priority,
    )
    research_backlog.add(item)
    return item.__dict__


@app.get("/research/{ministry_id}", dependencies=[Depends(require_token)])
def list_research(ministry_id: str) -> list[dict[str, object]]:
    return [x.__dict__ for x in research_backlog.by_ministry(ministry_id)]


@app.post("/world/nodes", dependencies=[Depends(require_token)])
def add_world_node(request: WorldNodeRequest) -> dict[str, object]:
    node = WorldNode(f"node:{uuid4().hex[:12]}", request.kind, request.name, request.attributes)
    world.add_node(node)
    return node.__dict__


@app.post("/world/edges", dependencies=[Depends(require_token)])
def add_world_edge(request: WorldEdgeRequest) -> dict[str, object]:
    edge = WorldEdge(request.source, request.relation, request.target, request.weight)
    world.connect(edge)
    return edge.__dict__


@app.get("/world", dependencies=[Depends(require_token)])
def get_world() -> dict[str, object]:
    return {
        "nodes": [x.__dict__ for x in world.nodes.values()],
        "edges": [x.__dict__ for x in world.edges],
    }


@app.post("/opportunities/match/{target_id}", dependencies=[Depends(require_token)])
def match_opportunity(target_id: str, request: OpportunityRequest) -> dict[str, object]:
    target = world.nodes.get(target_id)
    if target is None:
        raise HTTPException(status_code=404, detail="Target not found in My World.")
    opp = Opportunity(
        f"opp:{uuid4().hex[:12]}",
        request.title,
        tuple(request.domains),
        tuple(request.requirements),
        request.value_score,
        request.deadline_urgency,
    )
    attrs = target.attributes
    return opportunity_engine.match(
        opp,
        target_id=target_id,
        target_domains=tuple(attrs.get("domains", [])),
        target_capabilities=tuple(attrs.get("capabilities", [])),
    ).__dict__


@app.get("/councils/{cadence}", dependencies=[Depends(require_token)])
def council_template(cadence: CouncilCadence) -> dict[str, object]:
    return CouncilScheduler().create(f"council:{uuid4().hex[:12]}", cadence).__dict__


@app.post("/mode/{mode}", dependencies=[Depends(require_token)])
def set_mode(mode: GlobalMode) -> dict[str, object]:
    return mode_controller.set_mode(mode).__dict__


@app.post("/artifacts", dependencies=[Depends(require_token)])
async def upload_artifact(file: UploadFile = File(...)) -> dict[str, object]:
    content = await file.read()
    if len(content) > 100 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Artifact exceeds 100 MB limit.")
    return save_artifact_bytes(file.filename or "upload.bin", content)


@app.get("/records/{kind}", dependencies=[Depends(require_token)])
def list_records(kind: str) -> list[dict[str, object]]:
    with SessionLocal() as db:
        rows = db.scalars(select(Record).where(Record.kind == kind).order_by(Record.id.desc())).all()
        return [
            {
                "id": row.id,
                "kind": row.kind,
                "external_id": row.external_id,
                "title": row.title,
                "body": row.body,
                "data": row.data,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
