"""
Pytest conftest.py - Shared fixtures cho tất cả tests.
"""
import os
import pytest
from unittest.mock import MagicMock, AsyncMock

# Set test environment variables trước khi import app
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-unit-tests")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    """Async HTTP client cho testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_incident_simple():
    """Test data: sự cố đơn giản (trầy xước nhẹ)."""
    return {
        "time": "2024-06-16 14:00",
        "location": "Quận 1, TP.HCM",
        "description": "Xe bị trầy xước nhẹ ở cản sau khi đỗ xe",
        "incident_type": "tray_xuoc",
        "third_party_involved": False,
        "vehicle_drivable": True,
        "injuries": False,
        "insurer": "PTI"
    }


@pytest.fixture
def sample_incident_complex():
    """Test data: sự cố phức tạp (tai nạn liên hoàn)."""
    return {
        "time": "2024-06-15 08:30",
        "location": "Cao tốc TP.HCM - Long Thành, km 25",
        "description": "Va chạm liên hoàn 3 xe trên cao tốc do trời mưa trơn. Xe tôi bị hư hỏng nặng phần đầu.",
        "incident_type": "va_cham",
        "third_party_involved": True,
        "vehicle_drivable": False,
        "injuries": True,
        "insurer": "Bảo Việt"
    }


@pytest.fixture
def sample_incident_flood():
    """Test data: sự cố ngập nước."""
    return {
        "time": "2024-07-20 07:00",
        "location": "Quận Bình Thạnh, TP.HCM",
        "description": "Xe bị ngập nước do mưa lớn, động cơ bị thủy kích, không khởi động được",
        "incident_type": "ngap_nuoc",
        "third_party_involved": False,
        "vehicle_drivable": False,
        "injuries": False,
        "insurer": "Bảo Việt"
    }
