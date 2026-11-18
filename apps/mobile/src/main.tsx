import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { atlasFetch, loadConfig, pairOwner } from "./api";
import { RealtimeHandle, startRealtimeVoice } from "./realtime";
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
  const [active, setActive] = useState("Talk");
  const [status, setStatus] = useState<Status | null>(null);
  const [connected, setConnected] = useState(false);
  const [ownerCode, setOwnerCode] = useState("");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("");
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [liveVoice, setLiveVoice] = useState(false);
  const [speakReplies, setSpeakReplies] = useState(true);
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const realtimeRef = useRef<RealtimeHandle | null>(null);

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

  useEffect(() => {
    refresh();
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/sw.js").catch(() => undefined);
    }
    const onInstall = (event: Event) => {
      event.preventDefault();
      setInstallPrompt(event);
    };
    window.addEventListener("beforeinstallprompt", onInstall as EventListener);
    return () => {
      realtimeRef.current?.stop();
      window.removeEventListener("beforeinstallprompt", onInstall as EventListener);
    };
  }, []);

  async function pair() {
    if (!ownerCode.trim()) return;
    setBusy(true);
    setReply("");
    try {
      await pairOwner(ownerCode.trim());
      setOwnerCode("");
      await refresh();
      setReply("Este celular foi pareado com o seu ATLAS.");
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  async function installApp() {
    if (!installPrompt) {
      setReply("No Android, abra o menu ⋮ do navegador e toque em “Instalar app” ou “Adicionar à tela inicial”.");
      return;
    }
    await installPrompt.prompt();
    await installPrompt.userChoice;
    setInstallPrompt(null);
  }

  function speak(text: string) {
    if (!speakReplies || !("speechSynthesis" in window) || !text.trim()) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "pt-BR";
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }

  async function send(textOverride?: string) {
    const outgoing = (textOverride ?? message).trim();
    if (!outgoing || !connected) {
      if (!connected) setReply("Primeiro pareie este celular com o ATLAS.");
      return;
    }
    setBusy(true);
    setReply("");
    try {
      const data = await atlasFetch<{ text: string; mode: string }>("/chat", {
        method: "POST",
        body: JSON.stringify({
          message: outgoing,
          context: { surface: "mobile", input: textOverride ? "voice" : "text" },
        }),
      });
      setReply(data.text);
      setMessage("");
      speak(data.text);
    } catch (error) {
      setReply(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  }

  function listen() {
    setActive("Talk");
    if (!connected) {
      setReply("Primeiro pareie este celular com o ATLAS.");
      return;
    }
    if (!speechRecognition) {
      setReply("Reconhecimento de voz não está disponível neste navegador. Use o modo Realtime.");
      return;
    }
    speechRecognition.onresult = (event: any) => {
      const transcript = event.results?.[0]?.[0]?.transcript?.trim() || "";
      setMessage(transcript);
      setListening(false);
      if (transcript) void send(transcript);
    };
    speechRecognition.onerror = () => setListening(false);
    speechRecognition.onend = () => setListening(false);
    setListening(true);
    speechRecognition.start();
  }

  async function toggleRealtime() {
    setActive("Talk");
    if (realtimeRef.current) {
      realtimeRef.current.stop();
      realtimeRef.current = null;
      setLiveVoice(false);
      setReply("Conversa em tempo real encerrada.");
      return;
    }
    if (!connected) {
      setReply("Primeiro pareie este celular com o ATLAS.");
      return;
    }
    setBusy(true);
    setReply("");
    try {
      const handle = await startRealtimeVoice((event) => {
        if (event?.type === "response.output_audio_transcript.delta" && event.delta) {
          setReply((current) => current + event.delta);
        }
      });
      realtimeRef.current = handle;
      setLiveVoice(true);
      setReply("Modo Realtime ativo. Pode falar naturalmente.");
    } catch (error) {
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
      const data = await atlasFetch<{ artifact_id: string; kind: string }>("/artifacts", {
        method: "POST",
        body: form,
      });
      const text = `Arquivo recebido · ${data.kind}`;
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
        <div className="top-actions">
          <button className="secondary install" onClick={installApp}>Instalar</button>
          <div className={connected ? "status online" : "status"}>
            {connected ? `${status?.mode?.mode || "NORMAL"} · ONLINE` : "NÃO PAREADO"}
          </div>
        </div>
      </header>

      {!connected && (
        <section className="panel connection">
          <p className="eyebrow">Parear este celular</p>
          <h3>Entre uma vez. Depois o ATLAS reconhece este aparelho.</h3>
          <div className="pair-row">
            <input
              value={ownerCode}
              onChange={e => setOwnerCode(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") void pair(); }}
              placeholder="Código do proprietário"
              inputMode="numeric"
              autoComplete="one-time-code"
            />
            <button className="primary" onClick={pair} disabled={busy}>Parear</button>
          </div>
        </section>
      )}

      <section className="hero">
        <button
          className={liveVoice ? "orb live" : listening ? "orb listening" : "orb"}
          aria-label="Falar com ATLAS"
          onClick={liveVoice ? toggleRealtime : listen}
          disabled={busy}
        />
        <div>
          <p className="eyebrow">{active}</p>
          <h2>{liveVoice ? "Conversa ao vivo." : listening ? "Estou ouvindo." : "Fale comigo."}</h2>
          <p className="muted">
            Toque no núcleo, fale e o ATLAS envia automaticamente. Para conversa contínua, use Realtime.
          </p>
        </div>
      </section>

      <section className="panel talk-panel">
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void send();
            }
          }}
          placeholder="Digite aqui — Enter envia. Ou toque no núcleo e fale."
          rows={4}
        />
        <div className="actions">
          <button className="primary" onClick={() => send()} disabled={busy || !connected}>
            {busy ? "Processando…" : "Enviar"}
          </button>
          <button className="secondary" onClick={listen} disabled={busy || liveVoice || !connected}>
            {listening ? "Ouvindo…" : "Falar e enviar"}
          </button>
          <button
            className={liveVoice ? "secondary active-live" : "secondary"}
            onClick={toggleRealtime}
            disabled={busy || !connected}
          >
            {liveVoice ? "Encerrar Realtime" : "Conversa Realtime"}
          </button>
          <label className="upload">
            Anexar
            <input type="file" onChange={e => upload(e.target.files?.[0] || null)} />
          </label>
          <label className="toggle">
            <input
              type="checkbox"
              checked={speakReplies}
              onChange={e => setSpeakReplies(e.target.checked)}
            />
            Falar respostas
          </label>
        </div>
        {reply && <div className="reply">{reply}</div>}
      </section>

      <section className="panel">
        <div className="grid">
          <article><strong>Awareness</strong><span>{connected ? "Conectado" : "Aguardando pareamento"}</span></article>
          <article><strong>Ministérios</strong><span>{status?.ministries?.length ?? "—"} unidades</span></article>
          <article><strong>Pesquisa</strong><span>{status?.research?.blocked ?? "—"} bloqueios</span></article>
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
