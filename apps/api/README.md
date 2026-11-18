# ATLAS API

Run locally:

```bash
export ATLAS_API_TOKEN=change-me
uvicorn apps.api.main:app --reload
```

Optional cloud language model:

```bash
export ATLAS_OPENAI_API_KEY=...
export ATLAS_OPENAI_MODEL=gpt-6-luna
```

Persistent database:

```bash
export ATLAS_DATABASE_URL=postgresql+psycopg://user:pass@host/db
```

Core endpoints:

- GET /health
- GET /status
- POST /chat
- POST /missions/route
- POST/GET /research
- POST/GET /world
- POST /opportunities/match/{target_id}
- GET /councils/{cadence}
- POST /mode/{mode}
- POST /artifacts

All endpoints except /health require:

`Authorization: Bearer <ATLAS_API_TOKEN>`
