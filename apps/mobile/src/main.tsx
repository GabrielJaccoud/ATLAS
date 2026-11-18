import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { atlasFetch, loadConfig, saveConfig } from "./api";
import "./styles.css";

const tabs = [
  "Talk", "Agora", "Radar", "Urgente", "Ciência", "Pesquisa",
  "Ministérios", "Conselho", "Awareness", "My World", "Ações",
];

type Status = {
  mode?: { mode?: string };
  ministries?: Array<{ id: string; name: string }>;
  research?: { blocked: number };
  my_world?: { nodes: number; edges: number };
};

type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  start(): void;
  stop(): void;
  onresult: ((event: any) => void) | null;
  onerror: ((event: any) => void) | null;
  onend: (() => void) | null;
};

function App() {
  const [active, setActive] = useState("Agora");
  const [status, setStatus] = useState<Status | null>(null);
  const [connected, setConnected] = useState(false);
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [speakReplies, setSpeakReplies] = useState(true);
  const initial = loadConfig();
  const [baseUrl, setBaseUrl] = useState(initial.baseUrl);
  const [token, setToken] = useState(initial.token);

  const speechRecognition = useMemo(() => {
    if (typeof window === "undefined") return null;
    const Ctor = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!Ctor) return null;
    const recognition: SpeechRecognitionLike = new Ctor();
    recognition.lang = "pt-BR";
    recognition.interimResults = false;
    recognition.continuous = false;
    return recognition;
  }, []);

  async function refresh() {
    try {
      const data = await atlasFetch<Status>("/status");
      setStatus(data);
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }

  useEffect(() => {
    refresh();
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }
  }, []);

  function speak(text: string) {
    if (!speakReplies || !("speechSynthesis" in window) || !text.trim()) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  async function connect() {
    saveConfig({ baseUrl, token });
    await refresh();
  }

  async function send(textOverride?: string) {
    const outgoing = (textOverride ?? message).trim();
    if (!outgoing) return;
    setBusy(true);
    setReply("");
    try {
      const data = await atlasFetch<{ text: string; mode: string }>("/chat", {
        method: "POST",
        body: JSON.stringify({ message: outgoing, context: { surface: "mobile", input: textOverride ? "voice" : "text" } }),
      });
      setReply(data.text);
      setMessage("");
      speak(data.text);
    } catch (error) {
      const text = error instanceof Error ? error.message : String(error);
      setReply(text);
    } finally {
      setBusy(false);
    }
  }

  function listen() {
    setActive("Talk");
    if (!speechRecognition) {
      setReply("Reconhecimento de voz não está disponível neste navegador. Use o campo de texto.");
      return;
    }
    speechRecognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim() || "";
      setMessage(transcript);
      setListening(false);
      if (transcript && connected) void send(transcript);
    };
    speechRecognition.onerror = () => setListening(false);
    speechRecognition.onend = () => setListening(false);
    setListening(true);
    speechRecognition.start();
  }

  async function upload(file: File | null) {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    setBusy(true);
    try {
      const data = await atlasFetch<{ artifact_id: string; kind: string }>("/artifacts", {
        method: "POST", body: form,
      });
      const text = `Arquivo recebido · ${data.kind} · ${data.artifact_id}`;
      setReply(text);
      speak(text);
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">ATLAS 1.8</span>
          <h1>Fractal Cognitive Network</h1>
        </div>
        <div className={connected ? "status online" : "status"}>
          {connected ? `${status?.mode?.mode || "NORMAL"} · ONLINE` : "OFFLINE"}
        </div>
      </header>

      {!connected && (
        <section className="panel connection">
          <p className="eyebrow">Conectar ao seu ATLAS</p>
          <div className="form-row">
            <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api..." />
            <input value={token} onChange={e => setToken(e.target.value)} placeholder="Token do ATLAS" type="password" />
            <button className="primary" onClick={connect}>Conectar</button>
          </div>
          <p className="muted small">O token fica armazenado apenas neste navegador/aparelho.</p>
        </section>
      )}

      <section className="hero">
        <button
          className={listening ? "orb listening" : "orb"}
          aria-label="Falar com ATLAS"
          onClick={listen}
          disabled={busy}
        />
        <div>
          <p className="eyebrow">{active}</p>
          <h2>{listening ? "Estou ouvindo." : active === "Talk" ? "Fale comigo." : "Como posso ajudar?"}</h2>
          <p className="muted">
            Voz, pesquisa, projetos, ministérios, conselhos e ações em uma única presença.
          </p>
        </div>
      </section>

      {active === "Talk" && (
        <section className="panel talk-panel">
          <textarea
            value={message}
            onChange={e => setMessage(e.target.value)}
            placeholder="Escreva ou toque no núcleo para falar com o ATLAS..."
            rows={4}
          />
          <div className="actions">
            <button className="primary" onClick={() => send()} disabled={busy || !connected}>
              {busy ? "Processando…" : "Enviar"}
            </button>
            <button className="secondary" onClick={listen} disabled={busy}>
              {listening ? "Ouvindo…" : "Falar"}
            </button>
            <label className="upload">
              Anexar arquivo
              <input type="file" onChange={e => upload(e.target.files?.[0] || null)} />
            </label>
            <label className="toggle">
              <input type="checkbox" checked={speakReplies} onChange={e => setSpeakReplies(e.target.checked)} />
              Responder por voz
            </label>
          </div>
          {reply && <div className="reply">{reply}</div>}
        </section>
      )}

      <section className="panel">
        <div className="grid">
          <article><strong>Awareness</strong><span>{connected ? "Estado conectado" : "Aguardando conexão"}</span></article>
          <article><strong>Ministérios</strong><span>{status?.ministries?.length ?? "—"} unidades registradas</span></article>
          <article><strong>Pesquisa</strong><span>{status?.research?.blocked ?? "—"} bloqueios ativos</span></article>
          <article><strong>My World</strong><span>{status?.my_world?.nodes ?? "—"} nós · {status?.my_world?.edges ?? "—"} relações</span></article>
        </div>
      </section>

      <nav className="tabs" aria-label="ATLAS sections">
        {tabs.map(tab => (
          <button key={tab} className={tab === active ? "active" : ""} onClick={() => setActive(tab)}>
            {tab}
          </button>
        ))}
      </nav>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
