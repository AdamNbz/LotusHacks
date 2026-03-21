"""
Unit tests cho Auth security module (passwords, tokens).
"""
import pytest
from app.auth.security.passwords import hash_password, verify_password
from app.auth.security.tokens import create_access_token
from jose import jwt


class TestPasswords:
    """Test password hashing và verification."""

    def test_hash_password(self):
        """Test hash password tạo ra hash khác với plaintext."""
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_correct_password(self):
        """Test verify password đúng → True."""
        password = "MySecurePassword123!"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test verify password sai → False."""
        hashed = hash_password("CorrectPassword")
        assert verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test cùng password tạo ra hash khác nhau (salt)."""
        password = "SamePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Bcrypt dùng random salt
        # Nhưng cả 2 đều verify đúng
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestTokens:
    """Test JWT token creation."""

    def test_create_token(self):
        """Test tạo JWT token."""
        token = create_access_token(subject="user123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_subject(self):
        """Test token chứa subject (user ID)."""
        token = create_access_token(subject="user123")
        # Decode without verification (just to check payload)
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert payload["sub"] == "user123"

    def test_token_has_expiry(self):
        """Test token có thời gian hết hạn."""
        token = create_access_token(subject="user123")
        payload = jwt.decode(token, "test-secret", algorithms=["HS256"])
        assert "exp" in payload
        assert "iat" in payload
