import asyncio
import pytest
from unittest.mock import patch

from multi_agent_system.core.orchestrator import CrewOrchestrator


@pytest.mark.asyncio
async def test_quick_analysis_flow_success(monkeypatch):
    orch = CrewOrchestrator()

    async def fake_scrape(url):
        return {"url": url, "content": "hello", "title": "t", "meta_description": "d"}

    async def fake_cls(data):
        return {"success": True, "classification": {"type": "other", "reason": "r", "confidence": 0.9}}

    async def fake_sum(data, ctx):
        return {"success": True, "summary": {"summary": "s", "word_count": 10, "sentence_count": 3, "key_points": ["k"]}}

    with patch.object(orch, "_scrape_website_with_retry", side_effect=fake_scrape), \
         patch.object(orch, "_run_classifier_with_retry", side_effect=fake_cls), \
         patch.object(orch, "_run_summary_with_retry", side_effect=fake_sum):
        res = await orch.get_quick_analysis("https://example.com", use_cache=False)
        assert res["status"] == "completed"
        assert res["classification"]["success"] is True
        assert res["summary"]["success"] is True


