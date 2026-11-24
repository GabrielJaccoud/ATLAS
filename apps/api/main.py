from __future__ import annotations

import hmac
import base64
import hashlib
import json
import httpx
import smtplib
import ssl
import time
import tempfile
import wave
from email.message import EmailMessage
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Literal
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape

from uuid import uuid4

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
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


class ResearchFinding(BaseModel):
    source_id: str = Field(default="", max_length=300)
    title: str = Field(min_length=4, max_length=500)
    summary: str = Field(min_length=10, max_length=12000)
    what_happened: str = Field(default="", max_length=4000)
    background: str = Field(default="", max_length=4000)
    why_it_matters: str = Field(default="", max_length=4000)
    implications: str = Field(default="", max_length=4000)
    glossary: dict[str, str] = Field(default_factory=dict)
    recommended_action: str = Field(default="", max_length=4000)
    limits: str = Field(default="", max_length=4000)
    source_url: str = Field(default="", max_length=2000)
    published_at: str = Field(default="", max_length=80)
    source_type: Literal["scientific_paper", "technical_report", "official_report", "news_article", "news", "ministry_report", "internal_hypothesis", "other"] = "other"
    ministry_id: str = Field(default="research_evolution", max_length=120)
    hypothesis_ids: list[str] = Field(default_factory=list, max_length=30)
    tags: list[str] = Field(default_factory=list, max_length=40)
    confidence: float = Field(default=0.5, ge=0, le=1)
    priority: float = Field(default=0.5, ge=0, le=1)
    evidence_class: str = Field(default="unverified_report", max_length=100)


class ResearchIntakeRequest(BaseModel):
    batch_id: str = Field(default="", max_length=200)
    producer: str = Field(default="external_research_routine", max_length=200)
    generated_at: str = Field(default="", max_length=80)
    findings: list[ResearchFinding] = Field(min_length=1, max_length=100)


class ResearchInvestigationRequest(BaseModel):
    question: str = Field(min_length=8, max_length=4000)
    ministry_id: str = Field(default="research_evolution", max_length=120)
    hypothesis_ids: list[str] = Field(default_factory=list, max_length=30)


class ResearchGoalUpdate(BaseModel):
    status: Literal["planned", "in_progress", "blocked", "completed", "deferred"]
    note: str = Field(default="", max_length=3000)


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
    def get(key: str) -> str:
        return str(work.get(f"{key}_{language}") or "")

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


def build_scientific_work_html(work: dict[str, object], language: Literal["pt", "en"]) -> str:
    english = language == "en"
    def get(key: str) -> str:
        return str(work.get(f"{key}_{language}") or "")

    sections = (
        [("Abstract", "abstract"), ("Research question and origin", "question"),
         ("Assumptions and model", "assumptions"), ("Methodology and experiments", "methodology"),
         ("Theorem, proof and result" if work.get("work_type") == "mathematical_result" else "Results", "results"),
         ("Testable predictions", "predictions"), ("Uncertainty", "uncertainty"),
         ("Limitations and alternatives", "limitations")]
        if english else
        [("Resumo", "abstract"), ("Pergunta e origem da pesquisa", "question"),
         ("Premissas e modelo", "assumptions"), ("Métodos e experimentos", "methodology"),
         ("Teorema, demonstração e resultado" if work.get("work_type") == "mathematical_result" else "Resultados", "results"),
         ("Previsões testáveis", "predictions"), ("Incertezas", "uncertainty"),
         ("Limitações e explicações alternativas", "limitations")]
    )
    title = escape(get("title"))
    evidence = escape(str(work.get("claim_classification", "")).replace("_", " "))
    author = escape(str(work.get("author_name", "Gabriel Jaccoud")))
    ministry = escape(str(work.get("ministry_id", "")))
    body = "\n".join(
        f"<section><h2>{escape(heading)}</h2><p>{escape(get(key)).replace(chr(10), '<br>')}</p></section>"
        for heading, key in sections
    )
    references = work.get("references", [])
    refs = "".join(f"<li>{escape(str(reference))}</li>" for reference in references if isinstance(references, list))
    refs_title = "References" if english else "Referências"
    review_note = ("AI-assisted content must be reviewed by the responsible author before external submission."
                   if english else "O conteúdo elaborado com apoio de IA deve ser revisado pelo autor responsável antes de submissão externa.")
    return f"""<!doctype html><html lang="{'en' if english else 'pt-BR'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{title}</title><style>body{{font:17px/1.7 Georgia,serif;color:#222;background:#f4f1eb;margin:0}}main{{max-width:850px;margin:4rem auto;padding:3rem;background:white;box-shadow:0 12px 50px #14182118}}h1{{line-height:1.2}}h2{{font:600 1.2rem Arial,sans-serif;margin-top:2rem;color:#304254}}.meta,.note{{font:14px/1.6 Arial,sans-serif;color:#66717c}}@media(max-width:700px){{main{{margin:0;padding:1.5rem}}}}</style></head><body><main><p class="meta">ATLAS · {evidence}</p><h1>{title}</h1><p class="meta">{author} · {ministry}</p>{body}<section><h2>{refs_title}</h2><ol>{refs}</ol></section><p class="note">{escape(review_note)}</p></main></body></html>"""


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


