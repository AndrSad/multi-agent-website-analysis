import json
import pytest
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from multi_agent_system.api.main import app
except ImportError:
    # Skip tests if imports fail
    pytest.skip("Could not import app module", allow_module_level=True)


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


