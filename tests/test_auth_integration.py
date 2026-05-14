"""
Integration tests for the auth system.

These tests require a running SurrealDB instance.
Skip with: pytest -m "not integration"
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from api.auth import create_access_token


def _make_client():
    from api.main import app

    return TestClient(app)


def _admin_token(user_id="app_user:admin1"):
    return create_access_token({"sub": user_id, "role": "admin"})


def _user_token(user_id="app_user:user1"):
    return create_access_token({"sub": user_id, "role": "user"})


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestLoginEndpoint:
    """Integration tests for POST /api/auth/login."""

    def _mock_user(self, password="correct", is_active=True, role="user"):
        from open_notebook.domain.user import AppUser

        user = AppUser(
            id="app_user:test1",
            username="testuser",
            email="test@example.com",
            role=role,
            is_active=is_active,
        )
        user.set_password(password)
        return user

    @patch("api.routers.auth.AppUser")
    @patch("open_notebook.domain.base.ObjectModel.save", new_callable=AsyncMock)
    def test_login_success(self, mock_save, mock_user_cls):
        client = _make_client()
        user = self._mock_user()
        mock_user_cls.get_by_username = AsyncMock(return_value=user)

        response = client.post(
            "/api/auth/login",
            json={"username_or_email": "testuser", "password": "correct"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "testuser"
        assert "password_hash" not in data["user"]

    @patch("api.routers.auth.AppUser")
    def test_login_wrong_password(self, mock_user_cls):
        client = _make_client()
        user = self._mock_user(password="correct")
        mock_user_cls.get_by_username = AsyncMock(return_value=user)

        response = client.post(
            "/api/auth/login",
            json={"username_or_email": "testuser", "password": "wrong"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    @patch("api.routers.auth.AppUser")
    def test_login_inactive_user(self, mock_user_cls):
        client = _make_client()
        user = self._mock_user(is_active=False)
        mock_user_cls.get_by_username = AsyncMock(return_value=user)

        response = client.post(
            "/api/auth/login",
            json={"username_or_email": "testuser", "password": "correct"},
        )

        assert response.status_code == 403
        assert "disabled" in response.json()["detail"].lower()

    @patch("api.routers.auth.AppUser")
    def test_login_nonexistent_user(self, mock_user_cls):
        client = _make_client()
        mock_user_cls.get_by_username = AsyncMock(return_value=None)
        mock_user_cls.get_by_email = AsyncMock(return_value=None)

        response = client.post(
            "/api/auth/login",
            json={"username_or_email": "nobody", "password": "anything"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    @patch("api.routers.auth.AppUser")
    def test_login_error_messages_are_generic(self, mock_user_cls):
        """Wrong password and non-existent user return the same error message."""
        client = _make_client()

        # Non-existent user
        mock_user_cls.get_by_username = AsyncMock(return_value=None)
        mock_user_cls.get_by_email = AsyncMock(return_value=None)
        resp_no_user = client.post(
            "/api/auth/login",
            json={"username_or_email": "ghost", "password": "x"},
        )

        # Wrong password
        user = self._mock_user(password="right")
        mock_user_cls.get_by_username = AsyncMock(return_value=user)
        resp_wrong_pw = client.post(
            "/api/auth/login",
            json={"username_or_email": "testuser", "password": "wrong"},
        )

        assert resp_no_user.json()["detail"] == resp_wrong_pw.json()["detail"]


class TestIDORProtection:
    """Tests that user A cannot access user B's resources."""

    @patch("api.auth.AppUser")
    @patch("api.routers.notes.Note")
    def test_user_cannot_get_other_users_note(self, mock_note_cls, mock_auth_user_cls):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user_a = AppUser(
            id="app_user:userA",
            username="userA",
            email="a@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user_a)

        # Note belongs to user B
        mock_note = AsyncMock()
        mock_note.id = "note:123"
        mock_note.owner_id = "app_user:userB"
        mock_note_cls.get = AsyncMock(return_value=mock_note)

        token = create_access_token({"sub": "app_user:userA", "role": "user"})
        response = client.get("/api/notes/note:123", headers=_auth_header(token))

        assert response.status_code == 404

    @patch("api.auth.AppUser")
    @patch("api.routers.notes.Note")
    def test_user_cannot_delete_other_users_note(
        self, mock_note_cls, mock_auth_user_cls
    ):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user_a = AppUser(
            id="app_user:userA",
            username="userA",
            email="a@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user_a)

        mock_note = AsyncMock()
        mock_note.id = "note:123"
        mock_note.owner_id = "app_user:userB"
        mock_note_cls.get = AsyncMock(return_value=mock_note)

        token = create_access_token({"sub": "app_user:userA", "role": "user"})
        response = client.delete("/api/notes/note:123", headers=_auth_header(token))

        assert response.status_code == 404

    @patch("api.auth.AppUser")
    @patch("api.routers.notes.Note")
    def test_user_cannot_update_other_users_note(
        self, mock_note_cls, mock_auth_user_cls
    ):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user_a = AppUser(
            id="app_user:userA",
            username="userA",
            email="a@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user_a)

        mock_note = AsyncMock()
        mock_note.id = "note:123"
        mock_note.owner_id = "app_user:userB"
        mock_note_cls.get = AsyncMock(return_value=mock_note)

        token = create_access_token({"sub": "app_user:userA", "role": "user"})
        response = client.put(
            "/api/notes/note:123",
            json={"content": "hacked"},
            headers=_auth_header(token),
        )

        assert response.status_code == 404


class TestAdminGuard:
    """Tests that regular users cannot access admin-only endpoints."""

    @patch("api.auth.AppUser")
    def test_regular_user_cannot_create_notebook(self, mock_auth_user_cls):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user = AppUser(
            id="app_user:user1",
            username="regular",
            email="user@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user)

        token = create_access_token({"sub": "app_user:user1", "role": "user"})
        response = client.post(
            "/api/notebooks",
            json={"name": "Hacked Notebook"},
            headers=_auth_header(token),
        )

        assert response.status_code == 403

    @patch("api.auth.AppUser")
    def test_regular_user_cannot_list_admin_users(self, mock_auth_user_cls):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user = AppUser(
            id="app_user:user1",
            username="regular",
            email="user@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user)

        token = create_access_token({"sub": "app_user:user1", "role": "user"})
        response = client.get("/api/admin/users", headers=_auth_header(token))

        assert response.status_code == 403

    @patch("api.auth.AppUser")
    def test_regular_user_cannot_create_admin_user(self, mock_auth_user_cls):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        user = AppUser(
            id="app_user:user1",
            username="regular",
            email="user@test.com",
            role="user",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=user)

        token = create_access_token({"sub": "app_user:user1", "role": "user"})
        response = client.post(
            "/api/admin/users",
            json={
                "username": "evil",
                "email": "evil@test.com",
                "password": "hack",
                "role": "admin",
            },
            headers=_auth_header(token),
        )

        assert response.status_code == 403


class TestAdminDeleteProtection:
    """Tests that the last admin cannot be deleted."""

    @patch("api.auth.AppUser")
    @patch("api.routers.admin.AppUser")
    def test_cannot_delete_last_admin(self, mock_admin_user_cls, mock_auth_user_cls):
        client = _make_client()

        from open_notebook.domain.user import AppUser

        admin = AppUser(
            id="app_user:admin1",
            username="admin",
            email="admin@test.com",
            role="admin",
            is_active=True,
        )
        mock_auth_user_cls.get = AsyncMock(return_value=admin)
        mock_admin_user_cls.get = AsyncMock(return_value=admin)

        # Simulate only 1 admin exists
        from open_notebook.database.repository import repo_query

        with patch(
            "api.routers.admin.repo_query",
            new=AsyncMock(return_value=[{"count": 1}]),
        ):
            token = create_access_token({"sub": "app_user:admin1", "role": "admin"})
            response = client.delete(
                "/api/admin/users/app_user:admin1", headers=_auth_header(token)
            )

        assert response.status_code == 400
        assert "last admin" in response.json()["detail"].lower()


class TestBootstrapAdmin:
    """Tests for admin bootstrap on empty database."""

    @patch("open_notebook.database.repository.repo_query")
    def test_bootstrap_assigns_data_to_admin(self, mock_repo_query):
        """Verify _bootstrap_admin_data assigns ownerless records to admin."""
        mock_repo_query.return_value = []

        from api.main import _bootstrap_admin_data

        import asyncio

        asyncio.run(_bootstrap_admin_data("app_user:admin1"))

        assert mock_repo_query.call_count == 3
        calls = [c.args[0] for c in mock_repo_query.call_args_list]
        assert any("note" in c and "owner_id" in c for c in calls)
        assert any("chat_session" in c and "owner_id" in c for c in calls)
        assert any("notebook" in c and "created_by" in c for c in calls)

    def test_create_user_hashes_password(self):
        """Verify AppUser.create_user would hash the password (unit-level check)."""
        from open_notebook.domain.user import AppUser

        user = AppUser(username="test", email="t@t.com", role="admin")
        user.set_password("mypassword")
        assert user.password_hash is not None
        assert user.verify_password("mypassword")
