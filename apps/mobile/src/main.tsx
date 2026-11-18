import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { atlasFetch, loadConfig, pairOwner } from "./api";
import { RealtimeHandle, startRealtimeVoice } from "./realtime";
import "./design-system.css";
import "./styles.css";

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

type WorldData = {
  nodes: Array<{ node_id: string; kind: string; name: string; attributes?: Record<string, unknown> }>;
  edges: Array<{ edge_id: string; source: string; relation: string; target: string; weight: number }>;
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
  | "Awareness"
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
  "Awareness",
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
  const [active, setActive] = useState<ScreenId>("Agora");
  const [status, setStatus] = useState<Status | null>(null);
  const [connected, setConnected] = useState(false);
  const [ownerCode, setOwnerCode] = useState("");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [liveVoice, setLiveVoice] = useState(false);
  const [voiceState, setVoiceState] = useState<"ready" | "listening" | "thinking" | "speaking" | "degraded">("ready");
  const [worldPrograms, setWorldPrograms] = useState<WorldProgram[]>([]);
  const [worldError, setWorldError] = useState("");
  const [events, setEvents] = useState<AtlasEvent[]>([]);
  const [researchItems, setResearchItems] = useState<ResearchItem[]>([]);
  const [world, setWorld] = useState<WorldData>({ nodes: [], edges: [] });
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [commandOpen, setCommandOpen] = useState(false);
  const [commandQuery, setCommandQuery] = useState("");
  const [researchQuestion, setResearchQuestion] = useState("");
  const [worldNodeName, setWorldNodeName] = useState("");
  const [missionObjective, setMissionObjective] = useState("");
  const [councilCadence, setCouncilCadence] = useState("daily");
  const realtimeRef = useRef<RealtimeHandle | null>(null);

  async function refresh() {
    if (!loadConfig().token) {
      setConnected(false);
      return;
    }
    try {
      const data = await atlasFetch<Status>("/status");
      setStatus(data);
      setConnected(true);
      const [eventData, researchData, worldData, metricsData] = await Promise.allSettled([
        atlasFetch<AtlasEvent[]>("/events"),
        atlasFetch<Array<{ data: ResearchItem }>>("/records/research"),
        atlasFetch<WorldData>("/world"),
        atlasFetch<Record<string, unknown>>("/metrics"),
      ]);
      if (eventData.status === "fulfilled") setEvents(eventData.value);
      if (researchData.status === "fulfilled") setResearchItems(researchData.value.map((record) => record.data));
      if (worldData.status === "fulfilled") setWorld(worldData.value);
      if (metricsData.status === "fulfilled") setMetrics(metricsData.value);
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

  useEffect(() => {
    if (active === "Mundos" || active === "Laboratório" || active === "Pesquisa") void loadWorlds();
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
    try {
      const data = await atlasFetch<{ text: string }>("/chat", {
        method: "POST",
        body: JSON.stringify({
          message: outgoing,
          context: { surface: "atlas-web", input: textOverride ? "voice" : "text" },
        }),
      });
      setReply(data.text);
      setMessage("");
      speak(data.text);
    } catch (error) {
      setVoiceState("degraded");
      setReply(error instanceof Error ? error.message : String(error));
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
        if (event?.type === "response.created") {
          setVoiceState("thinking");
        }
        if (event?.type === "response.output_audio_transcript.delta" && event.delta) {
          setVoiceState("speaking");
          setReply((current) => current + event.delta);
        }
        if (event?.type === "response.done") {
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
      setReply(`Arquivo recebido: ${data.filename} · ${data.kind}`);
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  function VoiceCore({ compact = false }: { compact?: boolean }) {
    return (
      <button
        className={`atlas-core voice-core ${compact ? "compact" : ""}`}
        data-state={voiceState}
        aria-label={liveVoice ? "Encerrar conversa por voz com ATLAS" : "Conversar com ATLAS por voz"}
        aria-pressed={liveVoice}
        onClick={toggleRealtime}
      >
        <span className="core-mark">A</span>
      </button>
    );
  }

  function renderScreen() {
    switch (active) {
      case "Agora":
        return (
          <>
            <SectionHeader
              eyebrow="Command Center"
              title="O que merece sua atenção agora."
              description="Situação do sistema, contexto e prioridades em uma única visão."
            />
            <div className="hero-command atlas-surface">
              <div className="hero-copy">
                <span className="eyebrow">ATLAS 1.9</span>
                <h3>{connected ? "Sistema conectado." : "Aguardando pareamento."}</h3>
                <p>
                  {connected
                    ? "A arquitetura está pronta para pesquisa, mundos possíveis, ministérios e execução."
                    : "Pareie este dispositivo para ativar os dados operacionais."}
                </p>
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
              title="Fale comigo."
              description="Texto, arquivos e voz em uma única superfície."
            />
            <div className="talk-stage atlas-surface">
              <VoiceCore />
              <div className="voice-state">{liveVoice ? "Realtime ativo" : voiceState}</div>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    void send();
                  }
                }}
                placeholder="Escreva uma mensagem ou ative o núcleo de voz…"
                rows={4}
              />
              <div className="command-actions">
                <button className="primary" onClick={() => send()} disabled={busy || !connected}>Enviar</button>
                <button className="secondary" onClick={toggleRealtime} disabled={busy || !connected}>
                  {liveVoice ? "Encerrar Realtime" : "Conversar por voz"}
                </button>
                <label className="secondary upload-action">
                  Anexar
                  <input type="file" onChange={(e) => upload(e.target.files?.[0] || null)} />
                </label>
              </div>
              {reply && <div className="reply" aria-live="polite">{reply}</div>}
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
            <SectionHeader eyebrow="Epistemic Layer" title="Ciência" description="Evidência, mecanismos, hipóteses e fronteiras." />
            <div className="cards-grid">
              <div className="feature-card atlas-surface"><span>Ciência Interna</span><strong>Modelos próprios</strong><p>Hipóteses formais, mecanismos e previsões.</p></div>
              <div className="feature-card atlas-surface"><span>Fronteira</span><strong>Conhecimento novo</strong><p>Linhas científicas e técnicas emergentes.</p></div>
              <div className="feature-card atlas-surface"><span>Evidência</span><strong>Dossiês auditáveis</strong><p>Fonte → claim → evidência → interpretação.</p></div>
            </div>
          </>
        );
      case "Pesquisa":
        return (
          <>
            <SectionHeader eyebrow="Research" title="Pesquisa" description="Backlog, linhas em andamento, bloqueios e próximos experimentos." />
            <div className="metric-grid">
              <Metric label="Questões registradas" value={researchItems.length || 0} />
              <Metric label="Bloqueios atuais" value={status?.research?.blocked ?? "—"} />
              <Metric label="Mundos possíveis" value={worldPrograms.length || "—"} hint="programas carregados" />
              <Metric label="Método" value="RIA" />
            </div>
            <div className="form-panel atlas-surface"><h3>Registrar uma pergunta de pesquisa</h3><p>Ela entra no backlog do ATLAS com prioridade inicial média.</p><div className="form-row"><input value={researchQuestion} onChange={(event) => setResearchQuestion(event.target.value)} placeholder="Qual pergunta você quer investigar?" /><button className="primary" disabled={busy || !researchQuestion.trim()} onClick={() => void runAction<ResearchItem>("/research", { ministry_id: status?.ministries?.[0]?.id || "research", question: researchQuestion.trim(), priority: 0.5 }, (item) => `Pergunta registrada: ${item.question}`)}>Registrar</button></div></div>
            {researchItems.length > 0 && <div className="event-list">{researchItems.map((item) => <article className="event-card atlas-surface" key={item.item_id}><div><span className="eyebrow">{item.ministry_id} · {item.status}</span><strong>{item.question}</strong></div><small>Prioridade {item.priority.toFixed(1)}</small></article>)}</div>}
          </>
        );
      case "Mundos":
        return (
          <>
            <SectionHeader eyebrow="Possible Worlds" title="Mundos" description="Modelos concorrentes, probabilidades e o que pode distingui-los." />
            {worldError && <div className="notice atlas-surface">{worldError}</div>}
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
              <div className="mini-orbit" />
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
          <div><strong>ATLAS</strong><span>1.9</span></div>
        </div>
        <nav className="side-nav">
          {navigation.map((item) => (
            <button key={item} title={item} aria-label={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}><span className="nav-label">{item}</span><span className="nav-mark">{{ Agora: "AG", Talk: "TK", Radar: "RD", Urgente: "!", Ciência: "CI", Pesquisa: "PQ", Mundos: "MU", Laboratório: "LB", Ministérios: "MI", Conselho: "CO", Awareness: "AW", "My World": "MW", Inovação: "IN", Ações: "AC" }[item]}</span></button>
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

      {menuOpen && <><button className="menu-backdrop" aria-label="Fechar menu" onClick={() => setMenuOpen(false)} /><aside className="module-drawer atlas-surface" aria-label="Todos os módulos"><div className="drawer-heading"><div><span className="eyebrow">ATLAS 1.9</span><h2>Módulos</h2></div><button className="secondary" onClick={() => setMenuOpen(false)}>Fechar</button></div><nav>{navigation.map((item) => <button key={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}>{item}<span>›</span></button>)}</nav></aside></>}

      {commandOpen && <div className="command-overlay" role="dialog" aria-modal="true" aria-label="Buscar módulo" onMouseDown={(event) => { if (event.target === event.currentTarget) setCommandOpen(false); }}><div className="command-dialog atlas-surface"><input autoFocus value={commandQuery} onChange={(event) => setCommandQuery(event.target.value)} placeholder="Buscar um módulo do ATLAS…" onKeyDown={(event) => { if (event.key === "Enter" && visibleCommands[0]) goTo(visibleCommands[0]); }} /><div className="command-results">{visibleCommands.map((item) => <button key={item} onClick={() => goTo(item)}>{item}<span>↵</span></button>)}{visibleCommands.length === 0 && <p>Nenhum módulo corresponde à busca.</p>}</div><small>Pressione Esc para fechar · Enter para abrir</small></div></div>}

      <nav className="mobile-nav atlas-surface" aria-label="Navegação principal">
        {primaryMobile.map((item) => <button key={item} className={active === item ? "active" : ""} onClick={() => goTo(item)}>{item}</button>)}
        <button aria-expanded={menuOpen} onClick={() => setMenuOpen((value) => !value)}>Mais</button>
      </nav>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
