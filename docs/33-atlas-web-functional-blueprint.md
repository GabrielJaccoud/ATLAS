# ATLAS Web Premium — Blueprint Funcional

## Arquitetura de produto

### Camada 1 — Command Surface
Interface principal.

### Camada 2 — Intelligence Services
Chat, voz, pesquisa, mundos, ministérios, conselho, awareness.

### Camada 3 — Evidence & Memory
event ledger, records, research, My World, artifacts.

### Camada 4 — Models & Experiments
Possible Worlds, RIA, Hypothesis Forge, simulations.

### Camada 5 — Execution
Support Cell, Codex, actions, external connectors.

---

## Layout mestre desktop

12-column grid.

- left rail: 88px collapsed / 240px expanded;
- center workspace: flexible;
- context rail: 320px optional;
- top command bar: 64px;
- global voice core can float center-bottom or center-top depending on screen.

---

## Navigation model

Every screen has:
- title;
- status;
- primary metric;
- current recommendation;
- evidence/provenance access;
- voice command availability.

---

## Interaction model

### One click
open module.

### Long press / secondary action
context menu.

### Command palette
Ctrl/Cmd+K.

### Voice
“ATLAS, abra Pesquisa.”
“ATLAS, compare os mundos.”
“ATLAS, mostre apenas eventos críticos.”
“ATLAS, mande isto ao Conselho.”

---

## Global states

NORMAL
RESEARCH_INTENSIVE
RESOURCE_SAVING
CRISIS
EXPLORATION
MAINTENANCE

Each state changes:
- recommendations;
- animation density;
- alert prominence;
- resource use;
- default screen emphasis.

---

## Data contracts by screen

### Agora
GET /status
GET /events
GET /records/*
plus future scheduler/connectors.

### Talk
POST /chat
POST /voice/realtime-token
POST /artifacts

### Pesquisa
GET/POST /research

### Mundos
GET /possible-worlds/programs
GET /possible-worlds/programs/{id}
POST /possible-worlds/programs/{id}/observe

### Ministérios
GET /status
POST /missions/route
future dedicated ministry endpoint.

### Conselho
GET /councils/{cadence}
POST /governance/route

### Awareness
GET /metrics
GET /status
future drift/homeostasis endpoints.

### My World
GET/POST /world

### Inovação
future RIA/technology-seed endpoints.

### Ações
future action registry + approval endpoint.

---

## Implementation sequence

### Phase A — Foundation
- design tokens;
- logo;
- shell;
- navigation;
- responsive grid;
- shared cards;
- status primitives;
- loading/error/empty states.

### Phase B — Operational screens
- Agora;
- Talk;
- Radar;
- Pesquisa;
- Mundos;
- Laboratório.

### Phase C — Governance/organization
- Ministérios;
- Conselho;
- Awareness;
- Ações.

### Phase D — Personal intelligence
- My World;
- Opportunity;
- connected apps.

### Phase E — Advanced motion
- voice core;
- waveform;
- world probability transitions;
- contextual particles;
- critical states.

### Phase F — Packaging
- PWA;
- Android;
- iOS.
