from __future__ import annotations

import hmac
import smtplib
import ssl
from email.message import EmailMessage
from io import BytesIO
from typing import Literal
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from atlas.councils import CouncilCadence, CouncilScheduler
from atlas.executive import Mission
from atlas.modes import GlobalMode
from atlas.events import EventPriority, EventRecord
from atlas.governance import GovernanceNetwork, GovernanceRequest
from atlas.support import SupportCell, SupportRequest, SupportService
from atlas.worlds import PossibleWorldsLab
from atlas.worlds.programs import default_world_programs
from atlas.worlds.synthesis import WorldTechnologySynthesizer
from atlas.opportunities import Opportunity
from atlas.research import ResearchStatus

from .auth import create_session_token, verify_session_token
from .db import get_record, init_db, list_record_dicts, save_record
from .ops import export_backup, metrics_snapshot, write_backup_file
from .services import (
    atlas_chat,
    configured_review_providers,
    mode_controller,
    opportunity_engine,
    orchestrator,
    review_scientific_work,
    registry,
    save_artifact_bytes,
    create_realtime_client_secret,
)
from .settings import settings


app = FastAPI(
    title="ATLAS API",
    version="1.9.0",
    description="ATLAS Possible Worlds & Experimental Intelligence API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def require_token(authorization: str | None = Header(default=None)) -> None:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing ATLAS session.")
    token = authorization.removeprefix("Bearer ").strip()
    if token == settings.api_token:
        return
    if verify_session_token(token):
        return
    raise HTTPException(status_code=401, detail="Invalid or expired ATLAS session.")


class WorldObservationRequest(BaseModel):
    experiment_id: str
    outcome: str


class OwnerLoginRequest(BaseModel):
    code: str


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=6000)


class ChatRequest(BaseModel):
    message: str
    context: dict[str, object] = Field(default_factory=dict)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)


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


class ScientificWorkRequest(BaseModel):
    author_name: str = Field(default="Gabriel Jaccoud", min_length=3, max_length=200)
    ministry_id: str = Field(min_length=1, max_length=120)
    work_type: Literal["mathematical_result", "theoretical_physics", "empirical_result"]
    evidence_level: Literal[
        "internal_hypothesis",
        "mathematical_proof",
        "physical_viability",
        "empirical_support",
        "independent_replication",
    ]
    title_pt: str = Field(min_length=8, max_length=300)
    title_en: str = Field(default="", max_length=300)
    abstract_pt: str = Field(default="", max_length=5000)
    abstract_en: str = Field(default="", max_length=5000)
    question_pt: str = Field(default="", max_length=10000)
    question_en: str = Field(default="", max_length=10000)
    assumptions_pt: str = Field(default="", max_length=10000)
    assumptions_en: str = Field(default="", max_length=10000)
    methodology_pt: str = Field(default="", max_length=20000)
    methodology_en: str = Field(default="", max_length=20000)
    results_pt: str = Field(default="", max_length=20000)
    results_en: str = Field(default="", max_length=20000)
    predictions_pt: str = Field(default="", max_length=10000)
    predictions_en: str = Field(default="", max_length=10000)
    uncertainty_pt: str = Field(default="", max_length=10000)
    uncertainty_en: str = Field(default="", max_length=10000)
    limitations_pt: str = Field(default="", max_length=10000)
    limitations_en: str = Field(default="", max_length=10000)
    references: list[str] = Field(default_factory=list, max_length=100)


@app.get("/publication-delivery-settings", dependencies=[Depends(require_token)])
def publication_delivery_settings() -> dict[str, object]:
    """Return the owner's private, preconfigured destinations for sharing PDFs."""
    return {
        "email": settings.publication_email,
        "can_send_email": bool(settings.publication_email and settings.smtp_host and settings.smtp_username and settings.smtp_password),
    }


