# ATLAS 1.8 — Governance Network & Support Cell

## One external identity

ATLAS remains the only external identity/voice.

Internal governance bodies are not competing personas. They are functions that protect, coordinate, challenge, remember, repair and improve the system.

## Governance map

- **ASAS** — coordination, context routing, cross-ministry integration
- **Guardian** — identity, constitution, permissions, consent, safety boundaries
- **Epistemic Council** — evidence, uncertainty, claim status, contradiction
- **Mnemosyne** — memory curation, continuity, history, deduplication, retrieval
- **Operations Governor** — resource health, cost, latency, queues, capacity
- **Outcomes Observatory** — prediction-vs-result, calibration, regression, learning
- **Red Team** — challenge, failure modes, overconfidence, adversarial review
- **Integration Chamber** — cross-ministry conflicts and synthesis
- **Support Cell** — repair, maintenance, tooling, capability construction and recovery

## Support Cell: the "general services cell"

The Support Cell is a transversal internal workshop.

Any ministry or governance organ may request help when it detects:
- malfunction;
- degraded health;
- missing tool;
- missing skill;
- capacity bottleneck;
- migration need;
- observability gap;
- need for a new agent/capability;
- recovery after regression.

It is intentionally not a ministry because it does not own a world-domain. It serves the entire organism.

## Support flow

requester -> Support Cell -> diagnosis -> minimal reversible plan -> Codex/tooling if needed -> sandbox -> RIA if new capability -> validation -> outcome check -> Awareness update

## Healing metaphor

"Curative" behavior is operational, not biological:

- detect damage/regression;
- isolate affected component;
- preserve healthy state;
- restore from known-good checkpoint;
- repair or replace component;
- test recovery;
- feed root-cause learning back to ATLAS.

## Expansion flow

A ministry may say:

> I have reached a capability limit. I propose a new specialist/tool.

The request becomes a Capability Proposal and passes through:

ministry -> Awareness -> Support Cell -> ASAS -> RIA -> sandbox -> Guardian/approval when required -> deployment -> Outcomes Observatory

## Why this should exist

Without a shared support cell, each ministry would reinvent:
- engineering;
- tooling;
- debugging;
- migrations;
- observability;
- recovery;
- capability expansion.

That creates duplication and inconsistent standards.

The Support Cell centralizes maintenance while keeping domain knowledge inside ministries.

## Autonomy boundary

Support Cell may diagnose, draft repairs, create tests, propose tools and prepare implementation.

It may not:
- change constitutional invariants;
- silently elevate permissions;
- deploy irreversible changes;
- overwrite global memory;
- bypass RIA for major capability additions.

## Codex relationship

Codex acts as an engineering executor available to the Support Cell.

Support Cell defines the problem and acceptance criteria.
ASAS supplies context.
Codex implements in a branch.
Tests/CI validate.
RIA assesses net gain.
Guardian protects privileged boundaries.
Human approval is required when policy says so.
