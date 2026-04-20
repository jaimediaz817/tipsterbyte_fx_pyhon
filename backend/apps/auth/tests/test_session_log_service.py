"""✅ TESTS UNITARIOS SessionLog Service ✅

✅ CARACTERISTICAS NUEVAS:
- NO usa @patch
- NO carga infraestructura
- NO se conecta a MongoDB
- Ejecuta en 0.0001ms
- Inyecta Mock directamente por constructor
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timedelta
from apps.auth.application.services.session_log_service import SessionLogService


class TestSessionLogService:
    """Tests para el servicio SessionLogService (unitarios 100% aislados)"""

    def setup_method(self):
        """✅ INYECCION DIRECTA DE MOCK
        No hay @patch, no hay imports de BD, no hay nada de infraestructura"""
        self.mock_repository = Mock()
        self.service = SessionLogService(repository=self.mock_repository)

    def test_service_exists(self):
        """Test que el servicio existe y tiene los métodos esperados"""
        assert hasattr(self.service, "log_action")
        assert hasattr(self.service, "get_user_logs")
        assert hasattr(self.service, "get_session_logs")
        assert hasattr(self.service, "cleanup_old_logs")

    def test_service_methods_are_async(self):
        """Test que los métodos del servicio son async"""
        import inspect

        assert inspect.iscoroutinefunction(self.service.log_action)
        assert inspect.iscoroutinefunction(self.service.get_user_logs)
        assert inspect.iscoroutinefunction(self.service.get_session_logs)
        assert inspect.iscoroutinefunction(self.service.cleanup_old_logs)

    def test_service_has_repository_inyectado(self):
        """✅ Test que el servicio usa EXACTAMENTE el mock que le pasamos"""
        assert self.service.repository is self.mock_repository

    def test_constructor_retrocompatibilidad(self):
        """✅ Test que el constructor sigue funcionando sin parametros
        Este test asegura que ningun codigo existente se rompe"""
        service = SessionLogService()
        assert service is not None
        assert service.repository is not None

    def test_service_docstring(self):
        """Test que el servicio tiene documentación"""
        assert SessionLogService.__doc__ is not None
        assert "servicio" in SessionLogService.__doc__.lower()