def build_scientific_work_pdf(work: dict[str, object], language: Literal["pt", "en"]) -> bytes:
    english = language == "en"
    get = lambda key: str(work.get(f"{key}_{language}") or "")
    title = get("title")
    evidence = str(work.get("claim_classification", "")).replace("_", " ")
    sections = (
        [("Abstract", get("abstract")), ("Research question and origin", get("question")),
         ("Assumptions and model", get("assumptions")), ("Methodology and experiments", get("methodology")),
         ("Theorem, proof and result" if work.get("work_type") == "mathematical_result" else "Results", get("results")),
         ("Testable predictions", get("predictions")), ("Uncertainty", get("uncertainty")),
         ("Limitations and alternatives", get("limitations"))]
        if english else
        [("Resumo", get("abstract")), ("Pergunta e origem da pesquisa", get("question")),
         ("Premissas e modelo", get("assumptions")), ("Métodos e experimentos", get("methodology")),
         ("Teorema, demonstração e resultado" if work.get("work_type") == "mathematical_result" else "Resultados", get("results")),
         ("Previsões testáveis", get("predictions")), ("Incertezas", get("uncertainty")),
         ("Limitações e explicações alternativas", get("limitations"))]
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="AtlasTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=21, leading=26, textColor=colors.HexColor("#20252d"), alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="AtlasMeta", parent=styles["Normal"], fontSize=9, leading=13, textColor=colors.HexColor("#586270"), spaceAfter=14))
    styles.add(ParagraphStyle(name="AtlasSection", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=colors.HexColor("#293446"), spaceBefore=14, spaceAfter=5))
    styles.add(ParagraphStyle(name="AtlasBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.5, leading=15, spaceAfter=7, splitLongWords=1))
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=23*mm, rightMargin=23*mm, topMargin=20*mm, bottomMargin=20*mm, title=title, author=str(work.get("author_name", "Gabriel Jaccoud")))
    story = [Paragraph(escape(evidence.upper()), styles["AtlasMeta"]), Paragraph(escape(title), styles["AtlasTitle"])]
    author = escape(str(work.get("author_name", "Gabriel Jaccoud")))
    ministry = escape(str(work.get("ministry_id", "")))
    evidence_label = "Evidence classification" if english else "Classificação da evidência"
    story += [Paragraph(f"{author} · {ministry} · {evidence_label}: {escape(evidence)}", styles["AtlasMeta"]), Spacer(1, 4)]
    for heading, body in sections:
        story.extend([Paragraph(escape(heading), styles["AtlasSection"]), Paragraph(escape(body).replace("\n", "<br/>"), styles["AtlasBody"])])
    references = work.get("references", [])
    story.append(Paragraph("References" if english else "Referências", styles["AtlasSection"]))
    for index, reference in enumerate(references if isinstance(references, list) else [], start=1):
        story.append(Paragraph(f"{index}. {escape(str(reference))}", styles["AtlasBody"]))
    note = "AI-assisted content must be reviewed by the responsible author before external submission." if english else "O conteúdo elaborado com apoio de IA deve ser revisado pelo autor responsável antes de submissão externa."
    story += [Spacer(1, 14), Paragraph(escape(note), styles["AtlasMeta"])]
    document.build(story)
    return buffer.getvalue()


def get_exportable_scientific_work(publication_id: str) -> dict[str, object]:
    record = get_record("scientific_work", publication_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scientific work not found.")
    work = record.get("data")
    if not isinstance(work, dict) or not work.get("export_ready"):
        raise HTTPException(status_code=409, detail="This work has not passed the export gate.")
    return work


@app.get("/publications/{publication_id}/pdf", dependencies=[Depends(require_token)])
def download_scientific_work_pdf(publication_id: str, language: Literal["pt", "en"] = "pt") -> Response:
    work = get_exportable_scientific_work(publication_id)
    pdf = build_scientific_work_pdf(work, language)
    return Response(content=pdf, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="ATLAS-{language}-{publication_id.replace(":", "-")}.pdf"'})


@app.post("/publications/{publication_id}/email", dependencies=[Depends(require_token)])
def email_scientific_work(publication_id: str) -> dict[str, object]:
    work = get_exportable_scientific_work(publication_id)
    if not settings.publication_email:
        raise HTTPException(status_code=503, detail="No recipient e-mail is configured.")
    if not all((settings.smtp_host, settings.smtp_username, settings.smtp_password)):
        raise HTTPException(status_code=503, detail="Direct e-mail sending is not configured in ATLAS yet.")
    title = str(work.get("title_pt", "Trabalho científico"))
    message = EmailMessage()
    message["Subject"] = f"ATLAS — PDFs para revisão e exportação: {title}"
    message["From"] = settings.smtp_from or settings.smtp_username
    message["To"] = settings.publication_email
    message.set_content(f"Gabriel,\n\nSeguem anexos os PDFs do trabalho científico ‘{title}’, em português e inglês.\n\nRevise os documentos antes de qualquer submissão externa.\n\nATLAS")
    attachments = []
    for language in ("pt", "en"):
        pdf = build_scientific_work_pdf(work, language)
        filename = f"ATLAS-{language}-{publication_id.replace(':', '-')}.pdf"
        message.add_attachment(pdf, maintype="application", subtype="pdf", filename=filename)
        attachments.append(filename)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=25) as server:
            if settings.smtp_use_tls:
                server.starttls(context=ssl.create_default_context())
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        raise HTTPException(status_code=502, detail="ATLAS could not send the e-mail. Check the private SMTP configuration.") from error
    return {"sent": True, "to": settings.publication_email, "attachments": attachments}


def evaluate_scientific_work(data: ScientificWorkRequest) -> dict[str, object]:
    common_missing = [
        label for label, value in (
            ("abstract_pt", data.abstract_pt), ("abstract_en", data.abstract_en),
            ("question_pt", data.question_pt), ("question_en", data.question_en),
            ("methodology_pt", data.methodology_pt), ("methodology_en", data.methodology_en),
            ("limitations_pt", data.limitations_pt), ("limitations_en", data.limitations_en),
            ("title_en", data.title_en),
        ) if not value.strip()
    ]
    missing = list(common_missing)
    if not data.references:
        missing.append("references")

    if data.work_type == "mathematical_result":
        if data.evidence_level != "mathematical_proof":
            missing.append("complete_mathematical_proof")
        if not data.assumptions_pt.strip():
            missing.append("assumptions_pt")
        if not data.assumptions_en.strip():
            missing.append("assumptions_en")
        if not data.results_pt.strip() or not data.results_en.strip():
            missing.append("proof_and_result_in_both_languages")
        classification = "mathematically_proven_under_stated_assumptions"
    elif data.work_type == "theoretical_physics":
        if data.evidence_level not in {"physical_viability", "empirical_support", "independent_replication"}:
            missing.append("physical_viability_review")
        if not data.assumptions_pt.strip() or not data.assumptions_en.strip():
            missing.append("explicit_assumptions_in_both_languages")
        if not data.predictions_pt.strip() or not data.predictions_en.strip():
            missing.append("testable_predictions_in_both_languages")
        classification = (
            "theoretical_not_experimentally_confirmed"
            if data.evidence_level == "physical_viability"
            else data.evidence_level
        )
    else:
        if data.evidence_level not in {"empirical_support", "independent_replication"}:
            missing.append("empirical_evidence")
        if not data.results_pt.strip() or not data.results_en.strip():
            missing.append("results_in_both_languages")
        if not data.uncertainty_pt.strip() or not data.uncertainty_en.strip():
            missing.append("uncertainty_in_both_languages")
        classification = data.evidence_level

    return {
        "export_ready": not missing,
        "missing_requirements": missing,
        "claim_classification": classification,
        "review_required": True,
    }


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
        "version": "1.9.0",
        "environment": settings.environment,
        "mode": mode_controller.mode.value,
        "cloud_language_model": bool(settings.openai_api_key),
        "local_language_model": bool(settings.ollama_url),
        "database": "postgres" if settings.database_url.startswith("postgres") else "sqlite",
    }


@app.post("/auth/session")
def owner_session(request: OwnerLoginRequest) -> dict[str, object]:
    if not hmac.compare_digest(request.code.strip(), settings.owner_code):
        raise HTTPException(status_code=401, detail="Código do proprietário inválido.")
    token = create_session_token()
    return {
        "token": token,
        "expires_in_days": settings.session_days,
        "role": "owner",
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
    result = await atlas_chat(
        request.message,
        request.context,
        [turn.model_dump() for turn in request.history],
    )
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


@app.get("/publications", dependencies=[Depends(require_token)])
def list_scientific_works() -> list[dict[str, object]]:
    latest: dict[str, dict[str, object]] = {}
    for record in list_record_dicts("scientific_work"):
        external_id = str(record["external_id"])
        latest.setdefault(external_id, record["data"])
    return list(latest.values())


@app.post("/publications", dependencies=[Depends(require_token)])
def register_scientific_work(request: ScientificWorkRequest) -> dict[str, object]:
    publication_id = f"publication:{uuid4().hex[:12]}"
    gate = evaluate_scientific_work(request)
    data = {
        "publication_id": publication_id,
        "revision": 1,
        **request.model_dump(),
        **gate,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_record(
        "scientific_work",
        publication_id,
        title=request.title_pt,
        body=request.abstract_pt,
        data=data,
    )
    return data


@app.get("/review/providers", dependencies=[Depends(require_token)])
def list_review_providers() -> dict[str, object]:
    return {
        "providers": configured_review_providers(),
        "review_roles": ["language_editor", "structure_method", "evidence_red_team", "domain_reviewer"],
        "internet_research": False,
    }


@app.get("/publications/{publication_id}/reviews", dependencies=[Depends(require_token)])
def list_publication_reviews(publication_id: str) -> list[dict[str, object]]:
    rows = list_record_dicts("publication_review")
    reviews = [row["data"] for row in rows if row["data"].get("publication_id") == publication_id]
    return sorted(reviews, key=lambda review: str(review.get("generated_at", "")), reverse=True)


@app.post("/publications/{publication_id}/review", dependencies=[Depends(require_token)])
async def run_publication_review(publication_id: str) -> dict[str, object]:
    record = get_record("scientific_work", publication_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scientific work not found.")
    work = record.get("data")
    if not isinstance(work, dict):
        raise HTTPException(status_code=422, detail="Scientific work record is malformed.")
    try:
        review = await review_scientific_work(work)
    except RuntimeError as error:
        message = str(error)
        status_code = 503 if "No AI review provider" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from error
    save_record(
        "publication_review",
        str(review["review_id"]),
        title=str(work.get("title_pt", "Publication review")),
        data=review,
    )
    return review


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


def _program_by_id(program_id: str):
    for program in default_world_programs():
        if program.program_id == program_id:
            return program
    raise HTTPException(status_code=404, detail="Possible-world program not found.")


@app.get("/possible-worlds/programs", dependencies=[Depends(require_token)])
def list_possible_world_programs() -> list[dict[str, object]]:
    synthesizer = WorldTechnologySynthesizer()
    output: list[dict[str, object]] = []
    for program in default_world_programs():
        decision = synthesizer.evaluate(program)
        output.append({
            "program_id": program.program_id,
            "worlds": [
                {
                    "world_id": world.world_id,
                    "title": world.title,
                    "prior": world.prior,
                    "epistemic_label": world.epistemic_label,
                }
                for world in program.worlds
            ],
            "experiments": [
                {
                    "experiment_id": experiment.experiment_id,
                    "title": experiment.title,
                    "cost": experiment.cost,
                    "time": experiment.time,
                    "risk": experiment.risk,
                    "requires_human_approval": experiment.requires_human_approval,
                }
                for experiment in program.experiments
            ],
            "next_experiment": (
                decision.next_experiment.__dict__
                if decision.next_experiment
                else None
            ),
            "unresolved_world_pairs": decision.unresolved_world_pairs,
        })
    return output


@app.get("/possible-worlds/programs/{program_id}", dependencies=[Depends(require_token)])
def possible_world_program(program_id: str) -> dict[str, object]:
    program = _program_by_id(program_id)
    decision = WorldTechnologySynthesizer().evaluate(program)
    return {
        "program_id": program.program_id,
        "worlds": [
            {
                "world_id": world.world_id,
                "title": world.title,
                "prior": world.prior,
                "assumptions": world.assumptions,
                "source_refs": world.source_refs,
                "epistemic_label": world.epistemic_label,
            }
            for world in program.worlds
        ],
        "experiments": [experiment.__dict__ for experiment in program.experiments],
        "next_experiment": (
            decision.next_experiment.__dict__
            if decision.next_experiment
            else None
        ),
        "technology_results": [result.__dict__ for result in decision.technology_results],
        "unresolved_world_pairs": decision.unresolved_world_pairs,
    }


@app.post(
    "/possible-worlds/programs/{program_id}/observe",
    dependencies=[Depends(require_token)],
)
def observe_possible_world(
    program_id: str,
    request: WorldObservationRequest,
) -> dict[str, object]:
    program = _program_by_id(program_id)
    experiment_ids = {x.experiment_id for x in program.experiments}
    if request.experiment_id not in experiment_ids:
        raise HTTPException(status_code=404, detail="Experiment not found in program.")

    lab = PossibleWorldsLab()
    posterior = lab.posterior(program.worlds, request.experiment_id, request.outcome)
    gaps = lab.reality_gaps(program.worlds, request.experiment_id, request.outcome)
    observation_id = f"world-observation:{uuid4().hex[:12]}"
    payload = {
        "program_id": program_id,
        "experiment_id": request.experiment_id,
        "outcome": request.outcome,
        "posterior": posterior.__dict__,
        "reality_gaps": [gap.__dict__ for gap in gaps],
    }
    save_record(
        "world_observation",
        observation_id,
        title=f"{program_id}:{request.experiment_id}",
        data=payload,
    )
    return payload


@app.get("/records/{kind}", dependencies=[Depends(require_token)])
def list_records(kind: str) -> list[dict[str, object]]:
    return list_record_dicts(kind)
