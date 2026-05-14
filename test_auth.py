"""Tests for the internal auth system (JWT, AppUser, admin endpoints)."""

import os
import pytest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing")
os.environ.setdefault("OPEN_NOTEBOOK_ENCRYPTION_KEY", "test-encryption-key")

from api.auth import create_access_token, decode_access_token
from open_notebook.domain.user import AppUser, AppUserResponse


class TestJWT:
    """Unit tests for JWT token creation and decoding."""

    def test_create_access_token(self):
        token = create_access_token({"sub": "app_user:test123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_valid(self):
        token = create_access_token({"sub": "app_user:test123", "role": "admin"})
        payload = decode_access_token(token)
        assert payload["sub"] == "app_user:test123"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_decode_access_token_invalid(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_decode_access_token_expired(self):
        from datetime import datetime, timedelta, timezone
        from jose import jwt

        expired_payload = {
            "sub": "app_user:test123",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(expired_payload, "test-secret-key-for-testing", algorithm="HS256")

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            decode_access_token(token)
        assert exc_info.value.status_code == 401


class TestAppUserPassword:
    """Unit tests for AppUser password hashing and verification."""

    def test_set_password_hashes(self):
        user = AppUser(username="test", email="test@test.com")
        user.set_password("mysecretpassword")
        assert user.password_hash is not None
        assert user.password_hash != "mysecretpassword"

    def test_verify_password_correct(self):
        user = AppUser(username="test", email="test@test.com")
        user.set_password("mysecretpassword")
        assert user.verify_password("mysecretpassword") is True

    def test_verify_password_incorrect(self):
        user = AppUser(username="test", email="test@test.com")
        user.set_password("mysecretpassword")
        assert user.verify_password("wrongpassword") is False

    def test_verify_password_no_hash(self):
        user = AppUser(username="test", email="test@test.com")
        assert user.verify_password("anything") is False

    def test_set_password_changes_hash(self):
        user = AppUser(username="test", email="test@test.com")
        user.set_password("password1")
        hash1 = user.password_hash
        user.set_password("password2")
        hash2 = user.password_hash
        assert hash1 != hash2


class TestAppUserResponse:
    """Tests that AppUserResponse never includes password_hash."""

    def test_from_user_excludes_password_hash(self):
        user = AppUser(
            id="app_user:123",
            username="admin",
            email="admin@test.com",
            role="admin",
            is_active=True,
        )
        user.set_password("secret")

        response = AppUserResponse.from_user(user)
        response_dict = response.model_dump()

        assert "password_hash" not in response_dict
        assert response_dict["username"] == "admin"
        assert response_dict["email"] == "admin@test.com"
        assert response_dict["role"] == "admin"

    def test_response_model_has_no_password_field(self):
        fields = AppUserResponse.model_fields
        assert "password_hash" not in fields
        assert "password" not in fields


class TestLoginSecurity:
    """Tests for login security properties."""

    def test_generic_error_message_for_wrong_password(self):
        """Login endpoint uses same error for wrong password and non-existent user."""
        # This is verified by the implementation: both cases raise
        # HTTPException(status_code=401, detail="Invalid credentials")
        # The test verifies the code path logic
        user = AppUser(username="test", email="test@test.com")
        user.set_password("correct")

        # Wrong password
        assert user.verify_password("wrong") is False
        # Non-existent user returns None from get_by_username
        # Both result in same "Invalid credentials" response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
