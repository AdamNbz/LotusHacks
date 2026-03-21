"""
Unit tests cho Auth API endpoints.
Mock MongoDB để test routing logic.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from bson import ObjectId
from datetime import datetime, timezone


@pytest.mark.asyncio
class TestSignupEndpoint:
    """Test POST /auth/signup."""

    @patch("app.auth.routers.auth.get_db")
    async def test_signup_success(self, mock_get_db, client):
        """Test signup thành công."""
        mock_db = MagicMock()
        mock_users = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_users)
        mock_get_db.return_value = mock_db

        # User chưa tồn tại
        mock_users.find_one = AsyncMock(return_value=None)
        mock_users.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id=ObjectId())
        )

        response = await client.post("/auth/signup", json={
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "SecurePass123!"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"

    @patch("app.auth.routers.auth.get_db")
    async def test_signup_duplicate_email(self, mock_get_db, client):
        """Test signup email đã tồn tại → 409."""
        mock_db = MagicMock()
        mock_users = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_users)
        mock_get_db.return_value = mock_db

        # User đã tồn tại
        mock_users.find_one = AsyncMock(return_value={
            "_id": ObjectId(),
            "email": "existing@example.com"
        })

        response = await client.post("/auth/signup", json={
            "email": "existing@example.com",
            "full_name": "Existing User",
            "password": "SecurePass123!"
        })

        assert response.status_code == 409

    async def test_signup_invalid_email(self, client):
        """Test signup email không hợp lệ → 422."""
        response = await client.post("/auth/signup", json={
            "email": "not-valid",
            "full_name": "Test User",
            "password": "SecurePass123!"
        })
        assert response.status_code == 422


@pytest.mark.asyncio
class TestSigninEndpoint:
    """Test POST /auth/signin."""

    @patch("app.auth.routers.auth.get_db")
    async def test_signin_invalid_credentials(self, mock_get_db, client):
        """Test signin email không tồn tại → 401."""
        mock_db = MagicMock()
        mock_users = AsyncMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_users)
        mock_get_db.return_value = mock_db

        mock_users.find_one = AsyncMock(return_value=None)

        response = await client.post("/auth/signin", json={
            "email": "nonexist@example.com",
            "password": "SecurePass123!"
        })
        assert response.status_code == 401

    async def test_signin_missing_fields(self, client):
        """Test signin thiếu trường → 422."""
        response = await client.post("/auth/signin", json={
            "email": "test@example.com"
        })
        assert response.status_code == 422
