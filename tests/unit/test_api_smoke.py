from fastapi.testclient import TestClient

from apps.api.main import app


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