@app.get("/publications/{publication_id}/html", dependencies=[Depends(require_token)])
def download_scientific_work_html(publication_id: str, language: Literal["pt", "en"] = "pt") -> Response:
    work = get_exportable_scientific_work(publication_id)
    document = build_scientific_work_html(work, language)
    return Response(content=document, media_type="text/html; charset=utf-8", headers={"Content-Disposition": f'attachment; filename="ATLAS-{language}-{publication_id.replace(":", "-")}.html"'})


@app.post("/vision/posture-assessment", dependencies=[Depends(require_token)])
async def posture_assessment(images: list[UploadFile] = File(...), views: list[str] = File(...)) -> dict[str, object]:
    """Return a visual screening report from user-supplied front/side photos without retaining the images."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="A análise visual precisa de um provedor multimodal configurado no ATLAS.")
    if len(images) < 2 or len(images) > 4 or len(images) != len(views):
        raise HTTPException(status_code=422, detail="Envie de 2 a 4 imagens, cada uma identificada como frontal, lateral ou posterior.")
    accepted = {"image/jpeg", "image/png", "image/webp"}
    image_parts = []
    for image, view in zip(images, views, strict=False):
        if image.content_type not in accepted:
            raise HTTPException(status_code=415, detail="Use imagens JPG, PNG ou WebP.")
        content = await image.read()
        if not content or len(content) > 8 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Cada imagem deve ter até 8 MB.")
        data_url = f"data:{image.content_type};base64,{base64.b64encode(content).decode('ascii')}"
        image_parts.append({"type": "input_image", "image_url": data_url, "detail": "high"})
        image_parts.append({"type": "input_text", "text": f"Vista indicada pelo usuário: {view}. Considere perspectiva, roupa, pose e qualidade da captura."})
    prompt = (
        "Faça uma triagem visual observacional de postura e alinhamento corporal a partir das fotos fornecidas. "
        "Não diagnostique escoliose, lesão, doença ou causa. Informe primeiro se as imagens permitem avaliação e a qualidade/limitações. "
        "Descreva apenas sinais diretamente visíveis (por exemplo, inclinação aparente dos ombros, alinhamento aproximado da cabeça, "
        "simetria aparente, distribuição de peso apenas se inferível), diferencie observação de hipótese e dê nível de confiança baixo/médio/alto. "
        "Não estime ângulos exatos sem referência calibrada. Sugira uma nova captura específica quando necessário e próximos passos proporcionais. "
        "Se houver dor intensa, fraqueza, dormência ou piora rápida, recomende avaliação clínica. Responda em português, claro, com seções: "
        "Qualidade da captura; Observações; O que não é possível concluir; Próximo passo. Não afirme que uma câmera mede temperatura ou faz ressonância."
    )
    payload = {"model": settings.openai_model, "input": [
        {"role": "system", "content": "Você é um assistente de triagem visual cuidadoso. Relate observações, não diagnósticos."},
        {"role": "user", "content": [{"type": "input_text", "text": prompt}, *image_parts]},
    ]}
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f"{settings.openai_base_url}/responses", headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as error:
        raise HTTPException(status_code=502, detail="O provedor não aceitou a análise visual. Verifique o modelo configurado e tente novamente.") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Não foi possível alcançar o provedor de análise visual.") from error
    text_parts = [part["text"] for item in data.get("output", []) if item.get("type") == "message" for part in item.get("content", []) if part.get("type") in {"output_text", "text"} and part.get("text")]
    if not text_parts:
        raise HTTPException(status_code=502, detail="O provedor não retornou um relatório legível.")
    return {"report": "\n".join(text_parts), "classification": "triagem_visual_observacional", "images_retained": False, "provider": "openai", "model": settings.openai_model}


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


@app.post("/media/transcribe", dependencies=[Depends(require_token)])
async def transcribe_media(file: UploadFile = File(...)) -> dict[str, object]:
    """Transcribe uploaded audio/video without retaining either the media or transcript."""
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="A transcrição precisa de um provedor de áudio configurado no ATLAS.")
    filename = Path(file.filename or "media").name
    content_type = (file.content_type or "").lower()
    allowed_types = {
        "audio/mpeg", "audio/mp3", "audio/mp4", "audio/m4a", "audio/wav", "audio/x-wav",
        "audio/ogg", "audio/webm", "audio/flac", "video/mp4", "video/webm", "video/quicktime",
        "video/x-matroska", "application/octet-stream",
    }
    if content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Envie áudio ou vídeo MP3, M4A, WAV, OGG, FLAC, MP4, WebM ou MOV.")
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size <= 0 or size > 512 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="O arquivo precisa ter até 512 MB e conter dados.")

    try:
        import av
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="O decodificador de mídia não está instalado nesta API.") from exc
    try:
        input_container = av.open(file.file)
        audio_stream = next((stream for stream in input_container.streams if stream.type == "audio"), None)
        if audio_stream is None:
            input_container.close()
            raise HTTPException(status_code=422, detail="Não encontrei uma faixa de áudio neste arquivo.")
        resampler = av.AudioResampler(format="s16", layout="mono", rate=16000)
        with tempfile.TemporaryDirectory(prefix="atlas-transcribe-") as temp_dir:
            wav_path = Path(temp_dir) / "audio.wav"
            with wave.open(str(wav_path), "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                for frame in input_container.decode(audio_stream):
                    for converted in resampler.resample(frame):
                        wav_file.writeframesraw(converted.to_ndarray().tobytes())
                        if wav_file.tell() * 2 > 24 * 1024 * 1024:
                            raise HTTPException(status_code=413, detail="O áudio extraído excede 24 MB; envie um trecho menor.")
                for converted in resampler.resample(None):
                    wav_file.writeframesraw(converted.to_ndarray().tobytes())
            input_container.close()
            wav_size = wav_path.stat().st_size
            if wav_size > 25 * 1024 * 1024:
                raise HTTPException(status_code=413, detail="O áudio extraído excede 25 MB; envie um trecho menor.")
            with wav_path.open("rb") as audio_file:
                async with httpx.AsyncClient(timeout=240) as client:
                    response = await client.post(
                        f"{settings.openai_base_url}/audio/transcriptions",
                        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                        data={"model": settings.openai_transcription_model, "response_format": "json"},
                        files={"file": (f"{Path(filename).stem}.wav", audio_file, "audio/wav")},
                    )
            if response.is_error:
                raise HTTPException(status_code=502, detail="O provedor não concluiu a transcrição. Verifique o limite e tente novamente.")
            result = response.json()
            transcript = str(result.get("text", "")).strip()
            if not transcript:
                raise HTTPException(status_code=422, detail="O provedor não reconheceu fala neste arquivo.")
            return {
                "filename": filename,
                "transcript": transcript,
                "model": settings.openai_transcription_model,
                "media_retained": False,
                "transcript_retained": False,
            }
    except HTTPException:
        raise
    except (av.error.FFmpegError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="Não foi possível decodificar a faixa de áudio. Tente outro formato ou arquivo.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="O provedor de transcrição está indisponível neste momento.") from exc


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
        "provider": {
            "openai_configured": bool(settings.openai_api_key),
            "ollama_configured": bool(settings.ollama_url),
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


def research_intake_allowed(authorization: str | None, automation_key: str | None) -> bool:
    if automation_key and settings.research_automation_token and hmac.compare_digest(automation_key, settings.research_automation_token):
        return True
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        return token == settings.api_token or verify_session_token(token)
    return False


def latest_records(kind: str) -> list[dict[str, object]]:
    latest: dict[str, dict[str, object]] = {}
    for record in list_record_dicts(kind):
        latest.setdefault(str(record["external_id"]), record)
    return list(latest.values())


def store_research_intake(request: ResearchIntakeRequest) -> dict[str, object]:
    inserted: list[dict[str, object]] = []
    duplicates = 0
    now = datetime.now(timezone.utc).isoformat()
    for finding in request.findings:
        source_identity = finding.source_id.strip() or finding.source_url.strip() or f"{finding.title}|{finding.summary[:300]}"
        fingerprint = hashlib.sha256(source_identity.encode("utf-8")).hexdigest()[:20]
        external_id = f"research_finding:{fingerprint}"
        existing = get_record("research_finding", external_id)
        if existing:
            duplicates += 1
            continue
        data = {
            **finding.model_dump(),
            "finding_id": external_id,
            "producer": request.producer,
            "batch_id": request.batch_id,
            "generated_at": request.generated_at,
            "ingested_at": now,
            "triage_status": "unverified",
            "source_verification": "pending",
        }
        inserted.append(save_record("research_finding", external_id, title=finding.title, body=finding.summary, data=data))
    return {"received": len(request.findings), "inserted": len(inserted), "duplicates": duplicates, "findings": [item["data"] for item in inserted]}


@lru_cache(maxsize=1)
def github_oidc_jwks() -> dict[str, object]:
    response = httpx.get("https://token.actions.githubusercontent.com/.well-known/jwks", timeout=8)
    response.raise_for_status()
    return response.json()


def verify_github_actions_token(authorization: str | None) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        return False
    token = authorization.removeprefix("Bearer ").strip()
    try:
        encoded_header, encoded_claims, encoded_signature = token.split(".")
        def decode(part: str) -> bytes:
            return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))

        header = json.loads(decode(encoded_header))
        claims = json.loads(decode(encoded_claims))
        if header.get("alg") != "RS256" or claims.get("iss") != "https://token.actions.githubusercontent.com":
            return False
        if claims.get("aud") != "atlas-research-intake":
            return False
        if int(claims.get("exp", 0)) < int(time.time()) or int(claims.get("nbf", 0)) > int(time.time()) + 60:
            return False
        expected_workflow = f"{settings.github_research_repo}/{settings.github_research_workflow}@{settings.github_research_ref}"
        if claims.get("repository") != settings.github_research_repo:
            return False
        if claims.get("ref") != settings.github_research_ref or claims.get("workflow_ref") != expected_workflow:
            return False
        keys = github_oidc_jwks().get("keys", [])
        jwk = next((key for key in keys if key.get("kid") == header.get("kid")), None)
        if not jwk or jwk.get("kty") != "RSA":
            return False
        public_key = rsa.RSAPublicNumbers(
            int.from_bytes(decode(str(jwk["e"])), "big"),
            int.from_bytes(decode(str(jwk["n"])), "big"),
        ).public_key()
        public_key.verify(decode(encoded_signature), f"{encoded_header}.{encoded_claims}".encode(), padding.PKCS1v15(), hashes.SHA256())
        return True
    except (httpx.HTTPError, InvalidSignature, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False


async def search_research_sources(question: str, ministry_id: str, hypothesis_ids: list[str], producer: str) -> dict[str, object]:
    if not settings.openai_api_key:
        raise HTTPException(status_code=503, detail="A pesquisa web automática precisa de uma chave OpenAI configurada no serviço API do ATLAS.")
    hypotheses = latest_records("research_hypothesis") + latest_records("hypothesis")
    backlog = latest_records("research")
    hypothesis_context = [
        {"id": row["external_id"], "claim": row["data"].get("title", row["data"].get("question", row.get("title", "")))}
        for row in hypotheses[:40]
    ]
    backlog_context = [
        {"ministry": row["data"].get("ministry_id"), "question": row["data"].get("question"), "status": row["data"].get("status")}
        for row in backlog[:40]
    ]
    ministry_names = [{"id": ministry.ministry_id, "name": ministry.name, "skills": list(ministry.skills)} for ministry in registry.values()]
    research_prompt = f"""Pesquise na web por fontes novas e relevantes ao objetivo abaixo. Use busca web, priorize artigos científicos, dados primários, órgãos oficiais e documentos de ministérios. Distinga data do evento e data de publicação; evite duplicatas e inclua URL direta. Não trate alegação como fato sem evidência. Hipóteses especulativas, tradições e relatos devem ser classificados como tais, incluindo contraevidências quando encontradas.

