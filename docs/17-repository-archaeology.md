# ATLAS 1.8 — Repository Archaeology & Assimilation Map

## Scope

This audit covers every repository visible to the connected GitHub integration for the GabrielJaccoud account at the time of review. The goal is not to merge old code blindly, but to recover reusable ideas, architecture, workflows and product concepts.

Classification:
- **Assimilate** — strong fit for ATLAS core
- **Adapt** — useful idea/component, needs redesign
- **Reference** — useful pattern or domain case
- **Archive** — little/no ATLAS value beyond history
- **Inspect deeper** — promising but insufficient evidence from top-level files

## High-value assimilation targets

| Repository | Signal | ATLAS use | Decision |
|---|---|---|---|
| ZazaUnifiedAI | perception/decision/action/evolution, memory, LLM orchestration, science, tools, ASAS precursor | constitutional architecture, epistemics, world/context models, research loop | Assimilate selectively |
| meu-cerebro-digital | voice, local Ollama, STT/TTS, specialized agents, n8n, multimedia, monitoring, auto-optimization | Voice Gateway, local fallback, workflow engine, agent runtime, system telemetry | Assimilate concepts; rewrite core |
| webmind | six-agent swarm, orchestrator, live agent feed, history, shareable reports, premium mobile-first UX | ministry/agent orchestration patterns, visible agent products, report pipeline, UI inspiration | Adapt |
| nexor | relational intelligence, matchmaking, ecosystem graph, opportunities, stakeholders | Resonance Map, Personal/Venture graph, opportunity engine | Assimilate concept |
| arca-app | spatial analysis, OpenCV, geomagnetism, environmental context, BaZi/Kua/Feng Shui modules | Environmental Atlas, context signatures, tradition-science bridge, spatial sensing | Assimilate under epistemic controls |
| FragmentosdaAlma | adaptive world generation, eAREAL, creative triggers, state-dependent narrative | World Compiler, adaptive simulation, generative environments | Adapt |
| Portalesx / portales-app | AR portals, creator/explorer modes, contextual world-generation direction | mobile AR layer, environmental overlays, Portal Simulator | Adapt |
| StoryLeaf | narrative trees, adaptive content, multimodal reading, learning, conversion | knowledge trees, creative translocation, education ministry | Adapt |
| Kairos | presence-aware productivity, mentor role, rituals/reflection | personal operating layer, daily reflection, attention/presence model | Adapt |
| details-app | opportunity scraping, alerts, document upload, checklist, mobile roadmap | Opportunity Intelligence / grants radar / ingestion pipeline | Assimilate pattern |
| Assistente-Inteligente-de-Capta-o-e-Pr--Proposta | human-in-the-loop opportunity capture, OCR/NLP, compliance, pre-proposal | opportunity qualification, evidence extraction, approval workflow | Assimilate pattern |
| SingularyApp-Singulary / SingularyApp-Backend | multimodal experience shell + backend/auth stack | actuator/experience layer, future immersive interface | Inspect deeper + adapt |
| TheOdysseyOfGames | React Native mobile, cultural knowledge through interactive narrative | mobile gamification, learning journeys | Reference/Adapt |
| mostardinha / most3 / mostardinha-landing | PWA, audio, audiobook, quiz, multimedia | multimodal content delivery, PWA packaging | Reference |
| institutoceudoacoes | donations, recurring payments, impact dashboard, partnerships | social-impact domain connectors; impact metrics | Reference |
| a-plus-website / a-plus-group-website | venture ecosystem presentation, projects/investors/blog | Personal Venture Hub domain model | Reference |
| Aura-Celeste | conversion UX, lightweight landing patterns, emotional branding | communication/creative ministry examples | Reference |

## Low-signal / infrastructure / historical repositories

| Repository | Assessment | Decision |
|---|---|---|
| EBIM-Engenharia | top-level README only | Inspect deeper only if domain need arises |
| institutoceu | minimal institutional README | Reference; project data belongs in private Personal Hub |
| fullstack-prisma-nextjs-blog | generic Prisma/NextAuth starter | Reference for auth/data patterns only |
| portales-backend | minimal Flask backend dependencies | Superseded by newer architecture |
| PORTALES | no useful top-level content found | Archive/inspect only if needed |
| mostard | mostly Vite starter shell | Archive as implementation shell |
| a-plus-website-github | effectively empty top-level signal | Archive |
| cerebrotecnicodoAmaisStudio. | no useful top-level content found | Inspect only if files later surface |
| ATLA | near-empty ATLAS precursor | Archive after confirming no unique history |
| expo | very large Expo repository/fork, not an ATLAS-specific concept | Reference platform only; never vendor into ATLAS |
| ATLAS | official destination repository | Active canonical system |

## Cross-project capabilities recovered

### 1. Local/Hybrid Intelligence
From meu-cerebro-digital: Ollama/local-model fallback, offline/private operation, local STT/TTS, monitoring, agent delegation and n8n workflow generation.
Target: **Hybrid Runtime** that can route some tasks to local models and some to cloud models.

### 2. Agent Swarm UX
From webmind: visible agent lifecycle, specialized outputs, orchestrator, history and shareable reports.
Target: **Ministry Live Feed** and **Council Reports**, without exposing private chain-of-thought.

### 3. Relational Intelligence
From nexor: people/project/opportunity graph, synergy, matchmaking and stakeholder networks.
Target: **Resonance Graph / Opportunity Graph** connected to My World.

### 4. Environmental Intelligence
From arca-app: spatial analysis, environmental signatures, geomagnetic data and traditional models separable from measurements.
Target: **Environmental Atlas**, with measured, modeled and traditional layers explicitly labeled.

### 5. Adaptive World Generation
From FragmentosdaAlma and Portalesx: adaptive environments, creative triggers, generated-world actions and AR contextual experiences.
Target: **World Compiler + Portal Simulator + Adaptive Scenario Lab**.

### 6. Narrative/Knowledge Trees
From StoryLeaf: root/trunk/branch/leaf metaphor, adaptive reading/learning and document conversion.
Target: **Knowledge Tree** view for theories, projects, evidence and learning paths.

### 7. Human-Centered Time
From Kairos: important/urgent + presence, mentor mode and reflection.
Target: optional **Presence Layer** inside My World, separated from medical inference.

### 8. Opportunity Intelligence
From details-app and the pre-proposal assistant: scraping/ingestion, OCR/NLP extraction, qualification, compliance, alerts, human validation and pre-proposal preparation.
Target: **Opportunity Intelligence** for grants, ventures, institutional and research opportunities.

## Architectural rule for assimilation

Recover -> Inspect -> Test -> Reframe -> Benchmark -> RIA -> Assimilate or Reject

For frontier/traditional systems, tradition / hypothesis / measurement / simulation remain separate fields.

## New ATLAS 1.8 modules created from this audit

- Fractal Ministry self-state
- Collective Mind integrator
- Grand Council scaffold

## Recommended next implementation queue

1. Context Capsules
2. Ministry event ledger
3. ASAS Coordinator
4. Research backlog per ministry
5. Global Knowledge Assimilation gate
6. My World / Personal Venture graph
7. Opportunity Intelligence
8. Voice Gateway
9. Hybrid local/cloud runtime
10. Mobile PWA
11. Ministry Live Feed
12. Environmental Atlas
13. Knowledge Tree
14. World Compiler / Portal Simulator
15. Optional React Native shell after PWA validation

## Do not merge directly

Avoid direct code merges from legacy projects until tests exist, dependencies are current, security review passes, ownership/data boundaries are clear, epistemic claims are reclassified and the component demonstrates measurable gain.