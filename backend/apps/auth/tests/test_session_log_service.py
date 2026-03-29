"""Tests para SessionLog Service (sin conexión a MongoDB)"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.repositories.session_log_repository import (
    SessionLogRepository,
)


class TestSessionLogService:
    """Tests para el servicio SessionLogService (unitarios, sin DB)"""

    def test_service_exists(self):
        """Test que el servicio existe y tiene los métodos esperados"""
        repo = SessionLogRepository()
        service = SessionLogService(repo)

        assert hasattr(service, "log_action")
        assert hasattr(service, "get_user_logs")
        assert hasattr(service, "get_session_logs")
        assert hasattr(service, "cleanup_old_logs")

    def test_service_methods_are_async(self):
        """Test que los métodos del servicio son async"""
        import inspect

        repo = SessionLogRepository()
        service = SessionLogService(repo)

        assert inspect.iscoroutinefunction(service.log_action)
        assert inspect.iscoroutinefunction(service.get_user_logs)
        assert inspect.iscoroutinefunction(service.get_session_logs)
        assert inspect.iscoroutinefunction(service.cleanup_old_logs)

    def test_service_has_repository(self):
        """Test que el servicio tiene repositorio inyectado"""
        repo = SessionLogRepository()
        service = SessionLogService(repo)

        assert service.repository is not None
        assert isinstance(service.repository, SessionLogRepository)

    def test_service_docstring(self):
        """Test que el servicio tiene documentación"""
        assert SessionLogService.__doc__ is not None
        assert "servicio" in SessionLogService.__doc__.lower()
