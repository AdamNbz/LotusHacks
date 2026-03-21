"""
Unit tests cho Agent Workflow API endpoints.
Mock agents để test routing logic mà không cần LLM thật.
"""
import json
import pytest
from unittest.mock import patch
from app.agent.models.schemas import TriageOutput, CoverageOutput


@pytest.mark.asyncio
class TestProcessIncidentEndpoint:
    """Test POST /api/v1/agent/workflow/process-incident."""

    @patch("app.agent.routers.workflow.insurance_agents")
    async def test_complex_incident_returns_assisted_mode(self, mock_agents, client, sample_incident_complex):
        """Test: sự cố phức tạp → trả về ASSISTED_MODE."""
        mock_agents.run_triage_agent.return_value = TriageOutput(
            is_complex=True,
            description="Tai nạn liên hoàn, có thương tích."
        )

        response = await client.post(
            "/api/v1/agent/workflow/process-incident",
            json=sample_incident_complex
        )

        assert response.status_code == 200
        data = response.json()
        assert data["triage_result"]["is_complex"] is True
        assert data["coverage_result"] is None
        assert "ASSISTED_MODE" in data["next_step"]
        assert data["assisted_mode"] is not None
        # Agent 2 không được gọi
        mock_agents.run_coverage_agent.assert_not_called()

    @patch("app.agent.routers.workflow.insurance_agents")
    async def test_simple_eligible_incident(self, mock_agents, client, sample_incident_simple):
        """Test: sự cố đơn giản + đủ điều kiện → ELIGIBLE."""
        mock_agents.run_triage_agent.return_value = TriageOutput(
            is_complex=False,
            description="Trầy xước nhẹ."
        )
        mock_agents.run_coverage_agent.return_value = CoverageOutput(
            is_eligible=True,
            description="Thuộc phạm vi bảo hiểm."
        )

        response = await client.post(
            "/api/v1/agent/workflow/process-incident",
            json=sample_incident_simple
        )

        assert response.status_code == 200
        data = response.json()
        assert data["triage_result"]["is_complex"] is False
        assert data["coverage_result"]["is_eligible"] is True
        assert "ELIGIBLE" in data["next_step"]

    @patch("app.agent.routers.workflow.insurance_agents")
    async def test_simple_not_eligible_incident(self, mock_agents, client, sample_incident_simple):
        """Test: sự cố đơn giản + không đủ điều kiện → NOT_ELIGIBLE."""
        mock_agents.run_triage_agent.return_value = TriageOutput(
            is_complex=False,
            description="Trầy xước nhẹ."
        )
        mock_agents.run_coverage_agent.return_value = CoverageOutput(
            is_eligible=False,
            description="Trầy xước tự gây bị loại trừ."
        )

        response = await client.post(
            "/api/v1/agent/workflow/process-incident",
            json=sample_incident_simple
        )

        assert response.status_code == 200
        data = response.json()
        assert data["coverage_result"]["is_eligible"] is False
        assert "NOT_ELIGIBLE" in data["next_step"]

    async def test_invalid_input_returns_422(self, client):
        """Test: input không hợp lệ → 422 Validation Error."""
        response = await client.post(
            "/api/v1/agent/workflow/process-incident",
            json={"time": "2024-01-01"}  # Thiếu nhiều trường bắt buộc
        )
        assert response.status_code == 422


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test GET /health."""

    async def test_health_check(self, client):
        """Test health check trả về OK."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
class TestRagStatsEndpoint:
    """Test GET /api/v1/agent/workflow/rag-stats."""

    async def test_rag_stats(self, client):
        """Test rag-stats trả về thông tin collection."""
        response = await client.get("/api/v1/agent/workflow/rag-stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_chunks" in data
        assert "collection_name" in data
