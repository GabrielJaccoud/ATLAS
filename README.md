# ATLAS 1.9 — Possible Worlds & Experimental Intelligence

ATLAS is a governed personal, research, causal and experimental intelligence system. Version 1.9 adds explicit possible worlds, world ensembles, Bayesian posterior updates, reality-gap tracking and minimal discriminant experiment selection.

ATLAS does **not** claim phenomenal consciousness or sentience. Its "awareness" is computational self-modeling and metacognition.

## Core architecture

```text
User / Voice / Mobile / ChatGPT
              ↓
            ATLAS
              ↓
             ASAS
     ┌────────┼─────────────┐
Governance  Ministries  Possible Worlds Lab
     │          │              │
Guardian     Agents        World Ensemble
Epistemic    Research      Experiments
Mnemosyne    Models        Reality Gap
Red Team     Simulation    RIA / Innovation
     └────────┼─────────────┘
              ↓
        Collective Mind
              ↓
 Knowledge / Technologies / Actions
```

## ATLAS 1.9 additions

- Possible Worlds Lab
- world ensembles instead of binary hypothesis framing
- Bayesian posterior updates from observed outcomes
- reality-gap monitoring
- pairwise identifiability analysis
- minimal discriminant experiment selection
- experiment economy: information vs cost/time/risk
- robustness/representativeness weighting
- cross-world technology synthesis
- four initial research programs:
  - Multiscale Semantic Image Codec
  - Space Anomaly Fusion
  - Multimodal Physiology
  - Ancient Knowledge / Cross-Corpus Residuals
- API endpoints for world programs and observations
- Android APK build pipeline with Capacitor

## Existing foundation

- Operational Awareness
- fractal ministries
- ASAS Context Capsules
- Governance Network
- Support Cell
- Event Bus, Homeostasis, Failure Memory and Reflexes
- Regeneration Protocol
- Research Backlog
- My World
- Opportunity Intelligence
- Artifact Gateway and provenance
- OpenAI Responses
- Ollama
- Realtime voice
- persistent FastAPI/PostgreSQL backend
- installable PWA

## Run locally

```bash
python -m pip install -e '.[dev]'
export ATLAS_API_TOKEN=dev-atlas-token
uvicorn apps.api.main:app --reload
```

Mobile:

```bash
cd apps/mobile
npm install
npm run dev
```

## Android

The Android workflow regenerates a Capacitor project, builds the web bundle, adds microphone permission and produces a debug APK artifact.

```text
.github/workflows/android-apk.yml
```

A production-distribution APK/AAB still requires a release signing keystore. The debug APK is suitable for direct testing on Android.

## Quality

```bash
pytest -q
ruff check atlas apps tests
cd apps/mobile && npm run build
```

## Research principle

```text
The purpose of a hypothesis is not to win.
The purpose is to generate a world that can lose to reality.
```

ATLAS keeps observation, inference, model, hypothesis, simulation, tradition and fictional requirements in distinct epistemic classes.
