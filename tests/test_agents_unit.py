import pytest
from unittest.mock import patch

from multi_agent_system.agents.classifier_agent import ClassifierAgent
from multi_agent_system.agents.summary_agent import SummaryAgent
from multi_agent_system.agents.ux_reviewer_agent import UXReviewerAgent
from multi_agent_system.agents.design_advisor_agent import DesignAdvisorAgent


@patch("multi_agent_system.agents.classifier_agent.ChatOpenAI")
def test_classifier_parses_valid_json(mock_llm):
    agent = ClassifierAgent()
    task_result = {
        "type": "blog",
        "reason": "Contains posts with dates and tags",
        "confidence": 0.9,
        "industry": "tech",
        "target_audience": "developers",
        "business_model": "ads",
    }
    mock_llm.return_value = mock_llm
    with patch.object(ClassifierAgent, "_create_classification_task") as mk:
        class Dummy:
            def execute(self_inner):
                return str(task_result)

        mk.return_value = Dummy()
        res = agent.classify_website({"content": "x"})
        assert res["success"] is True
        assert res["classification"]["type"] == "blog"


@patch("multi_agent_system.agents.summary_agent.ChatOpenAI")
def test_summary_truncation_and_counts(mock_llm):
    agent = SummaryAgent()
    fake_text = "Sentence. " * 200
    with patch.object(SummaryAgent, "_create_summary_task") as mk:
        class Dummy:
            def execute(self_inner):
                return f"РЕЗЮМЕ: {fake_text} КЛЮЧЕВЫЕ_МОМЕНТЫ: A, B, C"

        mk.return_value = Dummy()
        res = agent.summarize_website({"content": fake_text})
        assert res["success"] is True
        assert res["summary"]["word_count"] <= 150


@patch("multi_agent_system.agents.ux_reviewer_agent.ChatOpenAI")
def test_ux_reviewer_recommendations_count(mock_llm):
    agent = UXReviewerAgent()
    recs = [
        {"title": "t1", "description": "d", "priority": "high", "impact": "i"},
        {"title": "t2", "description": "d", "priority": "high", "impact": "i"},
        {"title": "t3", "description": "d", "priority": "high", "impact": "i"},
        {"title": "t4", "description": "d", "priority": "high", "impact": "i"},
        {"title": "t5", "description": "d", "priority": "high", "impact": "i"},
    ]
    payload = {
        "strengths": ["s1"],
        "weaknesses": ["w1"],
        "recommendations": recs,
        "overall_score": 7.5,
        "word_count": 450,
    }
    with patch.object(UXReviewerAgent, "_create_ux_review_task") as mk:
        class Dummy:
            def execute(self_inner):
                return str(payload)

        mk.return_value = Dummy()
        res = agent.review_ux({"content": "x"})
        assert res["success"] is True
        assert len(res["ux_review"]["recommendations"]) == 5


@patch("multi_agent_system.agents.design_advisor_agent.ChatOpenAI")
def test_design_only_for_landing(mock_llm):
    agent = DesignAdvisorAgent()
    not_lp = {"success": True, "classification": {"type": "blog"}}
    res = agent.advise_design({"content": "x"}, classification_context=not_lp)
    assert res["success"] is False
    assert res["error"].lower().startswith("design advice")


