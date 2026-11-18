# ATLAS 1.8 — Fractal Cognitive Network

ATLAS is a governed personal, research and causal intelligence system. It combines operational self-awareness, specialized ministries, ASAS coordination, persistent memory, research, opportunity intelligence, multimodal artifacts, voice and a mobile interface under one ATLAS identity.

ATLAS 1.8 is an executable system. It does **not** claim phenomenal consciousness or sentience; its "awareness" is computational self-modeling and metacognition.

## Core architecture

```text
User / Voice / Mobile / ChatGPT
              ↓
            ATLAS
              ↓
             ASAS
     ┌────────┼────────┐
Governance  Ministries  Support Cell
     │          │           │
Guardian     Agents       Codex
Epistemic    Research     Repair
Mnemosyne    Models       Tooling
Red Team     Simulation   Expansion
     └────────┼───────────┘
              ↓
     Collective Mind
              ↓
  Knowledge / Memory / Actions
```

## Implemented

- Operational Awareness and drift detection
- fractal ministries and bounded autonomy
- Collective Mind and council architecture
- ASAS Context Capsules
- epistemic Global Knowledge Gate
- Governance Network and Support Cell
- Event Bus, Homeostasis, Failure Memory and Reflexes
- global operating modes and regeneration/checkpoints
- Research Backlog
- My World personal/project graph
- Opportunity Intelligence
- Artifact Gateway and provenance, including JXL-aware routing
- hybrid cloud/local model routing
- OpenAI Responses adapter
- Ollama local adapter
- secure Realtime client-secret endpoint
- WebRTC full-duplex voice + browser speech fallback
- persistent FastAPI backend with SQLite/PostgreSQL
- persistent chats, missions, research, projects, opportunities, councils, events and support records
- observability and logical backup
- installable mobile-first PWA
- CI for Python and mobile builds
- secure Render production Blueprint

## Run locally

Python 3.12+ and Node 22+.

```bash
python -m pip install -e '.[dev]'
export ATLAS_API_TOKEN=dev-atlas-token
uvicorn apps.api.main:app --reload
```

In another terminal:

```bash
cd apps/mobile
npm install
npm run dev
```

Optional OpenAI cloud/realtime:

```bash
export ATLAS_OPENAI_API_KEY=...
```

Optional Ollama local runtime:

```bash
export ATLAS_OLLAMA_URL=http://localhost:11434
export ATLAS_OLLAMA_MODEL=llama3.2
```

## Quality

```bash
pytest -q
ruff check atlas apps tests
cd apps/mobile && npm run build
```

## Production

Deployment infrastructure is defined in `render.yaml`.

The planned production topology uses:
- existing `atlas-postgres` PostgreSQL database;
- `atlas-18-api` web service;
- `atlas-18-mobile` static PWA;
- generated API secret;
- database credentials injected by Render.

See:
- `docs/18-atlas-1.8-fractal-cognitive-network.md`
- `docs/20-governance-and-support-cell.md`
- `docs/21-artifact-fabric-and-biological-inspiration.md`
- `docs/22-implementation-status.md`
- `docs/23-production-runtime.md`

## Epistemic rule

```text
Phenomenon ≠ interpretation ≠ mechanism.
Everything may enter investigation; not everything receives equal evidential weight.
```

Observations, inference, models, hypotheses, simulations, traditions and subjective experience remain distinct epistemic classes.
