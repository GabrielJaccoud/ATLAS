from fastapi.testclient import TestClient

from apps.api.db import init_db
from apps.api.main import app


init_db()
client = TestClient(app)
HEADERS = {"Authorization": "Bearer dev-atlas-token"}


def test_health_is_public():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["version"] == "1.8.0"


def test_status_requires_token():
    assert client.get("/status").status_code == 401
    response = client.get("/status", headers=HEADERS)
    assert response.status_code == 200
    assert "ministries" in response.json()


def test_local_chat_is_executable_without_cloud_key():
    response = client.post(
        "/chat",
        headers=HEADERS,
        json={"message": "Teste o ATLAS", "context": {}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] in {"local", "cloud"}
    assert data["text"]


def test_artifact_upload_accepts_text_file():
    response = client.post(
        "/artifacts",
        headers=HEADERS,
        files={"file": ("hello.txt", b"hello atlas", "text/plain")},
    )
    assert response.status_code == 200
    assert response.json()["kind"] == "document"


def test_research_and_world_are_persistent_api_resources():
    research = client.post(
        "/research",
        headers=HEADERS,
        json={"ministry_id": "science_frontiers", "question": "What changed?", "priority": 0.8},
    )
    assert research.status_code == 200
    listed = client.get("/research/science_frontiers", headers=HEADERS)
    assert listed.status_code == 200
    assert any(item["question"] == "What changed?" for item in listed.json())

    node = client.post(
        "/world/nodes",
        headers=HEADERS,
        json={
            "kind": "project",
            "name": "ATLAS",
            "attributes": {"domains": ["ai"], "capabilities": ["research"]},
        },
    )
    assert node.status_code == 200
    world = client.get("/world", headers=HEADERS)
    assert world.status_code == 200
    assert any(item["name"] == "ATLAS" for item in world.json()["nodes"])


def test_event_governance_and_support_endpoints():
    event = client.post(
        "/events",
        headers=HEADERS,
        json={
            "event_type": "health.alert",
            "source": "test",
            "payload": {"metric": "latency"},
            "priority": 30,
            "tags": ["health"],
        },
    )
    assert event.status_code == 200

    governance = client.post(
        "/governance/route",
        headers=HEADERS,
        json={
            "source": "science_frontiers",
            "purpose": "Need a new tool",
            "categories": ["tooling", "capability_gap"],
        },
    )
    assert governance.status_code == 200
    assert "support_cell" in governance.json()["routed_to"]

    support = client.post(
        "/support/plan",
        headers=HEADERS,
        json={
            "requester": "science_frontiers",
            "symptom": "Missing capability",
            "desired_outcome": "Build a safe tool",
            "requested_services": ["capability_build"],
            "requires_code_change": True,
        },
    )
    assert support.status_code == 200
    assert support.json()["route_to_codex"] is True


def test_metrics_and_backup_are_available():
    metrics = client.get("/metrics", headers=HEADERS)
    assert metrics.status_code == 200
    assert "records_by_kind" in metrics.json()

    backup = client.get("/backup", headers=HEADERS)
    assert backup.status_code == 200
    assert backup.json()["schema"] == "atlas.logical-backup.v1"


def test_owner_pairing_returns_session_token():
    response = client.post("/auth/session", json={"code": "000000"})
    assert response.status_code == 200
    token = response.json()["token"]
    authenticated = client.get("/status", headers={"Authorization": f"Bearer {token}"})
    assert authenticated.status_code == 200


def test_owner_pairing_rejects_wrong_code():
    response = client.post("/auth/session", json={"code": "wrong"})
    assert response.status_code == 401
