"""Tests para SessionLog Repository (sin conexión a MongoDB)"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from apps.auth.infrastructure.repositories.session_log_repository import (
    SessionLogRepository,
)


class TestSessionLogRepository:
    """Tests para el repositorio SessionLogRepository (unitarios, sin DB)"""

    def test_repository_exists(self):
        """Test que el repositorio existe y tiene los métodos esperados"""
        repo = SessionLogRepository()

        assert hasattr(repo, "save")
        assert hasattr(repo, "get_by_user")
        assert hasattr(repo, "count_by_user")
        assert hasattr(repo, "get_by_session_id")
        assert hasattr(repo, "delete_old_logs")

    def test_repository_methods_are_async(self):
        """Test que los métodos del repositorio son async"""
        import inspect

        repo = SessionLogRepository()

        assert inspect.iscoroutinefunction(repo.save)
        assert inspect.iscoroutinefunction(repo.get_by_user)
        assert inspect.iscoroutinefunction(repo.count_by_user)
        assert inspect.iscoroutinefunction(repo.get_by_session_id)
        assert inspect.iscoroutinefunction(repo.delete_old_logs)

    def test_repository_docstring(self):
        """Test que el repositorio tiene documentación"""
        assert SessionLogRepository.__doc__ is not None
        assert "repositorio" in SessionLogRepository.__doc__.lower()
