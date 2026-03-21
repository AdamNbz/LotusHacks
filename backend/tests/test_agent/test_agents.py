"""
Unit tests cho Insurance Agents (Triage + Coverage).
Mock LLM calls để test logic mà không cần API key thật.
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from app.agent.models.schemas import IncidentInput, TriageOutput, CoverageOutput
from app.agent.agents.insurance_agents import (
    InsuranceAgents,
    _parse_json_response,
    _call_llm,
)


class TestParseJsonResponse:
    """Test JSON parsing từ LLM response."""

    def test_parse_clean_json(self):
        """Test parse JSON sạch."""
        content = '{"is_complex": true, "description": "Test"}'
        result = _parse_json_response(content)
        assert result["is_complex"] is True

    def test_parse_json_with_markdown(self):
        """Test parse JSON wrapped trong markdown code block."""
        content = '```json\n{"is_complex": false, "description": "OK"}\n```'
        result = _parse_json_response(content)
        assert result["is_complex"] is False

    def test_parse_json_with_generic_codeblock(self):
        """Test parse JSON wrapped trong generic code block."""
        content = '```\n{"is_eligible": true, "description": "Eligible"}\n```'
        result = _parse_json_response(content)
        assert result["is_eligible"] is True

    def test_parse_invalid_json(self):
        """Test parse JSON không hợp lệ → raise exception."""
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("This is not JSON")


class TestTriageAgent:
    """Test Agent 1 (Triage Agent) với mock LLM."""

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_triage_complex_incident(self, mock_retriever, mock_llm, sample_incident_complex):
        """Test: sự cố phức tạp → is_complex = True."""
        mock_retriever.retrieve.return_value = "Điều 8: Tai nạn liên hoàn..."
        mock_llm.return_value = json.dumps({
            "is_complex": True,
            "description": "Tai nạn liên hoàn 3 xe, có thương tích, thuộc Điều 8."
        })

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_complex)
        result = agents.run_triage_agent(incident)

        assert isinstance(result, TriageOutput)
        assert result.is_complex is True
        assert len(result.description) > 0
        mock_llm.assert_called_once()

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_triage_simple_incident(self, mock_retriever, mock_llm, sample_incident_simple):
        """Test: sự cố đơn giản → is_complex = False."""
        mock_retriever.retrieve.return_value = "Phạm vi bảo hiểm..."
        mock_llm.return_value = json.dumps({
            "is_complex": False,
            "description": "Trầy xước nhẹ, không có bên thứ ba."
        })

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_simple)
        result = agents.run_triage_agent(incident)

        assert isinstance(result, TriageOutput)
        assert result.is_complex is False

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_triage_llm_error_fallback(self, mock_retriever, mock_llm, sample_incident_simple):
        """Test: LLM lỗi → fallback is_complex = True (an toàn)."""
        mock_retriever.retrieve.return_value = "Context..."
        mock_llm.side_effect = Exception("API Error")

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_simple)
        result = agents.run_triage_agent(incident)

        assert isinstance(result, TriageOutput)
        assert result.is_complex is True  # Fallback: mặc định phức tạp
        assert "Fallback" in result.description


class TestCoverageAgent:
    """Test Agent 2 (Coverage Agent) với mock LLM."""

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_coverage_eligible(self, mock_retriever, mock_llm, sample_incident_simple):
        """Test: sự cố đủ điều kiện bồi thường."""
        mock_retriever.retrieve.return_value = "Phạm vi bảo hiểm: va chạm..."
        mock_llm.return_value = json.dumps({
            "is_eligible": True,
            "description": "Thuộc phạm vi bảo hiểm vật chất xe."
        })

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_simple)
        result = agents.run_coverage_agent(incident)

        assert isinstance(result, CoverageOutput)
        assert result.is_eligible is True

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_coverage_not_eligible(self, mock_retriever, mock_llm, sample_incident_simple):
        """Test: sự cố bị loại trừ."""
        mock_retriever.retrieve.return_value = "Loại trừ: trầy xước tự gây..."
        mock_llm.return_value = json.dumps({
            "is_eligible": False,
            "description": "Trầy xước tự gây không thuộc phạm vi bảo hiểm."
        })

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_simple)
        result = agents.run_coverage_agent(incident)

        assert isinstance(result, CoverageOutput)
        assert result.is_eligible is False

    @patch("app.agent.agents.insurance_agents._call_llm")
    @patch("app.agent.agents.insurance_agents.policy_retriever")
    def test_coverage_llm_error_fallback(self, mock_retriever, mock_llm, sample_incident_simple):
        """Test: LLM lỗi → fallback is_eligible = False."""
        mock_retriever.retrieve.return_value = "Context..."
        mock_llm.side_effect = Exception("API Error")

        agents = InsuranceAgents()
        incident = IncidentInput(**sample_incident_simple)
        result = agents.run_coverage_agent(incident)

        assert isinstance(result, CoverageOutput)
        assert result.is_eligible is False  # Fallback: mặc định không đủ điều kiện
        assert "Fallback" in result.description
