import json
import pytest
from multi_agent_system.api.main import app


@pytest.fixture
def client():
    app.config.update({"TESTING": True})
    return app.test_client()


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "healthy"


def test_scrape_bad_input(client):
    resp = client.post("/scrape", json={})
    assert resp.status_code == 400


def test_analyze_requires_api_key(client):
    resp = client.post("/analyze", json={"url": "https://example.com"})
    assert resp.status_code == 401