Ao cobrir ciência e tecnologia, inclua de forma recorrente (sem fabricar novidade quando não houver): neurociência, optogenética, neurotecnologia e interfaces cérebro-computador; computação e IA, inclusive métodos inspirados biologicamente; biotecnologia, incluindo edição genética, organoides e biologia sintética. Compare o avanço com o estado anterior e diga se é demonstração em células/animais, estudo observacional ou resultado clínico em humanos. Não apresente potencial translacional como tratamento comprovado.

Objetivo/tema: {question}
Ministério de entrada: {ministry_id}
Hipóteses registradas: {json.dumps(hypothesis_context, ensure_ascii=False)}
Backlog de pesquisa: {json.dumps(backlog_context, ensure_ascii=False)}
Ministérios disponíveis: {json.dumps(ministry_names, ensure_ascii=False)}

 Retorne somente um objeto JSON válido com as chaves `report` e `findings`. `report` deve resumir as mudanças, separar fato/inferência/hipótese e sugerir próximos passos concretos. `findings` deve conter até seis itens, cada um com: source_id (estável; DOI ou URL quando houver), title, summary (síntese concisa), what_happened (o achado em linguagem simples), background (de onde veio e o contexto anterior necessário), why_it_matters, implications (consequências plausíveis, explicitando inferência), glossary (objeto com siglas/termos e definição curta; use {{}} se não houver), recommended_action (passo seguro e executável para ATLAS, ou "monitorar" se não houver ação justificada), limits (o que o estudo não demonstra e seus limites), source_url, published_at (ISO quando disponível), source_type (scientific_paper, technical_report, official_report, news_article, news, ministry_report, internal_hypothesis ou other), ministry_id (id da lista ou research_evolution), hypothesis_ids (apenas IDs listados acima), tags (lista), confidence (0 a 1, refletindo a qualidade da evidência), priority (0 a 1), evidence_class (ex.: primary_source, peer_reviewed, official_report, unverified_report, contrary_evidence). Explique siglas na primeira ocorrência e escreva para quem está começando, sem infantilizar nem presumir conhecimento prévio. Se não houver achado novo e útil, retorne findings vazio e explique no report. Responda em português. Não gere diagnósticos médicos nem confirme fenômenos extraordinários sem evidência independente."""
    payload = {
        "model": settings.openai_model,
        "tools": [{"type": "web_search"}],
        "input": [
            {"role": "system", "content": "Você é o pesquisador e professor do ATLAS. Apure fontes, retenha proveniência, explique contexto e siglas com clareza, e declare incerteza; não invente referências nem resultados."},
            {"role": "user", "content": research_prompt},
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=150) as client:
            response = await client.post(
                f"{settings.openai_base_url.rstrip('/')}/responses",
                headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPStatusError as error:
        raise HTTPException(status_code=502, detail="O provedor de pesquisa web não aceitou a solicitação. Verifique modelo e acesso à ferramenta web_search.") from error
    except httpx.HTTPError as error:
        raise HTTPException(status_code=502, detail="Não foi possível conectar ao provedor de pesquisa web.") from error
    output_text = "\n".join(
        part["text"] for item in result.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []) if part.get("type") in {"output_text", "text"} and part.get("text")
    ).strip()
    if not output_text:
        raise HTTPException(status_code=502, detail="A pesquisa web não retornou conteúdo legível.")
    cleaned = output_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").removeprefix("json").strip()
    try:
        parsed = json.loads(cleaned)
        report = str(parsed.get("report", "")).strip()
        findings = parsed.get("findings", [])
        intake = ResearchIntakeRequest(
            batch_id=f"{producer}:{datetime.now(ZoneInfo('America/Sao_Paulo')).date().isoformat()}:{uuid4().hex[:8]}",
            producer=producer,
            generated_at=datetime.now(timezone.utc).isoformat(),
            findings=findings,
        ) if findings else None
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as error:
        raise HTTPException(status_code=502, detail="O relatório recebido não seguiu o formato de pesquisa do ATLAS; nenhum item foi gravado.") from error
    intake_result = store_research_intake(intake) if intake else {"received": 0, "inserted": 0, "duplicates": 0, "findings": []}
    if intake_result["inserted"]:
        plan = make_daily_research_plan(force=True)
    else:
        plan = None
    return {"report": report, "intake": intake_result, "daily_plan": plan, "provider": "openai", "model": settings.openai_model, "response_id": result.get("id")}


@app.get("/research/central", dependencies=[Depends(require_token)])
def research_central() -> dict[str, object]:
    findings = latest_records("research_finding")
    plans = latest_records("research_daily_plan")
    hypotheses = latest_records("research_hypothesis") + latest_records("hypothesis")
    backlog = latest_records("research")
    runs = latest_records("research_run")
    return {
        "findings": [row["data"] for row in findings[:100]],
        "hypotheses": [row["data"] for row in hypotheses[:100]],
        "backlog": [row["data"] for row in backlog[:100]],
        "latest_plan": plans[0]["data"] if plans else None,
        "latest_run": runs[0]["data"] if runs else None,
        "automation_bridge": {
            "endpoint": "/research/automation/intake",
            "authentication": "X-Atlas-Automation-Key",
            "configured": bool(settings.research_automation_token),
            "web_search_configured": bool(settings.openai_api_key),
            "smtp_configured": bool(settings.publication_email and settings.smtp_host and settings.smtp_username and settings.smtp_password),
            "scheduled_chat_tasks_connected": False,
        },
        "publication_email": {"configured": bool(settings.publication_email and settings.smtp_host and settings.smtp_username and settings.smtp_password), "recipient": settings.publication_email},
    }


@app.post("/research/intake", dependencies=[Depends(require_token)])
def research_intake(request: ResearchIntakeRequest) -> dict[str, object]:
    return store_research_intake(request)


@app.post("/research/automation/intake")
def research_automation_intake(
    request: ResearchIntakeRequest,
    authorization: str | None = Header(default=None),
    x_atlas_automation_key: str | None = Header(default=None),
) -> dict[str, object]:
    if not settings.research_automation_token:
        raise HTTPException(status_code=503, detail="A chave privada da ponte de automação ainda não foi configurada.")
    if not research_intake_allowed(authorization, x_atlas_automation_key):
        raise HTTPException(status_code=401, detail="Credencial de ingestão inválida.")
    return store_research_intake(request)


@app.post("/research/github-intake")
def research_github_intake(
    request: ResearchIntakeRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    if not verify_github_actions_token(authorization):
        raise HTTPException(status_code=401, detail="Token GitHub Actions inválido ou fora do escopo autorizado.")
    return store_research_intake(request)


@app.post("/research/investigate", dependencies=[Depends(require_token)])
async def investigate_research_topic(request: ResearchInvestigationRequest) -> dict[str, object]:
    result = await search_research_sources(request.question, request.ministry_id, request.hypothesis_ids, "atlas-web-investigation")
    run_id = f"research-run:{uuid4().hex[:12]}"
    run = {"run_id": run_id, "trigger": "user_request", "question": request.question, "ministry_id": request.ministry_id, "status": "completed", "finding_count": result["intake"]["inserted"], "provider": result["provider"], "model": result["model"], "completed_at": datetime.now(timezone.utc).isoformat()}
    save_record("research_run", run_id, title=request.question, body=result["report"], data=run)
    return {**result, "run": run}


@app.post("/research/automation/daily-run")
async def daily_automated_research(
    authorization: str | None = Header(default=None),
    x_atlas_automation_key: str | None = Header(default=None),
) -> dict[str, object]:
    if not settings.research_automation_token:
        raise HTTPException(status_code=503, detail="A chave privada da ponte de automação ainda não foi configurada.")
    if not research_intake_allowed(authorization, x_atlas_automation_key):
        raise HTTPException(status_code=401, detail="Credencial de automação inválida.")
    questions = [str(row["data"].get("question", "")) for row in latest_records("research")[:8] if row["data"].get("question")]
    hypothesis_titles = [str(row["data"].get("title", row["data"].get("question", ""))) for row in (latest_records("research_hypothesis") + latest_records("hypothesis"))[:12]]
    focus = "\n".join([f"Backlog: {item}" for item in questions] + [f"Hipótese: {item}" for item in hypothesis_titles])
    question = "Faça a varredura diária das mudanças científicas, notícias verificáveis e fontes primárias relevantes aos ministérios do ATLAS nas últimas 24 horas. Relacione os achados ao backlog e hipóteses abaixo, priorize novidade, relevância, força da evidência, contraevidência e possibilidade de produzir um teste ou entrega hoje. Se não houver mudança confiável, informe isso e não fabrique achados.\n" + (focus or "Não há hipóteses estruturadas suficientes ainda; faça uma triagem transversal por especialidade ministerial e registre lacunas de conhecimento.")
    try:
        result = await search_research_sources(question, "research_evolution", [], "atlas-daily-research")
    except HTTPException as error:
        run_id = f"research-run:{uuid4().hex[:12]}"
        save_record("research_run", run_id, title="ATLAS Daily Research", data={"run_id": run_id, "trigger": "daily_schedule", "status": "failed", "error": error.detail, "completed_at": datetime.now(timezone.utc).isoformat()})
        raise
    plan = result["daily_plan"] or make_daily_research_plan(force=True)
    email = None
    if int(result["intake"]["inserted"]) > 0 and settings.publication_email and all((settings.smtp_host, settings.smtp_username, settings.smtp_password)):
        email = email_research_daily_plan(str(plan["plan_id"]))
    run_id = f"research-run:{uuid4().hex[:12]}"
    run = {"run_id": run_id, "trigger": "daily_schedule", "status": "completed", "finding_count": result["intake"]["inserted"], "email_sent": bool(email), "completed_at": datetime.now(timezone.utc).isoformat()}
    save_record("research_run", run_id, title="ATLAS Daily Research", body=result["report"], data=run)
    return {"report": result["report"], "daily_plan": plan, "run": run, "email": email}


@app.get("/research/automation/health")
def research_automation_health(
    authorization: str | None = Header(default=None),
    x_atlas_automation_key: str | None = Header(default=None),
) -> dict[str, object]:
    if not settings.research_automation_token:
        raise HTTPException(status_code=503, detail="A chave privada da ponte ainda não está configurada.")
    if not research_intake_allowed(authorization, x_atlas_automation_key):
        raise HTTPException(status_code=401, detail="Credencial de automação inválida.")
    return {
        "automation_bridge_configured": True,
        "web_search_configured": bool(settings.openai_api_key),
        "web_search_model": settings.openai_model if settings.openai_api_key else None,
        "email_configured": bool(settings.publication_email and settings.smtp_host and settings.smtp_username and settings.smtp_password),
        "scheduled_chat_tasks_connected": False,
    }


def make_daily_research_plan(force: bool = False) -> dict[str, object]:
    today = datetime.now(ZoneInfo("America/Sao_Paulo")).date().isoformat()
    plan_id = f"research-daily:{today}"
    existing = get_record("research_daily_plan", plan_id)
    if existing and not force:
        return existing["data"]
    cutoff = datetime.now(timezone.utc).timestamp() - 36 * 60 * 60
    findings = []
    for row in latest_records("research_finding"):
        data = row["data"]
        try:
            ingested = datetime.fromisoformat(str(data.get("ingested_at", "")).replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            ingested = 0
        if ingested >= cutoff:
            findings.append(data)
    backlog = [row["data"] for row in latest_records("research") if str(row["data"].get("status", "idea")) not in {"complete", "completed", "done", "deferred"}]
    findings.sort(key=lambda item: (float(item.get("priority", 0.5)) * 0.65 + float(item.get("confidence", 0.5)) * 0.35, str(item.get("ingested_at", ""))), reverse=True)
    selected = findings[:10]
    goals: list[dict[str, object]] = []
    ria_candidates: list[dict[str, object]] = []
    all_hypotheses = latest_records("research_hypothesis") + latest_records("hypothesis")
    hypotheses_by_id = {str(row["external_id"]): row["data"] for row in all_hypotheses}
    for index, finding in enumerate(selected[:3], start=1):
        explicit_ids = [str(value) for value in finding.get("hypothesis_ids", []) if str(value) in hypotheses_by_id]
        haystack = f"{finding.get('title', '')} {finding.get('summary', '')} {' '.join(finding.get('tags', []))}".casefold()
        if not explicit_ids:
            for hypothesis_id, hypothesis in hypotheses_by_id.items():
                title = str(hypothesis.get("title", hypothesis.get("question", "")))
                terms = [term for term in title.casefold().split() if len(term) > 4]
                if terms and sum(term in haystack for term in terms) >= max(1, min(2, len(terms))):
                    explicit_ids.append(hypothesis_id)
        ministry_id = str(finding.get("ministry_id", "research_evolution"))
        objective = f"Verificar e comparar: {finding.get('title', 'achado de pesquisa')}"
        route = orchestrator.route(Mission(mission_id=f"research-route:{uuid4().hex[:8]}", objective=objective, required_skills=("research", "analysis")))
        ministries = list(route.primary_ministries) or [ministry_id]
        finding_id = str(finding.get("finding_id", ""))
        if finding.get("source_url"):
            goals.append({"goal_id": f"goal:{today}:{index}:source", "title": f"Apurar a fonte: {finding.get('title', '')}", "action": "Conferir publicação, data, método, contexto e fonte primária; registrar evidências contrárias.", "deliverable": "Ficha de apuração com URL primária, data e classificação de evidência.", "status": "planned", "source_ids": [finding_id], "hypothesis_ids": explicit_ids, "ministries": ministries, "done_criteria": "Fonte primária aberta e alegação classificada; divergências registradas."})
        if explicit_ids:
            goals.append({"goal_id": f"goal:{today}:{index}:hypothesis", "title": f"Atualizar hipótese relacionada a {finding.get('title', 'novo achado')}", "action": "Comparar o achado com a hipótese, buscar suporte e contraevidência e atualizar a incerteza sem promover a conclusão automaticamente.", "deliverable": "Nota de atualização vinculada à hipótese e ao achado.", "status": "planned", "source_ids": [finding_id], "hypothesis_ids": explicit_ids, "ministries": ministries, "done_criteria": "Relação registrada como suporte, contradição ou inconclusiva, com justificativa."})
        tags = [str(tag).lower() for tag in finding.get("tags", [])]
        if finding.get("source_type") in {"scientific_paper", "ministry_report", "internal_hypothesis"} or tags:
            candidate_id = f"ria-candidate:{hashlib.sha256(finding_id.encode()).hexdigest()[:16]}"
            candidate = {"candidate_id": candidate_id, "source_ids": [finding_id], "title": str(finding.get("title", "")), "hypothesis_ids": explicit_ids, "stage": "source_triage", "status": "candidate_only", "method": "RIA + engenharia reversa", "steps": ["identificar função/efeito alegado", "separar mecanismo observado de interpretação", "mapear entradas, materiais, energia e controles conhecidos", "buscar análogos naturais/tecnológicos", "registrar lacunas e explicações alternativas", "propor teste mínimo discriminante e reversível"], "evidence_class": str(finding.get("evidence_class", "unverified_report")), "human_review_required": True, "created_at": datetime.now(timezone.utc).isoformat()}
            if not get_record("ria_candidate", candidate_id):
                save_record("ria_candidate", candidate_id, title=candidate["title"], data=candidate)
            ria_candidates.append(candidate)
            goals.append({"goal_id": f"goal:{today}:{index}:ria", "title": f"RIA e engenharia reversa: {finding.get('title', '')}", "action": "Decompor o efeito alegado em função, entradas, mecanismo possível, análogos, lacunas e um experimento mínimo discriminante.", "deliverable": "Ficha RIA em estágio de triagem, sem tratar hipótese como tecnologia demonstrada.", "status": "planned", "source_ids": [finding_id], "hypothesis_ids": explicit_ids, "ministries": ministries, "done_criteria": "Mecanismo e desconhecidos descritos; teste mínimo e riscos identificados."})
    if not goals and backlog:
        item = backlog[0]
        objective = str(item.get("question", "Pesquisa pendente"))
        route = orchestrator.route(Mission(mission_id=f"research-route:{uuid4().hex[:8]}", objective=objective, required_skills=("research", "analysis")))
        goals.append({"goal_id": f"goal:{today}:backlog", "title": f"Avançar pesquisa pendente: {objective}", "action": "Definir a fonte primária necessária e o menor passo de investigação que reduza a incerteza.", "deliverable": "Plano curto de apuração com evidência esperada e critério de encerramento.", "status": "planned", "source_ids": [], "hypothesis_ids": [], "ministries": list(route.primary_ministries), "done_criteria": "Próxima evidência ou teste documentado; sem alegar descoberta sem suporte."})
    goals = goals[:8]
    plan = {"plan_id": plan_id, "date": today, "created_at": datetime.now(timezone.utc).isoformat(), "status": "ready" if selected else ("backlog_only" if goals else "no_inputs"), "input_count": len(selected), "summary": f"{len(selected)} achado(s) recebido(s), {len(goals)} meta(s) proposta(s), {len(ria_candidates)} candidato(s) RIA em triagem.", "findings": selected, "goals": goals, "ria_candidates": ria_candidates, "epistemic_rule": "Achados não confirmados permanecem em triagem; nenhuma hipótese é promovida automaticamente a conclusão ou artigo."}
    save_record("research_daily_plan", plan_id, title=f"Plano diário de pesquisa · {today}", body=plan["summary"], data=plan)
    return plan


@app.post("/research/daily-plan", dependencies=[Depends(require_token)])
def create_research_daily_plan(force: bool = False) -> dict[str, object]:
    return make_daily_research_plan(force=force)


@app.post("/research/automation/plan")
def automation_research_plan(
    force: bool = False,
    authorization: str | None = Header(default=None),
    x_atlas_automation_key: str | None = Header(default=None),
) -> dict[str, object]:
    if not settings.research_automation_token:
        raise HTTPException(status_code=503, detail="A chave privada da ponte de automação ainda não foi configurada.")
    if not research_intake_allowed(authorization, x_atlas_automation_key):
        raise HTTPException(status_code=401, detail="Credencial de automação inválida.")
    plan = make_daily_research_plan(force=force)
    email = None
    if int(plan.get("input_count", 0)) > 0 and settings.publication_email and all((settings.smtp_host, settings.smtp_username, settings.smtp_password)):
        email = email_research_daily_plan(str(plan["plan_id"]))
    return {"plan": plan, "email": email, "ran_at": datetime.now(timezone.utc).isoformat()}


@app.patch("/research/goals/{goal_id}", dependencies=[Depends(require_token)])
def update_research_goal(goal_id: str, request: ResearchGoalUpdate) -> dict[str, object]:
    plans = latest_records("research_daily_plan")
    for row in plans:
        plan = row["data"]
        goals = plan.get("goals", [])
        for goal in goals:
            if goal.get("goal_id") == goal_id:
                goal["status"] = request.status
                goal["status_note"] = request.note
                goal["updated_at"] = datetime.now(timezone.utc).isoformat()
                if request.status == "completed":
                    goal["completed_at"] = goal["updated_at"]
                save_record("research_daily_plan", str(plan.get("plan_id", row["external_id"])), title=str(row.get("title", "Daily research plan")), body=str(plan.get("summary", "")), data=plan)
                return goal
    raise HTTPException(status_code=404, detail="Research goal not found.")


@app.post("/research/daily-plan/{plan_id}/email", dependencies=[Depends(require_token)])
def email_research_daily_plan(plan_id: str) -> dict[str, object]:
    plan = get_record("research_daily_plan", plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Daily research plan not found.")
    if not settings.publication_email or not all((settings.smtp_host, settings.smtp_username, settings.smtp_password)):
        raise HTTPException(status_code=503, detail="O envio de e-mail ainda não está configurado no ATLAS.")
    data = plan["data"]
    link = f"{settings.public_web_url.rstrip('/')}?screen=Pesquisa"
    message = EmailMessage()
    message["Subject"] = f"ATLAS · Central de Pesquisa · {data.get('date', '')}"
    message["From"] = settings.smtp_from or settings.smtp_username
    message["To"] = settings.publication_email
    message.set_content(f"{data.get('summary', '')}\n\nPlano e fontes no ATLAS: {link}\n\nOs achados permanecem em triagem até verificação de fonte e evidência.")
    message.add_alternative(f"<p>{escape(str(data.get('summary', '')))}</p><p><a href=\"{escape(link)}\">Abrir Central de Pesquisa do ATLAS</a></p><p>Os achados permanecem em triagem até verificação de fonte e evidência.</p>", subtype="html")
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=25) as server:
            if settings.smtp_use_tls:
                server.starttls(context=ssl.create_default_context())
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        raise HTTPException(status_code=502, detail="O ATLAS não conseguiu enviar o resumo por e-mail.") from error
    return {"sent": True, "to": settings.publication_email, "link": link}


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
