import React, { Suspense, useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { atlasFetch, loadConfig, pairOwner } from "./api";
import { RealtimeHandle, startRealtimeVoice } from "./realtime";
import "./design-system.css";
import "./styles.css";

const AtlasScene3D = React.lazy(() => import("./AtlasScene3D"));

type Status = {
  version?: string;
  mode?: { mode?: string };
  ministries?: Array<{ id: string; name: string }>;
  research?: { blocked: number };
  my_world?: { nodes: number; edges: number };
  provider?: { openai_configured?: boolean; ollama_configured?: boolean };
};

type WorldProgram = {
  program_id: string;
  worlds: Array<{
    world_id: string;
    title: string;
    prior: number;
    epistemic_label: string;
  }>;
  next_experiment?: {
    experiment_id: string;
    expected_information_gain: number;
    discrimination_power: number;
    efficiency: number;
  } | null;
};

type AtlasEvent = {
  event_id: string;
  event_type: string;
  source: string;
  payload: Record<string, unknown>;
  priority: number | string;
  tags?: string[];
  created_at?: string;
};

type ResearchItem = {
  item_id: string;
  ministry_id: string;
  question: string;
  status: string;
  priority: number;
};

type ResearchFindingRecord = {
  finding_id: string;
  title: string;
  summary: string;
  source_url: string;
  source_type: string;
  ministry_id: string;
  hypothesis_ids: string[];
  confidence: number;
  priority: number;
  triage_status: string;
  ingested_at: string;
};
type ResearchGoal = {
  goal_id: string;
  title: string;
  action: string;
  deliverable: string;
  status: "planned" | "in_progress" | "blocked" | "completed" | "deferred";
  source_ids: string[];
  hypothesis_ids: string[];
  ministries: string[];
  done_criteria: string;
};
type DailyResearchPlan = {
  plan_id: string;
  date: string;
  status: string;
  summary: string;
  findings: ResearchFindingRecord[];
  goals: ResearchGoal[];
  ria_candidates: Array<{ candidate_id: string; title: string; stage: string; status: string; steps: string[]; source_ids: string[] }>;
};
type ResearchCentralData = {
  findings: ResearchFindingRecord[];
  hypotheses: Array<Record<string, unknown>>;
  backlog: ResearchItem[];
  latest_plan: DailyResearchPlan | null;
  latest_run: Record<string, unknown> | null;
  automation_bridge: { endpoint: string; authentication: string; configured: boolean; web_search_configured: boolean; smtp_configured: boolean; scheduled_chat_tasks_connected: boolean };
  publication_email: { configured: boolean; recipient: string };
};

type ScientificWork = {
  publication_id: string;
  author_name: string;
  ministry_id: string;
  work_type: "mathematical_result" | "theoretical_physics" | "empirical_result";
  evidence_level: "internal_hypothesis" | "mathematical_proof" | "physical_viability" | "empirical_support" | "independent_replication";
  title_pt: string;
  title_en: string;
  abstract_pt: string;
  abstract_en: string;
  question_pt: string;
  question_en: string;
  assumptions_pt: string;
  assumptions_en: string;
  methodology_pt: string;
  methodology_en: string;
  results_pt: string;
  results_en: string;
  predictions_pt: string;
  predictions_en: string;
  uncertainty_pt: string;
  uncertainty_en: string;
  limitations_pt: string;
  limitations_en: string;
  references: string[];
  export_ready: boolean;
  missing_requirements: string[];
  claim_classification: string;
  review_required: boolean;
  created_at: string;
};

type PublicationDeliverySettings = { email: string; can_send_email: boolean };

type ReviewAgentResult = { role_id: string; title: string; provider: string; model: string; status: string; review: string };
type ReviewReport = {
  review_id: string;
  publication_id: string;
  generated_at: string;
  status: string;
  decision: string;
  source_verification: string;
  export_gate_changed: boolean;
  reviewers: ReviewAgentResult[];
};
type ReviewProvider = { id: string; model: string };
type PostureCapture = { file: File; view: "frontal" | "lateral" | "posterior" };

type ScientificWorkForm = Omit<ScientificWork, "publication_id" | "export_ready" | "missing_requirements" | "claim_classification" | "review_required" | "created_at" | "references"> & { referencesText: string };

type WorldData = {
  nodes: Array<{ node_id: string; kind: string; name: string; attributes?: Record<string, unknown> }>;
  edges: Array<{ edge_id: string; source: string; relation: string; target: string; weight: number }>;
};

type WorldObservation = {
  program_id: string;
  experiment_id: string;
  outcome: string;
  posterior: { probabilities: Record<string, number>; surprise_bits?: number };
};

type ApiRecord<T> = { data: T; created_at?: string };

type ChatMessage = {
  id: string;
  role: "user" | "assistant" | "error";
  content: string;
  createdAt: number;
};

function readChatHistory(): ChatMessage[] {
  try {
    const saved = localStorage.getItem("atlas.chat.history");
    const parsed = saved ? JSON.parse(saved) : [];
    return Array.isArray(parsed) ? parsed.filter((item) =>
      item && typeof item.id === "string" &&
      ["user", "assistant", "error"].includes(item.role) &&
      typeof item.content === "string" && typeof item.createdAt === "number",
    ).slice(-120) : [];
  } catch {
    return [];
  }
}

type HomeSignal = {
  eyebrow: string;
  title: string;
  description: string;
  action: ScreenId;
  actionLabel: string;
  tone: "calm" | "research" | "alert" | "critical";
  evidence?: string;
};

type ScreenId =
  | "Agora"
  | "Talk"
  | "Radar"
  | "Urgente"
  | "Ciência"
  | "Pesquisa"
  | "Mundos"
  | "Laboratório"
  | "Ministérios"
  | "Conselho"
  | "Apps"
  | "Awareness"
  | "Corpo"
  | "My World"
  | "Inovação"
  | "Ações";

const navigation: ScreenId[] = [
  "Agora",
  "Talk",
  "Radar",
  "Urgente",
  "Ciência",
  "Pesquisa",
  "Mundos",
  "Laboratório",
  "Ministérios",
  "Conselho",
  "Apps",
  "Awareness",
  "Corpo",
  "My World",
  "Inovação",
  "Ações",
];

const primaryMobile: ScreenId[] = ["Agora", "Talk", "Radar", "Pesquisa", "Ações"];

function Metric({ label, value, hint }: { label: string; value: React.ReactNode; hint?: string }) {
  return (
    <article className="metric-card atlas-surface">
      <span>{label}</span>
      <strong>{value}</strong>
      {hint && <small>{hint}</small>}
    </article>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="screen-header">
      <span className="eyebrow">{eyebrow}</span>
      <h2>{title}</h2>
      {description && <p className="muted">{description}</p>}
    </header>
  );
}

function App() {
  const [active, setActive] = useState<ScreenId>(() => {
    const requested = new URLSearchParams(window.location.search).get("screen") as ScreenId | null;
    return requested && navigation.includes(requested) ? requested : "Agora";
  });
  const [status, setStatus] = useState<Status | null>(null);
  const [connected, setConnected] = useState(false);
  const [ownerCode, setOwnerCode] = useState("");
  const [message, setMessage] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(readChatHistory);
  const [realtimeDraft, setRealtimeDraft] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [liveVoice, setLiveVoice] = useState(false);
  const [voiceState, setVoiceState] = useState<"ready" | "listening" | "thinking" | "speaking" | "degraded">("ready");
  const [worldPrograms, setWorldPrograms] = useState<WorldProgram[]>([]);
  const [worldError, setWorldError] = useState("");
  const [events, setEvents] = useState<AtlasEvent[]>([]);
  const [researchItems, setResearchItems] = useState<ResearchItem[]>([]);
  const [researchCentral, setResearchCentral] = useState<ResearchCentralData | null>(null);
  const [researchTitle, setResearchTitle] = useState("");
  const [researchUrl, setResearchUrl] = useState("");
  const [researchSummary, setResearchSummary] = useState("");
  const [researchSourceType, setResearchSourceType] = useState("scientific_paper");
  const [researchMinistry, setResearchMinistry] = useState("research_evolution");
  const [researchTags, setResearchTags] = useState("");
  const [researchImportJson, setResearchImportJson] = useState("");
  const [dailyPlanBusy, setDailyPlanBusy] = useState(false);
  const [investigationReport, setInvestigationReport] = useState("");
  const [scientificWorks, setScientificWorks] = useState<ScientificWork[]>([]);
  const [deliverySettings, setDeliverySettings] = useState<PublicationDeliverySettings>({ email: "", can_send_email: false });
  const [reviewProviders, setReviewProviders] = useState<ReviewProvider[]>([]);
  const [reviewReports, setReviewReports] = useState<Record<string, ReviewReport[]>>({});
  const [reviewingPublicationId, setReviewingPublicationId] = useState("");
  const [publicationForm, setPublicationForm] = useState<ScientificWorkForm>({
    author_name: "Gabriel Jaccoud",
    ministry_id: "research",
    work_type: "theoretical_physics",
    evidence_level: "internal_hypothesis",
    title_pt: "",
    title_en: "",
    abstract_pt: "",
    abstract_en: "",
    question_pt: "",
    question_en: "",
    assumptions_pt: "",
    assumptions_en: "",
    methodology_pt: "",
    methodology_en: "",
    results_pt: "",
    results_en: "",
    predictions_pt: "",
    predictions_en: "",
    uncertainty_pt: "",
    uncertainty_en: "",
    limitations_pt: "",
    limitations_en: "",
    referencesText: "",
  });
  const [world, setWorld] = useState<WorldData>({ nodes: [], edges: [] });
  const [observations, setObservations] = useState<Array<ApiRecord<WorldObservation>>>([]);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [commandQuery, setCommandQuery] = useState("");
  const [researchQuestion, setResearchQuestion] = useState("");
  const [worldNodeName, setWorldNodeName] = useState("");
  const [missionObjective, setMissionObjective] = useState("");
  const [councilCadence, setCouncilCadence] = useState("daily");
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [postureCaptures, setPostureCaptures] = useState<PostureCapture[]>([]);
  const [postureReport, setPostureReport] = useState("");
  const [postureConsent, setPostureConsent] = useState(false);
  const [postureView, setPostureView] = useState<PostureCapture["view"]>("frontal");
  const cameraVideoRef = useRef<HTMLVideoElement | null>(null);
  const cameraCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const realtimeRef = useRef<RealtimeHandle | null>(null);
  const realtimeTextRef = useRef("");
  const transcriptEndRef = useRef<HTMLDivElement | null>(null);

  function addChatMessage(role: ChatMessage["role"], content: string) {
    if (!content.trim()) return;
    setChatMessages((current) => [...current, {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      role,
      content: content.trim(),
      createdAt: Date.now(),
    }].slice(-120));
  }

  useEffect(() => {
    try {
      localStorage.setItem("atlas.chat.history", JSON.stringify(chatMessages.slice(-120)));
    } catch {
      setReply("Não foi possível salvar o histórico neste navegador.");
    }
  }, [chatMessages]);

  useEffect(() => {
    if (cameraVideoRef.current && cameraStream) cameraVideoRef.current.srcObject = cameraStream;
  }, [cameraStream, active]);

  useEffect(() => () => cameraStream?.getTracks().forEach((track) => track.stop()), [cameraStream]);

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [chatMessages, realtimeDraft, busy, active]);

  async function refresh() {
    if (!loadConfig().token) {
      setConnected(false);
      return;
    }
    try {
      const data = await atlasFetch<Status>("/status");
      setStatus(data);
      setConnected(true);
      const [eventData, researchData, worldData, metricsData, observationData, publicationData, deliveryData, reviewProviderData, researchCentralData] = await Promise.allSettled([
        atlasFetch<AtlasEvent[]>("/events"),
        atlasFetch<Array<{ data: ResearchItem }>>("/records/research"),
        atlasFetch<WorldData>("/world"),
        atlasFetch<Record<string, unknown>>("/metrics"),
        atlasFetch<Array<ApiRecord<WorldObservation>>>("/records/world_observation"),
        atlasFetch<ScientificWork[]>("/publications"),
        atlasFetch<PublicationDeliverySettings>("/publication-delivery-settings"),
        atlasFetch<{ providers: ReviewProvider[] }>("/review/providers"),
        atlasFetch<ResearchCentralData>("/research/central"),
      ]);
      if (eventData.status === "fulfilled") setEvents(eventData.value);
      if (researchData.status === "fulfilled") setResearchItems(researchData.value.map((record) => record.data));
      if (worldData.status === "fulfilled") setWorld(worldData.value);
      if (metricsData.status === "fulfilled") setMetrics(metricsData.value);
      if (observationData.status === "fulfilled") setObservations(observationData.value);
      if (publicationData.status === "fulfilled") setScientificWorks(publicationData.value);
      if (deliveryData.status === "fulfilled") setDeliverySettings(deliveryData.value);
      if (reviewProviderData.status === "fulfilled") setReviewProviders(reviewProviderData.value.providers);
      if (researchCentralData.status === "fulfilled") {
        setResearchCentral(researchCentralData.value);
        setResearchItems(researchCentralData.value.backlog);
      }
    } catch {
      setConnected(false);
    }
  }

  async function loadWorlds() {
    if (!connected) return;
    try {
      const data = await atlasFetch<WorldProgram[]>("/possible-worlds/programs");
      setWorldPrograms(data);
      setWorldError("");
    } catch {
      setWorldPrograms([]);
      setWorldError("O backend público ainda não expõe o Possible Worlds 1.9. A interface está pronta para receber esses dados quando a API 1.9 for publicada.");
    }
  }

  useEffect(() => {
    refresh();
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        void navigator.serviceWorker.register("/sw.js").catch(() => undefined);
      }, { once: true });
    }
    return () => realtimeRef.current?.stop();
  }, []);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommandOpen((value) => !value);
      }
      if (event.key === "Escape") {
        setCommandOpen(false);
        setMenuOpen(false);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  async function runAction<T>(path: string, body: unknown, success: (data: T) => string) {
    if (!connected) {
      setReply("Pareie este dispositivo para usar os módulos operacionais.");
      return;
    }
    setBusy(true);
    try {
      const data = await atlasFetch<T>(path, { method: "POST", body: JSON.stringify(body) });
      setReply(success(data));
      if (path === "/research") setResearchQuestion("");
      if (path === "/world/nodes") setWorldNodeName("");
      if (path === "/missions/route") setMissionObjective("");
      await refresh();
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function ingestResearchFinding() {
    if (!researchTitle.trim() || researchSummary.trim().length < 10) return;
    setBusy(true);
    try {
      await atlasFetch("/research/intake", { method: "POST", body: JSON.stringify({
        producer: "atlas-web-manual-intake",
        findings: [{
          title: researchTitle.trim(), summary: researchSummary.trim(), source_url: researchUrl.trim(),
          source_type: researchSourceType, ministry_id: researchMinistry,
          tags: researchTags.split(",").map((tag) => tag.trim()).filter(Boolean),
          confidence: 0.5, priority: 0.5, evidence_class: "unverified_report",
        }],
      }) });
      setResearchTitle(""); setResearchUrl(""); setResearchSummary(""); setResearchTags("");
      await refresh();
      setReply("Achado recebido na Central de Pesquisa. Ele permanece não verificado até apuração da fonte.");
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível registrar o achado.");
    } finally { setBusy(false); }
  }

  async function importResearchPackage() {
    try {
      const parsed = JSON.parse(researchImportJson) as { findings?: unknown[]; batch_id?: string; producer?: string };
      if (!Array.isArray(parsed.findings) || !parsed.findings.length) throw new Error("O JSON precisa conter uma lista 'findings'.");
      await atlasFetch("/research/intake", { method: "POST", body: JSON.stringify({
        batch_id: parsed.batch_id || `chat-import-${Date.now()}`,
        producer: parsed.producer || "chatgpt-research-import",
        findings: parsed.findings,
      }) });
      setResearchImportJson("");
      await refresh();
      setReply("Pacote de pesquisa importado. Os itens foram deduplicados por fonte e permanecem em triagem.");
    } catch (error) {
      setReply(error instanceof Error ? error.message : "JSON inválido ou pacote incompleto.");
    }
  }

  async function generateDailyResearchPlan() {
    setDailyPlanBusy(true);
    try {
      const plan = await atlasFetch<DailyResearchPlan>("/research/daily-plan?force=true", { method: "POST" });
      setResearchCentral((current) => current ? { ...current, latest_plan: plan } : current);
      setReply(`Plano diário atualizado: ${plan.summary}`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível consolidar a pesquisa do dia.");
    } finally { setDailyPlanBusy(false); }
  }

  async function investigateResearchTopic() {
    if (!researchQuestion.trim()) return;
    setDailyPlanBusy(true);
    setInvestigationReport("");
    try {
      const result = await atlasFetch<{ report: string; intake: { inserted: number }; daily_plan: DailyResearchPlan | null }>("/research/investigate", {
        method: "POST",
        body: JSON.stringify({ question: researchQuestion.trim(), ministry_id: researchMinistry }),
      });
      setInvestigationReport(result.report);
      if (result.daily_plan) setResearchCentral((current) => current ? { ...current, latest_plan: result.daily_plan } : current);
      setReply(`Apuração concluída; ${result.intake.inserted} achado(s) novo(s) recebido(s) na Central.`);
      await refresh();
    } catch (error) {
      setReply(error instanceof Error ? error.message : "A apuração web não foi concluída.");
    } finally { setDailyPlanBusy(false); }
  }

  async function updateResearchGoal(goal: ResearchGoal, status: ResearchGoal["status"]) {
    try {
      await atlasFetch(`/research/goals/${encodeURIComponent(goal.goal_id)}`, { method: "PATCH", body: JSON.stringify({ status, note: "" }) });
      await refresh();
      setReply(`Meta marcada como ${status.replaceAll("_", " ")}.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível atualizar a meta.");
    }
  }

  async function emailDailyResearchPlan() {
    const plan = researchCentral?.latest_plan;
    if (!plan) return;
    try {
      const result = await atlasFetch<{ sent: boolean; to: string; link: string }>(`/research/daily-plan/${encodeURIComponent(plan.plan_id)}/email`, { method: "POST" });
      setReply(`Resumo enviado para ${result.to} com link para a Central de Pesquisa.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível enviar o resumo.");
    }
  }

  function updatePublicationForm<K extends keyof ScientificWorkForm>(key: K, value: ScientificWorkForm[K]) {
    setPublicationForm((current) => ({ ...current, [key]: value }));
  }

  async function saveScientificWork() {
    if (!connected) {
      setReply("Pareie este dispositivo para registrar um trabalho científico.");
      return;
    }
    setBusy(true);
    try {
      const { referencesText, ...content } = publicationForm;
      const record = await atlasFetch<ScientificWork>("/publications", {
        method: "POST",
        body: JSON.stringify({
          ...content,
          references: referencesText.split("\n").map((value) => value.trim()).filter(Boolean),
        }),
      });
      setScientificWorks((current) => [record, ...current]);
      setReply(record.export_ready
        ? "Trabalho registrado e liberado para revisão final e exportação."
        : `Trabalho guardado na trilha interna. Ainda faltam ${record.missing_requirements.length} requisito(s) para exportação.`);
      setPublicationForm((current) => ({ ...current, title_pt: "", title_en: "" }));
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function downloadScientificWork(work: ScientificWork, language: "pt" | "en") {
    if (!work.export_ready) return;
    const config = loadConfig();
    try {
      const response = await fetch(`${config.baseUrl}/publications/${encodeURIComponent(work.publication_id)}/pdf?language=${language}`, {
        headers: config.token ? { Authorization: `Bearer ${config.token}` } : {},
      });
      if (!response.ok) throw new Error("O ATLAS não conseguiu gerar o PDF.");
      const pdf = await response.blob();
      const objectUrl = URL.createObjectURL(pdf);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `ATLAS-${language}-${work.publication_id.replaceAll(":", "-")}.pdf`;
      link.click();
      URL.revokeObjectURL(objectUrl);
      setReply(`PDF ${language.toUpperCase()} baixado pelo ATLAS.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Falha ao baixar o PDF.");
    }
  }

  async function downloadScientificHtml(work: ScientificWork, language: "pt" | "en") {
    if (!work.export_ready) return;
    const config = loadConfig();
    try {
      const response = await fetch(`${config.baseUrl}/publications/${encodeURIComponent(work.publication_id)}/html?language=${language}`, {
        headers: config.token ? { Authorization: `Bearer ${config.token}` } : {},
      });
      if (!response.ok) throw new Error("O ATLAS não conseguiu gerar o HTML.");
      const html = await response.blob();
      const objectUrl = URL.createObjectURL(html);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = `ATLAS-${language}-${work.publication_id.replaceAll(":", "-")}.html`;
      link.click();
      URL.revokeObjectURL(objectUrl);
      setReply(`HTML ${language.toUpperCase()} baixado pelo ATLAS.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Falha ao baixar o HTML.");
    }
  }

  async function emailScientificWork(work: ScientificWork) {
    if (!work.export_ready || !deliverySettings.can_send_email) return;
    setBusy(true);
    try {
      await atlasFetch(`/publications/${encodeURIComponent(work.publication_id)}/email`, { method: "POST" });
      setReply(`E-mail enviado para ${deliverySettings.email} com os PDFs em português e inglês anexados.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "O ATLAS não conseguiu enviar o e-mail.");
    } finally {
      setBusy(false);
    }
  }

  async function runScientificReview(work: ScientificWork) {
    if (!connected || reviewingPublicationId) return;
    if (!reviewProviders.length) {
      setReply("Configure pelo menos um provedor de revisão no Render (OpenAI, Ollama, Kimi ou Qwen).");
      return;
    }
    setReviewingPublicationId(work.publication_id);
    try {
      const report = await atlasFetch<ReviewReport>(`/publications/${encodeURIComponent(work.publication_id)}/review`, { method: "POST" });
      setReviewReports((current) => ({
        ...current,
        [work.publication_id]: [report, ...(current[work.publication_id] || [])],
      }));
      setReply(`Revisão concluída por ${report.reviewers.filter((reviewer) => reviewer.status === "completed").length} agente(s). A decisão final continua humana.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível concluir a revisão por agentes.");
    } finally {
      setReviewingPublicationId("");
    }
  }

  async function loadScientificReviews(work: ScientificWork) {
    try {
      const reports = await atlasFetch<ReviewReport[]>(`/publications/${encodeURIComponent(work.publication_id)}/reviews`);
      setReviewReports((current) => ({ ...current, [work.publication_id]: reports }));
      setReply(`${reports.length} revisão(ões) carregada(s).`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "Não foi possível carregar as revisões anteriores.");
    }
  }

  async function startPostureCamera() {
    if (!navigator.mediaDevices?.getUserMedia) {
      setReply("Este navegador não disponibiliza câmera. Use as opções para anexar fotos.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
      setCameraStream(stream);
      setReply("Câmera ativa neste dispositivo. Enquadre o corpo inteiro e mantenha a câmera na altura do quadril.");
    } catch {
      setReply("O acesso à câmera foi negado ou está indisponível. Você ainda pode anexar imagens já capturadas.");
    }
  }

  function stopPostureCamera() {
    cameraStream?.getTracks().forEach((track) => track.stop());
    setCameraStream(null);
  }

  function capturePostureImage() {
    const video = cameraVideoRef.current;
    const canvas = cameraCanvasRef.current;
    if (!video || !canvas || !video.videoWidth) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    if (!context) return;
    context.drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], `atlas-postura-${postureView}-${Date.now()}.jpg`, { type: "image/jpeg" });
      setPostureCaptures((current) => [...current.filter((capture) => capture.view !== postureView), { file, view: postureView }]);
      setReply(`Vista ${postureView} capturada. Para comparar alinhamento, capture também uma vista lateral.`);
    }, "image/jpeg", 0.88);
  }

  async function assessPosture() {
    if (!connected || !postureConsent || postureCaptures.length < 2) return;
    setBusy(true);
    setPostureReport("");
    const form = new FormData();
    postureCaptures.forEach(({ file, view }) => { form.append("images", file); form.append("views", view); });
    try {
      const result = await atlasFetch<{ report: string; images_retained: boolean; model: string }>("/vision/posture-assessment", { method: "POST", body: form });
      setPostureReport(result.report);
      setReply(`Triagem visual concluída pelo modelo ${result.model}. As imagens não foram armazenadas pelo ATLAS.`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : "A análise visual não foi concluída.");
    } finally {
      setBusy(false);
    }
  }

  function goTo(screen: ScreenId) {
    setActive(screen);
    setMenuOpen(false);
    setCommandOpen(false);
    setCommandQuery("");
  }

  const visibleCommands = navigation.filter((item) => item.toLocaleLowerCase("pt-BR").includes(commandQuery.toLocaleLowerCase("pt-BR")));
  const criticalEvents = events.filter((event) => {
    const priority = String(event.priority).toLowerCase();
    return (Number(priority) >= 30) || priority === "high" || priority === "critical";
  });
  const newestEvent = [...events].sort((a, b) => (b.created_at || "").localeCompare(a.created_at || ""))[0];
  const newestObservation = observations[0];
  const observationProgram = newestObservation && worldPrograms.find((program) => program.program_id === newestObservation.data.program_id);
  const largestWorldShift = observationProgram && newestObservation
    ? observationProgram.worlds
      .map((possibleWorld) => ({
        title: possibleWorld.title,
        delta: (newestObservation.data.posterior.probabilities[possibleWorld.world_id] ?? possibleWorld.prior) - possibleWorld.prior,
      }))
      .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))[0]
    : undefined;
  const recommendedProgram = worldPrograms.find((program) => program.next_experiment);
  const newestCritical = criticalEvents[0];
  const highestPriorityIsCritical = criticalEvents.some((event) => Number(event.priority) >= 40 || String(event.priority).toLowerCase() === "critical");
  const homeSignal: HomeSignal = !connected
    ? { eyebrow: "Aguardando conexão", title: "Conecte o ATLAS para começar.", description: "Depois do pareamento, esta página resume eventos, pesquisas e observações realmente registradas no sistema.", action: "Talk", actionLabel: "Abrir Talk", tone: "calm" }
    : newestCritical
      ? { eyebrow: "Atenção prioritária", title: `${criticalEvents.length} evento${criticalEvents.length === 1 ? "" : "s"} de alta prioridade no Radar.`, description: `${newestCritical.event_type} · origem ${newestCritical.source}. A classificação vem da prioridade registrada pela API.`, action: "Urgente", actionLabel: "Ver eventos", tone: highestPriorityIsCritical ? "critical" : "alert", evidence: newestCritical.created_at ? `Registro: ${new Date(newestCritical.created_at).toLocaleString("pt-BR")}` : newestCritical.event_id }
      : newestObservation && observationProgram && largestWorldShift && Math.abs(largestWorldShift.delta) >= 0.01
        ? { eyebrow: "Possible Worlds · observação registrada", title: `O peso estimado de “${largestWorldShift.title}” mudou.`, description: `A observação “${newestObservation.data.outcome}” no programa ${newestObservation.data.program_id} alterou a estimativa em ${Math.abs(largestWorldShift.delta * 100).toFixed(1)} pontos percentuais. Isso atualiza o modelo; não confirma, por si só, uma explicação.`, action: "Mundos", actionLabel: "Examinar mundos", tone: "research", evidence: `Experimento: ${newestObservation.data.experiment_id}${newestObservation.created_at ? ` · ${new Date(newestObservation.created_at).toLocaleString("pt-BR")}` : ""}` }
        : (status?.research?.blocked ?? 0) > 0
          ? { eyebrow: "Pesquisa · bloqueio registrado", title: `${status?.research?.blocked} item${status?.research?.blocked === 1 ? "" : "s"} de pesquisa bloqueado${status?.research?.blocked === 1 ? "" : "s"}.`, description: "O backlog contém pesquisa marcada como bloqueada. Consulte as perguntas registradas para decidir o próximo passo.", action: "Pesquisa", actionLabel: "Abrir Pesquisa", tone: "alert" }
          : newestEvent
            ? { eyebrow: "Radar · último registro", title: newestEvent.event_type, description: `O registro mais recente veio de ${newestEvent.source}. A prioridade foi classificada como ${newestEvent.priority}.`, action: "Radar", actionLabel: "Abrir Radar", tone: "research", evidence: newestEvent.created_at ? `Atualizado em ${new Date(newestEvent.created_at).toLocaleString("pt-BR")}` : newestEvent.event_id }
            : recommendedProgram
              ? { eyebrow: "Laboratório · próximo experimento", title: recommendedProgram.next_experiment!.experiment_id, description: `O programa ${recommendedProgram.program_id} selecionou este experimento. Ganho de informação esperado: ${recommendedProgram.next_experiment!.expected_information_gain.toFixed(3)} bits.`, action: "Laboratório", actionLabel: "Ver recomendação", tone: "research" }
              : { eyebrow: "Estado operacional", title: "Nenhum alerta prioritário registrado.", description: worldError ? "A API está conectada, mas ainda não forneceu os dados de Possible Worlds 1.9. A Home está usando os registros operacionais disponíveis." : "Os dados carregados não indicam alertas prioritários ou observações recentes. Abra o Radar ou a Pesquisa para explorar os registros.", action: "Radar", actionLabel: "Abrir Radar", tone: "calm" };

  useEffect(() => {
    if (active === "Agora" || active === "Mundos" || active === "Laboratório" || active === "Pesquisa") void loadWorlds();
  }, [active, connected]);

  async function pair() {
    if (!ownerCode.trim()) return;
    setBusy(true);
    try {
      await pairOwner(ownerCode.trim());
      setOwnerCode("");
      await refresh();
      setReply("Este dispositivo foi pareado com o ATLAS.");
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  function speak(text: string) {
    if (!("speechSynthesis" in window) || !text.trim()) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    utterance.rate = 1;
    utterance.onstart = () => setVoiceState("speaking");
    utterance.onend = () => setVoiceState("ready");
    window.speechSynthesis.speak(utterance);
  }

  async function send(textOverride?: string) {
    const outgoing = (textOverride ?? message).trim();
    if (!outgoing || !connected) {
      if (!connected) setReply("Primeiro pareie este dispositivo com o ATLAS.");
      return;
    }
    setBusy(true);
    setVoiceState("thinking");
    setReply("");
    addChatMessage("user", outgoing);
    setMessage("");
    try {
      const shouldResearchWeb = /\b(pesquise|pesquisar|investigue|investigar|apure|averigue|averiguar|busque fontes|procure evidências|notícias recentes)\b/i.test(outgoing);
      if (shouldResearchWeb) {
        const data = await atlasFetch<{ report: string; intake: { inserted: number } }>("/research/investigate", {
          method: "POST",
          body: JSON.stringify({ question: outgoing, ministry_id: "research_evolution" }),
        });
        const responseText = `${data.report}\n\n${data.intake.inserted} novo(s) achado(s) foi/foram guardado(s) na Central de Pesquisa.`;
        addChatMessage("assistant", responseText);
        speak(responseText);
        await refresh();
      } else {
        const data = await atlasFetch<{ text: string }>("/chat", {
          method: "POST",
          body: JSON.stringify({
            message: outgoing,
            context: {
              surface: "atlas-web",
              input: textOverride ? "voice" : "text",
              current_screen: active,
              available_surfaces: ["Talk", "Radar", "Pesquisa", "Ciência", "Conselho", "Apps", "Awareness", "Corpo", "Ações"],
              posture_screen_available: true,
              research_central_available: true,
              visual_model_configured: Boolean(status?.provider?.openai_configured),
            },
            history: chatMessages.filter((item) => item.role === "user" || item.role === "assistant")
              .slice(-20).map(({ role, content }) => ({ role, content })),
          }),
        });
        addChatMessage("assistant", data.text);
        speak(data.text);
      }
    } catch (error) {
      setVoiceState("degraded");
      addChatMessage("error", error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function toggleRealtime() {
    setActive("Talk");
    if (realtimeRef.current) {
      realtimeRef.current.stop();
      realtimeRef.current = null;
      setLiveVoice(false);
      setVoiceState("ready");
      setReply("Conversa Realtime encerrada.");
      return;
    }
    if (!connected) {
      setReply("Primeiro pareie este dispositivo com o ATLAS.");
      return;
    }
    setBusy(true);
    setVoiceState("listening");
    try {
      const handle = await startRealtimeVoice((event) => {
        if (event?.type === "input_audio_buffer.speech_started") {
          setVoiceState("listening");
        }
        if (event?.type === "conversation.item.input_audio_transcription.completed" && event.transcript) {
          addChatMessage("user", event.transcript);
        }
        if (event?.type === "response.created") {
          setVoiceState("thinking");
          realtimeTextRef.current = "";
          setRealtimeDraft("");
        }
        if (event?.type === "response.output_audio_transcript.delta" && event.delta) {
          setVoiceState("speaking");
          realtimeTextRef.current += event.delta;
          setRealtimeDraft(realtimeTextRef.current);
        }
        if (event?.type === "response.done") {
          addChatMessage("assistant", realtimeTextRef.current);
          realtimeTextRef.current = "";
          setRealtimeDraft("");
          setVoiceState("ready");
        }
      });
      realtimeRef.current = handle;
      setLiveVoice(true);
      setReply("Realtime conectado. Pode falar.");
    } catch (error) {
      setVoiceState("degraded");
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function upload(file: File | null) {
    if (!file || !connected) return;
    const form = new FormData();
    form.append("file", file);
    setBusy(true);
    try {
      const data = await atlasFetch<{ filename: string; kind: string }>("/artifacts", {
        method: "POST",
        body: form,
      });
      addChatMessage("assistant", `Arquivo recebido: ${data.filename} · ${data.kind}`);
    } catch (error) {
      addChatMessage("error", error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  function VoiceCore({ compact = false }: { compact?: boolean }) {
    const contextualState = voiceState !== "ready"
      ? voiceState
      : active === "Agora"
        ? homeSignal.tone === "calm" ? "ready" : homeSignal.tone === "research" ? "researching" : homeSignal.tone
        : active === "Pesquisa" || active === "Mundos" || active === "Laboratório" || active === "Ciência"
          ? "researching"
          : "ready";
    const trigger = (
      <button
        className={`atlas-core voice-core ${compact ? "compact" : "core-trigger"}`}
        data-state={contextualState}
        aria-label={liveVoice ? "Encerrar conversa por voz com ATLAS" : "Conversar com ATLAS por voz"}
        aria-pressed={liveVoice}
        onClick={toggleRealtime}
      >
        <span className="core-mark">A</span>
      </button>
    );
    if (compact) return trigger;
    return (
      <div className="atlas-core-stage">
        <Suspense fallback={<div className="atlas-scene-loading" />}>
          <AtlasScene3D state={contextualState} />
        </Suspense>
        {trigger}
        <span className="core-state-label">{liveVoice ? "Realtime ativo" : voiceState === "ready" ? "Atlas Core" : voiceState}</span>
      </div>
    );
  }

  function renderScreen() {
    switch (active) {
      case "Agora":
        return (
          <>
            <SectionHeader
              eyebrow="Web 3D 3.0 · Command Center"
              title="O que merece sua atenção agora."
              description="Situação do sistema, contexto e prioridades em uma única visão."
            />
            <div className={`hero-command atlas-surface home-signal signal-${homeSignal.tone}`}>
              <div className="hero-copy">
                <span className="eyebrow">{homeSignal.eyebrow}</span>
                <h3>{homeSignal.title}</h3>
                <p>{homeSignal.description}</p>
                {homeSignal.evidence && <small className="signal-evidence">{homeSignal.evidence}</small>}
                <button className="secondary signal-action" onClick={() => goTo(homeSignal.action)}>{homeSignal.actionLabel} <span aria-hidden="true">→</span></button>
              </div>
              <VoiceCore />
            </div>
            <div className="metric-grid">
              <Metric label="Modo global" value={status?.mode?.mode || "—"} />
              <Metric label="Ministérios" value={status?.ministries?.length ?? "—"} />
              <Metric label="Pesquisa bloqueada" value={status?.research?.blocked ?? "—"} />
              <Metric label="My World" value={status?.my_world ? `${status.my_world.nodes} nós` : "—"} />
            </div>
          </>
        );
      case "Talk":
        return (
          <>
            <SectionHeader
              eyebrow="Conversation"
              title="Vamos conversar."
              description="Uma conversa contínua com ATLAS, por texto, voz ou arquivos. O histórico fica salvo neste navegador."
            />
            <div className="chat-shell atlas-surface">
              <div className="chat-toolbar">
                <div><span className={`connection-dot ${connected ? "online" : ""}`} /><span>{liveVoice ? "Voz em tempo real" : connected ? "ATLAS conectado" : "Aguardando pareamento"}</span></div>
                <button className="secondary clear-chat" onClick={() => { setChatMessages([]); setRealtimeDraft(""); }} disabled={!chatMessages.length}>Limpar conversa</button>
              </div>
              <div className="chat-transcript" aria-live="polite" aria-relevant="additions text">
                {!chatMessages.length && !realtimeDraft && (
                  <div className="chat-welcome">
                    <VoiceCore />
                    <span className="eyebrow">ATLAS · Talk</span>
                    <h3>Por onde começamos?</h3>
                    <p>Faça uma pergunta, organize uma ideia ou peça uma análise. A conversa mantém o contexto dos últimos turnos.</p>
                  </div>
                )}
                {chatMessages.map((item) => (
                  <article key={item.id} className={`chat-message ${item.role}`}>
                    <span>{item.role === "user" ? "Você" : item.role === "error" ? "Conexão" : "ATLAS"}</span>
                    <p>{item.content}</p>
                    <time dateTime={new Date(item.createdAt).toISOString()}>{new Date(item.createdAt).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</time>
                  </article>
                ))}
                {busy && <div className="chat-thinking"><i /><i /><i /><span>ATLAS está pensando</span></div>}
                {realtimeDraft && <article className="chat-message assistant draft"><span>ATLAS · falando</span><p>{realtimeDraft}</p></article>}
                <div ref={transcriptEndRef} />
              </div>
              <div className="chat-composer">
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      void send();
                    }
                  }}
                  placeholder="Escreva sua mensagem…"
                  rows={2}
                  aria-label="Mensagem para ATLAS"
                />
                <div className="chat-composer-actions">
                  <div className="command-actions">
                    <button className="secondary" onClick={toggleRealtime} disabled={busy || !connected} aria-pressed={liveVoice}>
                      {liveVoice ? "Encerrar voz" : "Conversar por voz"}
                    </button>
                    <label className="secondary upload-action">
                      Anexar arquivo
                      <input type="file" onChange={(e) => upload(e.target.files?.[0] || null)} />
                    </label>
                  </div>
                  <button className="primary send-button" onClick={() => void send()} disabled={busy || !connected || !message.trim()}>Enviar <span aria-hidden="true">↑</span></button>
                </div>
                <small>Enter envia · Shift + Enter quebra a linha</small>
              </div>
            </div>
          </>
        );
      case "Radar":
        return (
          <>
            <SectionHeader eyebrow="Operational Intelligence" title="Radar" description="Sinais, mudanças e vigilância estratégica." />
            <div className="cards-grid">
              <div className="feature-card atlas-surface"><span>Radar Matinal</span><strong>07:00</strong><p>Prioridades e mudanças de cenário.</p></div>
              <div className="feature-card atlas-surface"><span>Vigilância Crítica</span><strong>Contínua</strong><p>Monitoramento de evidências e anomalias.</p></div>
              <div className="feature-card atlas-surface"><span>Fechamento</span><strong>19:00</strong><p>Comparação com o início do dia.</p></div>
            </div>
            <div className="section-row"><h3>Eventos registrados</h3><button className="secondary" onClick={() => void refresh()}>Atualizar</button></div>
            {events.length ? <div className="event-list">{[...events].reverse().map((event) => <article className="event-card atlas-surface" key={event.event_id}><div><span className="eyebrow">{event.source} · prioridade {event.priority}</span><strong>{event.event_type}</strong></div><small>{event.created_at ? new Date(event.created_at).toLocaleString("pt-BR") : event.event_id}</small></article>)}</div> : <div className="empty-state atlas-surface">Ainda não há eventos registrados na API conectada.</div>}
          </>
        );
      case "Urgente":
        return (
          <>
            <SectionHeader eyebrow="Priority" title="Urgente" description="Somente o que exige atenção imediata." />
            {criticalEvents.length ? <div className="event-list">{[...criticalEvents].reverse().map((event) => <article className="event-card critical atlas-surface" key={event.event_id}><div><span className="eyebrow">Prioridade {event.priority} · {event.source}</span><strong>{event.event_type}</strong><p>{JSON.stringify(event.payload)}</p></div><small>{event.created_at ? new Date(event.created_at).toLocaleString("pt-BR") : event.event_id}</small></article>)}</div> : <div className="empty-state atlas-surface"><strong>Nenhum evento de alta prioridade.</strong><p>A lista usa os eventos armazenados pela API. Prioridades normais permanecem no Radar.</p></div>}
          </>
        );
      case "Ciência":
        return (
          <>
            <SectionHeader eyebrow="Epistemic Layer · Publication Gate" title="Da pesquisa ao artigo." description="Qualquer ministério pode encaminhar um resultado. O ATLAS só libera a exportação quando o tipo de trabalho e a força da evidência atendem aos requisitos correspondentes." />
            <div className="publication-principles atlas-surface">
              <div><span className="eyebrow">Teorema</span><strong>Premissas e demonstração</strong><p>Prova formal, completa e verificável.</p></div>
              <div><span className="eyebrow">Teoria física</span><strong>Viabilidade não é confirmação</strong><p>Modelos teóricos ficam identificados como não confirmados até haver evidência experimental.</p></div>
              <div><span className="eyebrow">Resultado empírico</span><strong>Método, dados e incerteza</strong><p>A força da conclusão acompanha os resultados e a possibilidade de reprodução.</p></div>
            </div>
            <div className="publication-form atlas-surface">
              <div className="section-row"><div><span className="eyebrow">Entrada transversal</span><h3>Registrar trabalho científico</h3></div><span className="publication-scope">Todos os ministérios</span></div>
              {!connected && <div className="notice">Pareie o dispositivo para registrar submissões no ATLAS.</div>}
              <div className="publication-fields">
                <label>Ministério de origem<select value={publicationForm.ministry_id} onChange={(event) => updatePublicationForm("ministry_id", event.target.value)}>{(status?.ministries || []).map((ministry) => <option key={ministry.id} value={ministry.id}>{ministry.name}</option>)}<option value="transversal">Transversal / múltiplos ministérios</option>{!status?.ministries?.length && <option value="research">Pesquisa</option>}</select></label>
                <label>Natureza do trabalho<select value={publicationForm.work_type} onChange={(event) => updatePublicationForm("work_type", event.target.value as ScientificWorkForm["work_type"])}><option value="mathematical_result">Resultado matemático / teorema</option><option value="theoretical_physics">Teoria ou modelo físico</option><option value="empirical_result">Resultado empírico / experimental</option></select></label>
                <label>Nível de evidência<select value={publicationForm.evidence_level} onChange={(event) => updatePublicationForm("evidence_level", event.target.value as ScientificWorkForm["evidence_level"])}><option value="internal_hypothesis">Hipótese interna</option><option value="mathematical_proof">Prova matemática concluída</option><option value="physical_viability">Viabilidade física teórica</option><option value="empirical_support">Apoio empírico</option><option value="independent_replication">Reprodução independente</option></select></label>
                <label>Autor responsável<input value={publicationForm.author_name} onChange={(event) => updatePublicationForm("author_name", event.target.value)} /></label>
                <label>Título · português<input value={publicationForm.title_pt} onChange={(event) => updatePublicationForm("title_pt", event.target.value)} placeholder="Título do trabalho" /></label>
                <label>Title · English<input value={publicationForm.title_en} onChange={(event) => updatePublicationForm("title_en", event.target.value)} placeholder="Reviewed English title" /></label>
                <label>Resumo · português<textarea rows={4} value={publicationForm.abstract_pt} onChange={(event) => updatePublicationForm("abstract_pt", event.target.value)} /></label>
                <label>Abstract · English<textarea rows={4} value={publicationForm.abstract_en} onChange={(event) => updatePublicationForm("abstract_en", event.target.value)} /></label>
                <label>Pergunta e origem da pesquisa · português<textarea rows={3} value={publicationForm.question_pt} onChange={(event) => updatePublicationForm("question_pt", event.target.value)} /></label>
                <label>Research question and origin · English<textarea rows={3} value={publicationForm.question_en} onChange={(event) => updatePublicationForm("question_en", event.target.value)} /></label>
                <label>Premissas / modelo · português<textarea rows={3} value={publicationForm.assumptions_pt} onChange={(event) => updatePublicationForm("assumptions_pt", event.target.value)} /></label>
                <label>Assumptions / model · English<textarea rows={3} value={publicationForm.assumptions_en} onChange={(event) => updatePublicationForm("assumptions_en", event.target.value)} /></label>
                <label>Métodos e experimentos · português<textarea rows={4} value={publicationForm.methodology_pt} onChange={(event) => updatePublicationForm("methodology_pt", event.target.value)} /></label>
                <label>Methods and experiments · English<textarea rows={4} value={publicationForm.methodology_en} onChange={(event) => updatePublicationForm("methodology_en", event.target.value)} /></label>
                <label>{publicationForm.work_type === "mathematical_result" ? "Teorema, prova e resultado · português" : "Resultados · português"}<textarea rows={4} value={publicationForm.results_pt} onChange={(event) => updatePublicationForm("results_pt", event.target.value)} /></label>
                <label>{publicationForm.work_type === "mathematical_result" ? "Theorem, proof and result · English" : "Results · English"}<textarea rows={4} value={publicationForm.results_en} onChange={(event) => updatePublicationForm("results_en", event.target.value)} /></label>
                <label>Previsões testáveis · português<textarea rows={3} value={publicationForm.predictions_pt} onChange={(event) => updatePublicationForm("predictions_pt", event.target.value)} /></label>
                <label>Testable predictions · English<textarea rows={3} value={publicationForm.predictions_en} onChange={(event) => updatePublicationForm("predictions_en", event.target.value)} /></label>
                <label>Incertezas · português<textarea rows={3} value={publicationForm.uncertainty_pt} onChange={(event) => updatePublicationForm("uncertainty_pt", event.target.value)} /></label>
                <label>Uncertainty · English<textarea rows={3} value={publicationForm.uncertainty_en} onChange={(event) => updatePublicationForm("uncertainty_en", event.target.value)} /></label>
                <label>Limitações e explicações alternativas · português<textarea rows={3} value={publicationForm.limitations_pt} onChange={(event) => updatePublicationForm("limitations_pt", event.target.value)} /></label>
                <label>Limitations and alternatives · English<textarea rows={3} value={publicationForm.limitations_en} onChange={(event) => updatePublicationForm("limitations_en", event.target.value)} /></label>
                <label className="full-span">Referências verificáveis · uma por linha<textarea rows={4} value={publicationForm.referencesText} onChange={(event) => updatePublicationForm("referencesText", event.target.value)} placeholder="Autor, título, publicação, ano, DOI ou URL" /></label>
              </div>
              <p className="publication-note">O ATLAS guarda hipóteses para pesquisa interna. A exportação só é liberada se a prova, a viabilidade teórica ou a evidência empírica forem compatíveis com o tipo de trabalho. A versão inglesa exige revisão humana.</p>
              <button className="primary" disabled={busy || !connected || publicationForm.title_pt.trim().length < 8} onClick={() => void saveScientificWork()}>Registrar e avaliar evidências</button>
            </div>
            <div className="section-row"><h3>Trabalhos registrados</h3><button className="secondary" onClick={() => void refresh()}>Atualizar</button></div>
            <p className="publication-note">Ao iniciar, o ATLAS envia o texto completo e as referências do trabalho aos provedores configurados para até quatro avaliações, o que pode consumir créditos desses serviços. Os agentes não pesquisam a internet nesta etapa, não alteram o trabalho e não decidem sua aprovação. Provedores disponíveis: {reviewProviders.length ? reviewProviders.map((provider) => provider.id).join(", ") : "nenhum configurado"}.</p>
            {!deliverySettings.can_send_email && <p className="publication-note">Os PDFs podem ser baixados pelo ATLAS. O envio direto com anexos será ativado quando o remetente de e-mail seguro estiver configurado.</p>}
            {scientificWorks.length ? <div className="publication-list">{scientificWorks.map((work) => {
              const reviews = reviewReports[work.publication_id] || [];
              return <article className="publication-entry atlas-surface" key={work.publication_id}>
                <div className="publication-entry-heading">
                  <div><span className="eyebrow">{work.ministry_id} · {work.work_type.replaceAll("_", " ")}</span><h3>{work.title_pt}</h3><p>{work.title_en || "English title pending"}</p></div>
                  <span className={`evidence-badge ${work.export_ready ? "ready" : "internal"}`}>{work.export_ready ? "Apto para revisão e PDF" : "Pesquisa interna"}</span>
                </div>
                <p>{work.claim_classification.replaceAll("_", " ")}{work.review_required ? " · revisão humana pendente" : ""}</p>
                {!work.export_ready && <details><summary>Requisitos pendentes ({work.missing_requirements.length})</summary><ul>{work.missing_requirements.map((item) => <li key={item}>{item.replaceAll("_", " ")}</li>)}</ul></details>}
                <div className="publication-actions">
                  <button className="secondary" disabled={!connected || Boolean(reviewingPublicationId)} onClick={() => void runScientificReview(work)}>{reviewingPublicationId === work.publication_id ? "Agentes revisando…" : "Revisar com agentes"}</button>
                  <button className="secondary" onClick={() => void loadScientificReviews(work)}>Carregar revisões anteriores</button>
                  {work.export_ready && <>
                    <button className="secondary" onClick={() => void downloadScientificWork(work, "pt")}>Baixar PDF · Português</button>
                    <button className="secondary" onClick={() => void downloadScientificWork(work, "en")}>Baixar PDF · English</button>
                    <button className="secondary" onClick={() => void downloadScientificHtml(work, "pt")}>Baixar HTML · Português</button>
                    <button className="secondary" onClick={() => void downloadScientificHtml(work, "en")}>Baixar HTML · English</button>
                    <button className="secondary" disabled={!deliverySettings.can_send_email || busy} onClick={() => void emailScientificWork(work)}>Enviar os dois PDFs por e-mail</button>
                  </>}
                </div>
                {reviews.map((report) => <section className="review-report" key={report.review_id}>
                  <div className="section-row"><strong>Revisão de {new Date(report.generated_at).toLocaleString("pt-BR")}</strong><span className="eyebrow">{report.status === "completed" ? "Completa" : "Parcial"} · decisão humana requerida</span></div>
                  {report.reviewers.map((reviewer) => <details key={`${report.review_id}-${reviewer.role_id}`}><summary>{reviewer.title} · {reviewer.provider}/{reviewer.model} · {reviewer.status === "completed" ? "concluída" : "falhou"}</summary><p className="review-text">{reviewer.review}</p></details>)}
                  <p className="publication-note">Conferência externa de fontes: não realizada. Esta revisão não alterou a classificação nem a liberação de exportação.</p>
                </section>)}
              </article>;
            })}</div> : <div className="empty-state atlas-surface">As submissões dos ministérios aparecerão aqui. Nenhuma hipótese será promovida automaticamente a artigo.</div>}
          </>
        );
      case "Pesquisa":
        return (
          <>
            <SectionHeader eyebrow="Research & Production" title="Central de Pesquisa" description="Achados, hipóteses, apuração e metas do dia em um único fluxo. O ATLAS mantém notícia, hipótese e conclusão em classes separadas." />
            <div className="metric-grid">
              <Metric label="Achados recebidos" value={researchCentral?.findings.length ?? 0} hint="inclui rotina e entrada manual" />
              <Metric label="Hipóteses registradas" value={researchCentral?.hypotheses.length ?? 0} />
              <Metric label="Metas de hoje" value={researchCentral?.latest_plan?.goals.length ?? 0} hint={researchCentral?.latest_plan?.status || "plano ainda não consolidado"} />
              <Metric label="Fila dos ministérios" value={researchItems.length} hint={`${status?.research?.blocked ?? 0} bloqueada(s)`} />
            </div>
            <div className="hero-command atlas-surface">
              <div className="hero-copy"><span className="eyebrow">Daily Research & Production</span><h3>{researchCentral?.latest_plan?.summary || "Ainda não há plano diário consolidado."}</h3><p>Recebe relatórios, relaciona evidências às hipóteses, encaminha questões aos ministérios e sugere entregas concretas. A RIA fica em triagem até haver mecanismo, teste e evidência.</p></div>
              <button className="primary" disabled={!connected || dailyPlanBusy} onClick={() => void generateDailyResearchPlan()}>{dailyPlanBusy ? "Consolidando…" : "Consolidar pesquisa e gerar metas"}</button>
            </div>
            <div className="form-panel atlas-surface">
              <div className="section-row"><div><span className="eyebrow">Research inbox</span><h3>Receber achado ou relatório</h3></div><span className="publication-scope">Não verificado até apuração</span></div>
              <div className="publication-fields">
                <label>Título<input value={researchTitle} onChange={(event) => setResearchTitle(event.target.value)} placeholder="Achado, notícia, artigo ou relatório ministerial" /></label>
                <label>Fonte ou URL<input value={researchUrl} onChange={(event) => setResearchUrl(event.target.value)} placeholder="https://…" /></label>
                <label>Tipo<select value={researchSourceType} onChange={(event) => setResearchSourceType(event.target.value)}><option value="scientific_paper">Artigo científico</option><option value="news">Notícia</option><option value="ministry_report">Relatório de ministério</option><option value="internal_hypothesis">Hipótese interna</option><option value="other">Outro</option></select></label>
                <label>Ministério<select value={researchMinistry} onChange={(event) => setResearchMinistry(event.target.value)}>{(status?.ministries || []).map((ministry) => <option key={ministry.id} value={ministry.id}>{ministry.name}</option>)}<option value="research_evolution">Pesquisa e Evolução</option></select></label>
                <label className="full-span">Resumo do achado<textarea rows={4} value={researchSummary} onChange={(event) => setResearchSummary(event.target.value)} placeholder="O que a fonte afirma? Quais dados ou métodos apresenta?" /></label>
                <label className="full-span">Tags para relacionar com hipóteses e áreas<textarea rows={2} value={researchTags} onChange={(event) => setResearchTags(event.target.value)} placeholder="UAP, metrologia, biomecânica… separado por vírgulas" /></label>
              </div>
              <button className="primary" disabled={!connected || busy || researchTitle.trim().length < 4 || researchSummary.trim().length < 10} onClick={() => void ingestResearchFinding()}>Receber na Central de Pesquisa</button>
            </div>
            <div className="form-panel atlas-surface">
              <div className="section-row"><div><span className="eyebrow">Automated intake bridge</span><h3>Ponte segura das rotinas</h3></div><span className={`evidence-badge ${researchCentral?.automation_bridge.configured ? "ready" : "internal"}`}>{researchCentral?.automation_bridge.configured ? "chave configurada" : "aguardando chave privada"}</span></div>
              <p>Endpoint de ingestão: <code>{loadConfig().baseUrl}{researchCentral?.automation_bridge.endpoint || "/research/automation/intake"}</code></p>
              <p className="publication-note">Autenticação: cabeçalho <code>{researchCentral?.automation_bridge.authentication || "X-Atlas-Automation-Key"}</code>. A chave fica apenas como variável privada do serviço; nunca aparece nesta tela. As tarefas agendadas do ChatGPT ainda não têm ação HTTP de saída, então elas precisam de um conector compatível para enviar os resultados automaticamente.</p>
              <p className="publication-note">Última execução automática: {researchCentral?.latest_run?.completed_at ? `${new Date(String(researchCentral.latest_run.completed_at)).toLocaleString("pt-BR")} · ${researchCentral.latest_run.status} · ${String(researchCentral.latest_run.finding_count ?? 0)} achado(s)` : "nenhuma execução registrada"}. Rota diária: <code>/research/automation/daily-run</code>.</p>
              <label>Importar pacote JSON de uma rotina ou do Chat<textarea rows={5} value={researchImportJson} onChange={(event) => setResearchImportJson(event.target.value)} placeholder={'{"batch_id":"radar-2026-11-20","producer":"atlas-radar","findings":[{"title":"…","summary":"…","source_url":"https://…","source_type":"news","ministry_id":"science_frontiers","tags":["…"],"confidence":0.7,"priority":0.8}]}'} /></label>
              <button className="secondary" disabled={!connected || !researchImportJson.trim() || busy} onClick={() => void importResearchPackage()}>Importar pacote na Central</button>
              <div className="form-row"><button className="secondary" onClick={() => void refresh()}>Atualizar estado da ponte</button><button className="secondary" onClick={() => goTo("Conselho")}>Ver rotinas e provedores</button></div>
            </div>
            <div className="section-row"><h3>Metas e produção de hoje</h3><div className="form-row"><button className="secondary" disabled={!researchCentral?.latest_plan || !researchCentral.publication_email.configured} onClick={() => void emailDailyResearchPlan()}>Enviar link por e-mail</button><button className="secondary" onClick={() => void refresh()}>Atualizar</button></div></div>
            {researchCentral?.latest_plan?.goals.length ? <div className="cards-grid">{researchCentral.latest_plan.goals.map((goal) => <article className="feature-card atlas-surface research-goal" key={goal.goal_id}><span>{goal.ministries.join(" · ")} · {goal.status.replaceAll("_", " ")}</span><strong>{goal.title}</strong><p>{goal.action}</p><small><b>Entrega:</b> {goal.deliverable}</small><small><b>Concluída quando:</b> {goal.done_criteria}</small><div className="form-row"><select value={goal.status} onChange={(event) => void updateResearchGoal(goal, event.target.value as ResearchGoal["status"])}><option value="planned">Planejada</option><option value="in_progress">Em andamento</option><option value="blocked">Bloqueada</option><option value="completed">Concluída</option><option value="deferred">Adiada</option></select><button className="secondary" onClick={() => goTo("Ciência")}>Preparar artigo / relatório</button></div></article>)}</div> : <div className="empty-state atlas-surface">Quando novos achados ou hipóteses entrarem, o ATLAS poderá propor metas. Para não inventar produção, o plano vazio é identificado como tal.</div>}
            {researchCentral?.latest_plan?.ria_candidates?.length ? <><div className="section-row"><h3>RIA e engenharia reversa em triagem</h3><span className="eyebrow">Sem promoção automática de hipótese</span></div><div className="cards-grid">{researchCentral.latest_plan.ria_candidates.map((candidate) => <article className="feature-card atlas-surface" key={candidate.candidate_id}><span>{candidate.stage} · {candidate.status}</span><strong>{candidate.title}</strong><p>Sequência: {candidate.steps.join(" → ")}</p></article>)}</div></> : null}
            <div className="section-row"><h3>Achados recebidos</h3><span className="eyebrow">Registros recentes da API</span></div>
            {researchCentral?.findings.length ? <div className="event-list">{researchCentral.findings.map((finding) => <article className="event-card atlas-surface" key={finding.finding_id}><div><span className="eyebrow">{finding.source_type.replaceAll("_", " ")} · {finding.ministry_id} · {finding.triage_status}</span><strong>{finding.title}</strong><p>{finding.summary}</p>{finding.source_url && <a href={finding.source_url} target="_blank" rel="noreferrer">Abrir fonte ↗</a>}</div><small>{finding.ingested_at ? new Date(finding.ingested_at).toLocaleString("pt-BR") : ""}</small></article>)}</div> : <div className="empty-state atlas-surface">Nenhum achado recebido pela API ainda.</div>}
            <div className="section-row"><h3>Backlog dos ministérios</h3><button className="secondary" onClick={() => void runAction<ResearchItem>("/research", { ministry_id: status?.ministries?.[0]?.id || "research_evolution", question: researchQuestion.trim(), priority: 0.5 }, (item) => `Pergunta registrada: ${item.question}`)} disabled={!researchQuestion.trim() || busy}>Registrar pergunta</button></div>
            <div className="form-row"><input value={researchQuestion} onChange={(event) => setResearchQuestion(event.target.value)} placeholder="Nova pergunta ou hipótese para o backlog" /></div>
            <button className="secondary" disabled={!connected || !researchQuestion.trim() || dailyPlanBusy || !status?.provider?.openai_configured} onClick={() => void investigateResearchTopic()}>{dailyPlanBusy ? "Pesquisando…" : "Investigar agora na web"}</button>
            {!status?.provider?.openai_configured && <p className="publication-note">A pesquisa web do ATLAS precisa de uma chave OpenAI API configurada no serviço. A rotina agendada do ChatGPT pode ser importada acima enquanto esse provedor não estiver conectado.</p>}
            {investigationReport && <article className="review-report atlas-surface"><span className="eyebrow">Apuração Web · ATLAS</span><div className="posture-report">{investigationReport.split("\n").map((line, index) => <p key={index}>{line}</p>)}</div></article>}
            {researchItems.length > 0 && <div className="event-list">{researchItems.map((item) => <article className="event-card atlas-surface" key={item.item_id}><div><span className="eyebrow">{item.ministry_id} · {item.status}</span><strong>{item.question}</strong></div><small>Prioridade {item.priority.toFixed(1)}</small></article>)}</div>}
          </>
        );
      case "Mundos":
        return (
          <>
            <SectionHeader eyebrow="Possible Worlds" title="Mundos" description="Modelos concorrentes, probabilidades e o que pode distingui-los." />
            {worldError && <div className="notice atlas-surface">{worldError}</div>}
            {worldPrograms.length > 0 && <div className="worlds-3d-panel atlas-surface"><div className="worlds-3d-copy"><span className="eyebrow">Possible Worlds · spatial view</span><h3>Modelos em relação.</h3><p>Uma leitura espacial dos modelos do programa selecionado. As probabilidades seguem discriminadas nos cartões abaixo.</p></div><Suspense fallback={<div className="atlas-scene-loading" />}><AtlasScene3D mode="worlds" state="researching" nodes={worldPrograms[0].worlds.map((possibleWorld) => ({ id: possibleWorld.world_id, label: possibleWorld.title, weight: possibleWorld.prior, tone: possibleWorld.epistemic_label.toLowerCase().includes("unknown") ? "cyan" : possibleWorld.epistemic_label.toLowerCase().includes("conventional") ? "blue" : "gold" }))} /></Suspense></div>}
            <div className="world-list">
              {worldPrograms.map((program) => (
                <div className="world-program atlas-surface" key={program.program_id}>
                  <span className="eyebrow">{program.program_id}</span>
                  <div className="probability-bars">
                    {program.worlds.map((world) => (
                      <div key={world.world_id}>
                        <div className="probability-label"><span>{world.title}</span><strong>{Math.round(world.prior * 100)}%</strong></div>
                        <div className="probability-track"><i style={{ width: `${world.prior * 100}%` }} /></div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
              {!worldPrograms.length && !worldError && <div className="empty-state atlas-surface">{connected ? "Carregando mundos possíveis…" : "Pareie o dispositivo para carregar os mundos possíveis."}</div>}
            </div>
          </>
        );
      case "Laboratório":
        return (
          <>
            <SectionHeader eyebrow="Experimental Intelligence" title="Laboratório" description="Do mundo possível ao experimento mínimo." />
            {worldError && <div className="notice atlas-surface">{worldError}</div>}
            <div className="cards-grid">
              {worldPrograms.map((program) => (
                <div className="feature-card atlas-surface" key={program.program_id}>
                  <span>{program.program_id}</span>
                  <strong>{program.next_experiment?.experiment_id || "Sem experimento selecionado"}</strong>
                  <p>
                    {program.next_experiment
                      ? `Ganho de informação: ${program.next_experiment.expected_information_gain.toFixed(3)}`
                      : "Aguardando backend/experimentos."}
                  </p>
                </div>
              ))}
            </div>
          </>
        );
      case "Ministérios":
        return (
          <>
            <SectionHeader eyebrow="Collective Intelligence" title="Ministérios" description="Unidades especializadas coordenadas por governança." />
            <div className="cards-grid">
              {(status?.ministries || []).map((ministry) => (
                <div className="feature-card atlas-surface" key={ministry.id}><span>{ministry.id}</span><strong>{ministry.name}</strong><p>Ver pesquisas, decisões e interfaces.</p></div>
              ))}
            </div>
          </>
        );
      case "Conselho":
        return (
          <>
            <SectionHeader eyebrow="Governance" title="Conselho" description="Deliberações, divergências, evidências e decisão." />
            <div className="form-panel atlas-surface"><h3>Preparar uma sessão de conselho</h3><p>O ATLAS registra a pauta e a cadência; nenhuma decisão externa é executada automaticamente.</p><div className="form-row"><select value={councilCadence} onChange={(event) => setCouncilCadence(event.target.value)}><option value="daily">Diária</option><option value="weekly">Semanal</option><option value="periodic">Periódica</option><option value="crisis">Crise</option></select><button className="primary" disabled={busy} onClick={async () => { if (!connected) return setReply("Pareie este dispositivo para usar os módulos operacionais."); setBusy(true); try { const data = await atlasFetch<Record<string, unknown>>(`/councils/${councilCadence}`); setReply(`Sessão preparada: ${String(data.session_id || data.sessionId || "conselho")}`); } catch (error) { setReply(error instanceof Error ? error.message : String(error)); } finally { setBusy(false); } }}>Preparar sessão</button></div></div>
            <div className="cards-grid"><div className="feature-card atlas-surface"><span>Epistemic Council</span><strong>Qualidade das evidências</strong><p>Examine alegações, fontes, incertezas e contradições.</p></div><div className="feature-card atlas-surface"><span>Red Team</span><strong>Busca de falhas</strong><p>Procure explicações alternativas e contraevidências.</p></div><div className="feature-card atlas-surface"><span>Outcomes Observatory</span><strong>Acompanhamento</strong><p>Compare decisões com os resultados observados.</p></div></div>
            <SectionHeader eyebrow="Model Council" title="Conselho de inteligências" description="Pareceres independentes, identificados por modelo e sem decisão por maioria." />
            <div className="cards-grid">
              {reviewProviders.length ? reviewProviders.map((provider) => <div className="feature-card atlas-surface" key={provider.id + "-" + provider.model}><span>PROVEDOR CONFIGURADO</span><strong>{provider.id === "claude" ? "Claude · Anthropic API" : provider.id}</strong><p>Modelo: {provider.model}. Pode receber uma função de revisão na análise científica.</p></div>) : <div className="feature-card atlas-surface"><span>AGUARDANDO CONFIGURAÇÃO</span><strong>Nenhum provedor conectado</strong><p>Adicione as credenciais de API no ambiente seguro do Render para habilitar os pareceres.</p></div>}
              <div className="feature-card atlas-surface"><span>AGENTE DE CÓDIGO · PRÓXIMA FASE</span><strong>Claude Code</strong><p>Agente de desenvolvimento com acesso restrito a um workspace isolado e mudanças revisáveis.</p></div>
            </div>
            <SectionHeader eyebrow="Creative Studio" title="Ateliê de criação" description="Conectores para música, vídeo e mundos interativos, com autorização por ferramenta." />
            <div className="cards-grid"><div className="feature-card atlas-surface"><span>MÚSICA · CONECTOR PLANEJADO</span><strong>Suno</strong><p>Ideação, composição e geração musical via conector oficial, após autorização da conta.</p></div><div className="feature-card atlas-surface"><span>VÍDEO · CONECTORES PLANEJADOS</span><strong>Imagem em movimento</strong><p>Roteiro, storyboard e geração audiovisual com ferramentas escolhidas e conectadas pelo usuário.</p></div><div className="feature-card atlas-surface"><span>3D · CONECTORES PLANEJADOS</span><strong>Mundos interativos</strong><p>Conceito, personagens, ambientes e protótipos 3D ligados ao fluxo Web 3D do ATLAS.</p></div></div>
            <p className="publication-note">Conectar uma ferramenta não significa que ela já esteja autorizada. O ATLAS pedirá a conexão por serviço e mostrará quais dados, créditos ou arquivos serão usados.</p>
          </>
        );
      case "Apps": {
        const linked = new Set(reviewProviders.map((provider) => provider.id));
        const appConnections = [
          { id: "openai", name: "OpenAI", kind: "Modelos e análise visual", need: "Chave de API configurada no serviço seguro do ATLAS." },
          { id: "claude", name: "Claude / Anthropic", kind: "Conselho de revisão", need: "Chave de API Anthropic configurada no serviço seguro." },
          { id: "kimi", name: "Kimi", kind: "Conselho de revisão", need: "Chave de API e modelo configurados." },
          { id: "qwen", name: "Qwen", kind: "Conselho de revisão", need: "Chave, endpoint e modelo configurados." },
          { id: "ollama", name: "Ollama", kind: "Modelo local", need: "URL de um servidor Ollama acessível pelo ATLAS." },
          { id: "suno", name: "Suno", kind: "Criação musical", need: "Conector oficial e autorização da conta; não conectado no ATLAS." },
          { id: "runway", name: "Runway / vídeo", kind: "Imagem em movimento", need: "Conector e autorização da conta; não conectado no ATLAS." },
          { id: "worlds", name: "ATLAS Web 3D", kind: "Mundos e visualização", need: "Motor 3D interno; disponível nas áreas Mundos e My World." },
        ];
        return (
          <>
            <SectionHeader eyebrow="Apps & Connections" title="Aplicativos e conexões" description="Um painel para saber o que o ATLAS consegue usar agora e o que ainda precisa de autorização ou credenciais." />
            <div className="notice">As conexões de IA do ATLAS usam credenciais mantidas no servidor. Um login OAuth dentro do ATLAS só ficará ativo quando o serviço oferecer um fluxo autorizado e o conector estiver implementado; nenhum cartão abaixo finge que a conta já foi vinculada.</div>
            <div className="cards-grid">
              {appConnections.map((app) => {
                const is3d = app.id === "worlds";
                const isConnected = is3d || linked.has(app.id);
                return <article className="feature-card atlas-surface" key={app.id}>
                  <span>{isConnected ? "DISPONÍVEL" : "PRECISA CONECTAR"} · {app.kind}</span>
                  <strong>{app.name}</strong>
                  <p>{isConnected ? (is3d ? app.need : `Modelo ativo: ${reviewProviders.find((provider) => provider.id === app.id)?.model || "configurado"}.`) : app.need}</p>
                  <button className="secondary" onClick={() => goTo(app.id === "suno" || app.id === "runway" ? "Conselho" : "Awareness")}>{isConnected ? "Ver estado" : "Ver configuração"} <span aria-hidden="true">→</span></button>
                </article>;
              })}
            </div>
            <p className="publication-note">Próximo passo para habilitar um provedor: configurar as credenciais como variáveis privadas do serviço API e atualizar o estado em Awareness. Não cole senhas ou chaves neste chat ou em páginas públicas.</p>
          </>
        );
      }
      case "Corpo":
        return (
          <>
            <SectionHeader eyebrow="Visual screening" title="Avaliação visual de postura" description="Capture vistas padronizadas e receba observações visuais práticas, com limites e próximos passos explícitos." />
            <div className="publication-principles atlas-surface">
              <div><span className="eyebrow">Preparação</span><strong>Corpo inteiro, câmera estável</strong><p>Use roupa que permita ver o alinhamento, fundo simples e boa iluminação. Afaste a câmera e mantenha-a aproximadamente na altura do quadril.</p></div>
              <div><span className="eyebrow">Vistas</span><strong>Frontal + lateral</strong><p>Fique em postura confortável e natural. Evite poses forçadas; uma vista posterior é opcional.</p></div>
              <div><span className="eyebrow">Resultado</span><strong>Triagem observacional</strong><p>O ATLAS descreve sinais visíveis e incerteza. Foto não confirma escoliose, lesão, causa de dor, temperatura corporal nem substitui exame clínico.</p></div>
            </div>
            {!metrics?.openai_configured && <div className="notice">A análise visual depende de um modelo multimodal configurado no ATLAS. Quando indisponível, a captura continua local e o ATLAS informa o bloqueio sem inventar achados.</div>}
            {!connected && <div className="notice">Pareie este dispositivo para usar a análise visual.</div>}
            <div className="form-panel atlas-surface posture-panel">
              <div className="section-row"><h3>Capturar ou anexar fotos</h3><span className="publication-scope">As imagens não ficam salvas pelo ATLAS</span></div>
              <div className="form-row"><label>Vista<select value={postureView} onChange={(event) => setPostureView(event.target.value as PostureCapture["view"])}><option value="frontal">Frontal</option><option value="lateral">Lateral</option><option value="posterior">Posterior</option></select></label><button className="secondary" onClick={() => cameraStream ? stopPostureCamera() : void startPostureCamera()}>{cameraStream ? "Desligar câmera" : "Abrir câmera"}</button><button className="primary" disabled={!cameraStream} onClick={capturePostureImage}>Capturar vista selecionada</button></div>
              {cameraStream && <video ref={cameraVideoRef} autoPlay playsInline muted className="posture-camera-preview" aria-label="Prévia local da câmera" />}
              <canvas ref={cameraCanvasRef} hidden />
              <div className="form-row"><label>Anexar uma imagem<select value={postureView} onChange={(event) => setPostureView(event.target.value as PostureCapture["view"])}><option value="frontal">Frontal</option><option value="lateral">Lateral</option><option value="posterior">Posterior</option></select></label><label className="secondary upload-action">Escolher imagem<input type="file" accept="image/jpeg,image/png,image/webp" capture="environment" onChange={(event) => { const file = event.target.files?.[0]; if (file) setPostureCaptures((current) => [...current.filter((capture) => capture.view !== postureView), { file, view: postureView }]); event.currentTarget.value = ""; }} /></label></div>
              <p className="publication-note">Vistas incluídas: {postureCaptures.map(({ view }) => view).join(" · ") || "nenhuma"}. Capture pelo menos uma vista frontal e uma lateral. A análise envia as imagens ao modelo visual configurado para gerar o relatório e não as armazena no ATLAS.</p>
              <label className="consent-line"><input type="checkbox" checked={postureConsent} onChange={(event) => setPostureConsent(event.target.checked)} /> Entendo que as imagens serão processadas pelo provedor de IA configurado para produzir esta triagem visual.</label>
              <button className="primary" disabled={!connected || !postureConsent || postureCaptures.length < 2 || busy} onClick={() => void assessPosture()}>{busy ? "Analisando…" : "Analisar postura"}</button>
            </div>
            {postureReport && <article className="review-report atlas-surface"><span className="eyebrow">Triagem visual · não diagnóstica</span><div className="posture-report">{postureReport.split("\n").map((line, index) => <p key={index}>{line}</p>)}</div><button className="secondary" onClick={() => setPostureReport("")}>Fechar relatório</button></article>}
          </>
        );
      case "Awareness":
        return (
          <>
            <SectionHeader eyebrow="Self Model" title="Awareness" description="Saúde operacional, drift, falhas, reflexos e regeneração." />
            <div className="metric-grid">
              <Metric label="Conexão" value={connected ? "ONLINE" : "OFFLINE"} />
              <Metric label="OpenAI" value={metrics?.openai_configured ? "Configurada" : "—"} />
              <Metric label="Modo" value={status?.mode?.mode || "—"} />
              <Metric label="Estado" value={voiceState} />
            </div>
            <div className="section-row"><h3>Resumo do funcionamento interno</h3><span className="eyebrow">Baseado em registros reais da API</span></div>
            <div className="cards-grid">
              <div className="feature-card atlas-surface"><span>RADAR</span><strong>{events.length} evento(s) carregado(s)</strong><p>{events[0] ? `Registro mais recente: ${events[0].event_type} · ${events[0].source}` : "Nenhum evento retornado pela API."}</p></div>
              <div className="feature-card atlas-surface"><span>PESQUISA</span><strong>{researchItems.length} item(ns) registrado(s)</strong><p>{status?.research?.blocked ?? 0} marcado(s) como bloqueado(s) pelo sistema.</p></div>
              <div className="feature-card atlas-surface"><span>CIÊNCIA</span><strong>{scientificWorks.length} trabalho(s)</strong><p>{scientificWorks.filter((work) => work.export_ready).length} liberado(s) para exportação conforme os requisitos atuais.</p></div>
              <div className="feature-card atlas-surface"><span>MODELOS</span><strong>{reviewProviders.length} provedor(es) de revisão</strong><p>{reviewProviders.length ? reviewProviders.map((provider) => provider.id).join(" · ") : "Nenhum modelo de revisão está configurado."}</p></div>
            </div>
            <div className="section-row"><h3>Métricas da API</h3><button className="secondary" onClick={() => void refresh()}>Atualizar</button></div>
            <pre className="data-panel atlas-surface">{metrics ? JSON.stringify(metrics, null, 2) : "As métricas aparecerão após o pareamento."}</pre>
          </>
        );
      case "My World":
        return (
          <>
            <SectionHeader eyebrow="Personal Intelligence" title="My World" description="Projetos, pessoas, organizações, ativos e relações." />
            <div className="hero-command atlas-surface">
              <div className="hero-copy"><span className="eyebrow">Knowledge Graph</span><h3>{world.nodes.length} nós · {world.edges.length} relações</h3><p>Cadastre elementos do seu mundo e acompanhe os vínculos salvos na API.</p></div>
              <Suspense fallback={<div className="atlas-scene-loading" />}><AtlasScene3D mode="network" state="researching" nodes={world.nodes.map((node) => ({ id: node.node_id, label: node.name, tone: node.kind === "person" ? "gold" : node.kind === "organization" ? "blue" : "cyan" }))} edges={world.edges.map((edge) => ({ source: edge.source, target: edge.target, weight: edge.weight }))} className="my-world-scene" /></Suspense>
            </div>
            <div className="form-panel atlas-surface"><h3>Adicionar ao My World</h3><div className="form-row"><input value={worldNodeName} onChange={(event) => setWorldNodeName(event.target.value)} placeholder="Nome de projeto, pessoa, organização ou ativo" /><button className="primary" disabled={busy || !worldNodeName.trim()} onClick={() => void runAction<{ name: string }>("/world/nodes", { kind: "project", name: worldNodeName.trim(), attributes: {} }, (node) => `Adicionado ao My World: ${node.name}`)}>Adicionar nó</button></div></div>
            {world.nodes.length > 0 && <div className="cards-grid">{world.nodes.map((node) => <article className="feature-card atlas-surface" key={node.node_id}><span>{node.kind}</span><strong>{node.name}</strong><small>{node.node_id}</small></article>)}</div>}
          </>
        );
      case "Inovação":
        return (
          <>
            <SectionHeader eyebrow="Hypothesis Forge" title="Inovação" description="Hipóteses transformadas em mecanismos e tecnologias candidatas." />
            <div className="pipeline atlas-surface">
              {["Fonte", "Hipótese", "Mundo", "Mecanismo", "Tecnologia", "RIA", "Sandbox", "Benchmark"].map((step) => <span key={step}>{step}</span>)}
            </div>
            <div className="form-panel atlas-surface"><h3>Iniciar uma hipótese</h3><p>Registra a hipótese como pesquisa para posterior formulação e teste discriminante.</p><div className="form-row"><input value={researchQuestion} onChange={(event) => setResearchQuestion(event.target.value)} placeholder="Descreva a hipótese que deseja explorar" /><button className="primary" disabled={busy || !researchQuestion.trim()} onClick={() => void runAction<ResearchItem>("/research", { ministry_id: "innovation", question: researchQuestion.trim(), priority: 0.7 }, (item) => `Hipótese encaminhada ao backlog: ${item.question}`)}>Enviar ao Forge</button></div></div>
          </>
        );
      case "Ações":
        return (
          <>
            <SectionHeader eyebrow="Execution" title="Ações" description="O que o ATLAS recomenda, o que exige aprovação e o que foi executado." />
            <div className="form-panel atlas-surface"><h3>Solicitar um plano de ação</h3><p>O ATLAS roteia o objetivo para os ministérios competentes. Este formulário não executa ações externas.</p><textarea rows={3} value={missionObjective} onChange={(event) => setMissionObjective(event.target.value)} placeholder="Descreva o objetivo" /><div className="form-row action-form"><label><input id="external-action" type="checkbox" /> Pode afetar sistemas ou pessoas externas</label><button className="primary" disabled={busy || !missionObjective.trim()} onClick={() => void runAction<Record<string, unknown>>("/missions/route", { objective: missionObjective.trim(), required_skills: ["research", "analysis"], external_action: (document.getElementById("external-action") as HTMLInputElement | null)?.checked || false }, (route) => `Plano roteado. Ministérios: ${Array.isArray(route.primary_ministries) ? route.primary_ministries.join(", ") : "em avaliação"}.`)}>Gerar plano</button></div></div>
            <div className="empty-state atlas-surface"><strong>Execução externa exige uma etapa própria de aprovação.</strong><p>Esta tela registra e encaminha planos. Não há execução automática de ações externas.</p></div>
          </>
        );
    }
  }

  return (
    <div className="atlas-app">
      <aside className="sidebar atlas-surface">
        <div className="brand">
          <div className="brand-symbol">A</div>
          <div><strong>ATLAS</strong><span>2.0</span></div>
        </div>
        <nav className="side-nav">
          {navigation.map((item) => (
            <button key={item} title={item} aria-label={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}><span className="nav-label">{item}</span><span className="nav-mark">{{ Agora: "AG", Talk: "TK", Radar: "RD", Urgente: "!", Ciência: "CI", Pesquisa: "PQ", Mundos: "MU", Laboratório: "LB", Ministérios: "MI", Conselho: "CO", Apps: "AP", Awareness: "AW", Corpo: "CV", "My World": "MW", Inovação: "IN", Ações: "AC" }[item]}</span></button>
          ))}
        </nav>
        <div className={connected ? "system-pill online" : "system-pill"}>{connected ? "ONLINE" : "NÃO PAREADO"}</div>
      </aside>

      <main className="workspace">
        <header className="command-bar">
          <div>
            <span className="eyebrow">Private Intelligence System</span>
            <strong>{active}</strong>
          </div>
          <div className="command-tools"><button className="secondary command-shortcut" onClick={() => setCommandOpen(true)} aria-label="Abrir busca de módulos">Buscar <kbd>⌘ / Ctrl K</kbd></button><button className="secondary refresh-button" onClick={() => void refresh()} aria-label="Atualizar dados">Atualizar</button><VoiceCore compact /></div>
        </header>

        {reply && active !== "Talk" && <div className="global-feedback" role="status" aria-live="polite">{reply}</div>}

        {!connected && (
          <section className="pairing atlas-surface">
            <div><span className="eyebrow">Pareamento</span><strong>Conecte este dispositivo ao ATLAS.</strong></div>
            <div className="pair-row">
              <input value={ownerCode} onChange={(e) => setOwnerCode(e.target.value)} placeholder="Código do proprietário" inputMode="numeric" />
              <button className="primary" onClick={pair} disabled={busy}>Parear</button>
            </div>
          </section>
        )}

        <section className="screen">{renderScreen()}</section>
      </main>

      {menuOpen && <><button className="menu-backdrop" aria-label="Fechar menu" onClick={() => setMenuOpen(false)} /><aside className="module-drawer atlas-surface" aria-label="Todos os módulos"><div className="drawer-heading"><div><span className="eyebrow">ATLAS 2.0</span><h2>Módulos</h2></div><button className="secondary" onClick={() => setMenuOpen(false)}>Fechar</button></div><nav>{navigation.map((item) => <button key={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}>{item}<span>›</span></button>)}</nav></aside></>}

      {commandOpen && <div className="command-overlay" role="dialog" aria-modal="true" aria-label="Buscar módulo" onMouseDown={(event) => { if (event.target === event.currentTarget) setCommandOpen(false); }}><div className="command-dialog atlas-surface"><input autoFocus value={commandQuery} onChange={(event) => setCommandQuery(event.target.value)} placeholder="Buscar um módulo do ATLAS…" onKeyDown={(event) => { if (event.key === "Enter" && visibleCommands[0]) goTo(visibleCommands[0]); }} /><div className="command-results">{visibleCommands.map((item) => <button key={item} onClick={() => goTo(item)}>{item}<span>↵</span></button>)}{visibleCommands.length === 0 && <p>Nenhum módulo corresponde à busca.</p>}</div><small>Pressione Esc para fechar · Enter para abrir</small></div></div>}

      <nav className="mobile-nav atlas-surface" aria-label="Navegação principal">
        {primaryMobile.map((item) => <button key={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}>{item}</button>)}
        <button aria-expanded={menuOpen} onClick={() => setMenuOpen((value) => !value)}>Mais</button>
      </nav>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
