# ATLAS Mobile + Voice Agent Architecture

## Objective

Evolve ATLAS from a research/forecasting system into a persistent conversational intelligence accessible from mobile and desktop, while preserving auditability, epistemic controls and human approval.

## Design principle

ATLAS Voice is not a separate assistant. It is an interface to the same ATLAS identity, memory, Research Engine, Operational Awareness layer and ASAS/ZAZA context system.

```text
Voice / Text / Mobile
        ↓
Conversation Gateway
        ↓
ATLAS Orchestrator
        ↓
Awareness + Memory + Research + ASAS/ZAZA
        ↓
Tools / Web / GitHub / Automations / Sensors
```

## Recommended voice architecture

Use a full-duplex voice frontend with a separate ATLAS backend.

The voice layer handles:
- microphone input;
- interruption / barge-in;
- turn taking;
- speech output;
- wake / push-to-talk interaction.

The backend handles:
- reasoning;
- research;
- hypothesis testing;
- memory;
- RIA / Reverse RIA;
- tool calls;
- permissions;
- self-check;
- audit trail.

This keeps voice replaceable without coupling the ATLAS brain to one speech provider.

## Mobile application

Recommended initial path: responsive PWA first, then native wrapper or React Native/Expo if background audio, push notifications and device integrations require it.

### Main screens

1. **Talk**
   - hold-to-talk and continuous conversation modes;
   - live transcript;
   - interrupt ATLAS while it speaks;
   - switch between concise and research modes.

2. **Radar**
   - morning radar;
   - critical alerts;
   - forecasts by horizon;
   - confidence and evidence status.

3. **Research Lab**
   - active hypotheses;
   - experiments;
   - evidence graph;
   - pending data requirements;
   - internal science progress.

4. **Awareness**
   - goals;
   - current ATLAS state;
   - uncertainty;
   - module health;
   - drift warnings;
   - recent checkpoints.

5. **Memory / Context Capsules**
   - active projects;
   - canonical summaries;
   - decisions;
   - permissions;
   - portable context.

6. **Actions**
   - proposed actions;
   - approvals;
   - execution log;
   - rollback.

## ZAZA / ASAS integration

Reuse the ZAZA concepts as operational primitives:

- **Context Capsule** → portable project/mission state;
- **Identity Guardian** → preserve ATLAS constitution across models and devices;
- **World Compiler** → convert spoken intentions into formal target states;
- **Resonance Map** → relate people, projects, data and opportunities;
- **Semantic Wormholes** → transfer useful structure across domains;
- **Distributed Operational Identity** → multiple ATLAS clients sharing one governed state;
- **Temporal State Transport** → restore and compare historical checkpoints.

## Voice modes

### Conversational
Fast spoken answers with minimal latency.

### Research
ATLAS acknowledges the request by voice, delegates deep work to the backend, and returns the result when ready.

### Briefing
ATLAS reads selected Radar / Vigilance / Research findings.

### Hands-free
Wake word or persistent session. Requires explicit user controls and privacy indicators.

### Critical alert
High-priority automation result can generate a push notification and optionally a spoken briefing after user interaction.

## Memory model

Do not store raw audio by default.

Recommended:
- transient audio stream;
- transcript;
- semantic memory;
- canonical project state;
- explicit saved memories;
- audit events.

Voice should use the same Context Capsules as text so mobile, web and future desktop clients remain synchronized.

## Security

- API keys never embedded in the mobile client;
- ephemeral session tokens for realtime audio;
- human approval for external writes or sensitive actions;
- visible microphone state;
- configurable retention;
- rate/cost limits;
- tool permission boundaries;
- checkpoint before self-modification;
- no autonomous constitutional changes.

## Jarvis lessons to assimilate

Useful patterns seen in current open-source Jarvis-like assistants:
- wake phrase;
- push-to-talk fallback;
- streaming speech;
- interruptions;
- local STT/TTS fallback;
- model/provider routing;
- personal memory;
- MCP / tool support;
- agent delegation;
- visible approvals;
- local-first privacy options.

ATLAS should assimilate the architecture, not copy a branded persona or couple itself to one implementation.

## Proposed milestones

### M1 — Voice Gateway
- realtime audio session;
- transcript;
- streaming response;
- interruption;
- ATLAS backend delegation.

### M2 — Mobile PWA
- installable mobile UI;
- Talk, Radar, Research and Awareness screens;
- push notifications;
- secure authentication.

### M3 — Unified memory
- Context Capsules;
- cross-device conversation state;
- project memory;
- voice/text continuity.

### M4 — Agentic voice
- tool calls;
- GitHub;
- research;
- automations;
- approval flow;
- spoken execution summaries.

### M5 — Ambient ATLAS
- optional wake word;
- local speech fallback;
- sensor context;
- proactive alerts;
- configurable presence modes.

## Architectural decision

Prefer **voice interface + independent ATLAS backend** over a monolithic voice model. This preserves the current Research Engine and allows the conversational layer, reasoning model and speech stack to evolve independently.
