import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_token_count():
    payload = {"text": "This is a test", "model": "gpt-4"}
    response = client.post("/api/tokens", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("tokens"), int)
    assert data.get("model") == "gpt-4"

def test_process_content():
    payload = {"text": "Test content", "platform": "LinkedIn"}
    response = client.post("/api/process", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "formatted" in data and "safe" in data and "headlines" in data
    assert isinstance(data["headlines"], list)
