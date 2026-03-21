"""
Unit tests cho Auth schemas.
"""
import pytest
from pydantic import ValidationError
from app.auth.schemas.auth import SignUpRequest, SignInRequest, GoogleAuthRequest


class TestSignUpRequest:
    """Test SignUpRequest schema validation."""

    def test_valid_signup(self):
        """Test signup hợp lệ."""
        req = SignUpRequest(
            email="test@example.com",
            full_name="Nguyen Van A",
                   password="SecurePass123!"
        )
        assert req.email == "test@example.com"
        assert req.full_name == "Nguyen Van A"

    def test_invalid_email(self):
        """Test email không hợp lệ → ValidationError."""
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="not-an-email",
                full_name="Test",
                password="SecurePass123!"
            )

    def test_missing_password(self):
        """Test thiếu password → ValidationError."""
        with pytest.raises(ValidationError):
            SignUpRequest(
                email="test@example.com",
                full_name="Test"
            )


class TestSignInRequest:
    """Test SignInRequest schema validation."""

    def test_valid_signin(self):
        """Test signin hợp lệ."""
        req = SignInRequest(
            email="test@example.com",
            password="SecurePass123!"
        )
        assert req.email == "test@example.com"

    def test_missing_email(self):
        """Test thiếu email → ValidationError."""
        with pytest.raises(ValidationError):
            SignInRequest(password="SecurePass123!")


class TestGoogleAuthRequest:
    """Test GoogleAuthRequest schema validation."""

    def test_valid_google_auth(self):
        """Test Google auth hợp lệ."""
        req = GoogleAuthRequest(id_token="fake-google-token-123")
        assert req.id_token == "fake-google-token-123"

    def test_missing_token(self):
        """Test thiếu token → ValidationError."""
        with pytest.raises(ValidationError):
            GoogleAuthRequest()
