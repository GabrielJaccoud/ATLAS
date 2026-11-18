import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const tabs = [
  "Talk",
  "Agora",
  "Radar",
  "Urgente",
  "Ciência",
  "Pesquisa",
  "Ministérios",
  "Conselho",
  "Awareness",
  "My World",
  "Ações",
];

function App() {
  const [active, setActive] = useState("Agora");

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <span className="eyebrow">ATLAS 1.8</span>
          <h1>Fractal Cognitive Network</h1>
        </div>
        <div className="status">NORMAL · ONLINE</div>
      </header>

      <section className="hero">
        <div className="orb" aria-label="ATLAS voice core" />
        <div>
          <p className="eyebrow">{active}</p>
          <h2>Como posso ajudar?</h2>
          <p className="muted">
            Voz, pesquisa, projetos, ministérios, conselhos e ações em uma única presença.
          </p>
        </div>
      </section>

      <section className="panel">
        <div className="grid">
          <article><strong>Awareness</strong><span>Saúde operacional e deriva</span></article>
          <article><strong>Ministérios</strong><span>Rede cognitiva especializada</span></article>
          <article><strong>Pesquisa</strong><span>Hipóteses e experimentos ativos</span></article>
          <article><strong>My World</strong><span>Projetos, ideias e oportunidades</span></article>
        </div>
      </section>

      <nav className="tabs" aria-label="ATLAS sections">
        {tabs.map((tab) => (
          <button
            key={tab}
            className={tab === active ? "active" : ""}
            onClick={() => setActive(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
