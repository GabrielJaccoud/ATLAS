# ATLAS 1.8 — Production Runtime

## Runtime topology

Mobile/PWA -> ATLAS API -> Governance/ASAS/Ministries -> Providers/Tools
                         -> PostgreSQL
                         -> Artifact store
                         -> Event/Failure/Research ledgers

## Provider hierarchy

1. OpenAI Responses API when ATLAS_OPENAI_API_KEY is configured.
2. Ollama when ATLAS_OLLAMA_URL is configured and reachable.
3. Deterministic ATLAS routing/status mode when no generative provider is configured.

## Voice hierarchy

1. OpenAI Realtime WebRTC when the backend can mint a short-lived client secret.
2. Browser speech recognition + speech synthesis fallback.
3. Text chat.

The main OpenAI API key never belongs in the browser.

## Persistence

The API stores durable logical records for:
- chat input/output
- missions
- research
- My World nodes/edges
- opportunity matches
- councils
- mode changes
- artifact metadata
- events
- governance decisions
- support requests
- backups

SQLite is valid for local development.
PostgreSQL is the intended deployed database.

## Security boundaries

- bearer token required for all non-health API routes;
- Render generates the production token;
- main cloud-model key remains server-side;
- Realtime clients receive only short-lived secrets;
- high-risk/external/constitutional actions remain approval-gated;
- unknown artifacts are quarantined by classification policy;
- uploaded file size is capped at the API boundary.

## Recovery

Logical backup export is available through the protected API.
Regeneration uses known-good checkpoints, isolation, regression testing and incident memory.

## Current deployment target

Render:
- atlas-postgres (existing free database)
- atlas-18-api (planned free web service)
- atlas-18-mobile (planned static site)

Infrastructure is defined in render.yaml.
