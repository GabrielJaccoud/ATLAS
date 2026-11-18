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
    return () => realtimeRef.current?.stop();
  }, []);

  useEffect(() => {
    if (active === "Mundos" || active === "Laboratório") void loadWorlds();
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
        aria-label="Conversar com ATLAS"
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
              {reply && <div className="reply">{reply}</div>}
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
          </>
        );
      case "Urgente":
        return (
          <>
            <SectionHeader eyebrow="Priority" title="Urgente" description="Somente o que exige atenção imediata." />
            <div className="empty-state atlas-surface"><strong>Nenhum evento crítico carregado.</strong><p>Eventos HIGH/CRITICAL aparecerão aqui com evidência, impacto e ação recomendada.</p></div>
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
              <Metric label="Bloqueios atuais" value={status?.research?.blocked ?? "—"} />
              <Metric label="Mundos possíveis" value={worldPrograms.length || "—"} hint="quando API 1.9 estiver pública" />
              <Metric label="Método" value="RIA" />
              <Metric label="Critério" value="Teste discriminante" />
            </div>
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
              {!worldPrograms.length && !worldError && <div className="empty-state atlas-surface">Carregando mundos possíveis…</div>}
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
            <div className="empty-state atlas-surface"><strong>Governança pronta para interface dedicada.</strong><p>Epistemic Council, Guardian, Red Team, Integration Chamber e Outcomes Observatory serão exibidos aqui.</p></div>
          </>
        );
      case "Awareness":
        return (
          <>
            <SectionHeader eyebrow="Self Model" title="Awareness" description="Saúde operacional, drift, falhas, reflexos e regeneração." />
            <div className="metric-grid">
              <Metric label="Conexão" value={connected ? "ONLINE" : "OFFLINE"} />
              <Metric label="OpenAI" value={status?.provider?.openai_configured ? "Configurada" : "—"} />
              <Metric label="Modo" value={status?.mode?.mode || "—"} />
              <Metric label="Estado" value={voiceState} />
            </div>
          </>
        );
      case "My World":
        return (
          <>
            <SectionHeader eyebrow="Personal Intelligence" title="My World" description="Projetos, pessoas, organizações, ativos e relações." />
            <div className="hero-command atlas-surface">
              <div className="hero-copy"><span className="eyebrow">Knowledge Graph</span><h3>{status?.my_world?.nodes ?? "—"} nós · {status?.my_world?.edges ?? "—"} relações</h3><p>O grafo visual completo será a próxima camada desta superfície.</p></div>
              <div className="mini-orbit" />
            </div>
          </>
        );
      case "Inovação":
        return (
          <>
            <SectionHeader eyebrow="Hypothesis Forge" title="Inovação" description="Hipóteses transformadas em mecanismos e tecnologias candidatas." />
            <div className="pipeline atlas-surface">
              {["Fonte", "Hipótese", "Mundo", "Mecanismo", "Tecnologia", "RIA", "Sandbox", "Benchmark"].map((step) => <span key={step}>{step}</span>)}
            </div>
          </>
        );
      case "Ações":
        return (
          <>
            <SectionHeader eyebrow="Execution" title="Ações" description="O que o ATLAS recomenda, o que exige aprovação e o que foi executado." />
            <div className="empty-state atlas-surface"><strong>Nenhuma ação pendente carregada.</strong><p>Ações futuras terão risco, reversibilidade, responsável, evidência e botão de aprovação.</p></div>
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
            <button key={item} className={active === item ? "active" : ""} onClick={() => setActive(item)}>{item}</button>
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
          <VoiceCore compact />
        </header>

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

      <nav className="mobile-nav atlas-surface">
        {primaryMobile.map((item) => <button key={item} className={active === item ? "active" : ""} onClick={() => setActive(item)}>{item}</button>)}
        <button onClick={() => setActive("Mundos")}>Mais</button>
      </nav>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
