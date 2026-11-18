from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from .db import count_by_kind, list_all_record_dicts
from .settings import settings


STARTED_AT = time.time()


def metrics_snapshot() -> dict[str, object]:
    return {
        "uptime_seconds": int(time.time() - STARTED_AT),
        "pid": os.getpid(),
        "environment": settings.environment,
        "database": "postgres" if settings.database_url.startswith("postgres") else "sqlite",
        "openai_configured": bool(settings.openai_api_key),
        "ollama_configured": bool(settings.ollama_url),
        "records_by_kind": count_by_kind(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def export_backup() -> dict[str, object]:
    records = list_all_record_dicts()
    return {
        "schema": "atlas.logical-backup.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "records": records,
    }


def write_backup_file() -> str:
    root = Path(settings.artifact_dir) / "backups"
    root.mkdir(parents=True, exist_ok=True)
    name = datetime.now(timezone.utc).strftime("atlas-backup-%Y%m%dT%H%M%SZ.json")
    path = root / name
    path.write_text(json.dumps(export_backup(), ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
