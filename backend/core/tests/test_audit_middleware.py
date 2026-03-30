"""Tests para el middleware de auditoría"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, Response
from core.middleware.audit_middleware import AuditMiddleware


class TestAuditMiddleware:
    """Tests para AuditMiddleware"""

    def test_middleware_exists(self):
        """Test que el middleware existe"""
        assert AuditMiddleware is not None

    def test_middleware_has_dispatch_method(self):
        """Test que el middleware tiene el método dispatch"""
        mock_service = MagicMock()
        middleware = AuditMiddleware(app=MagicMock(), session_log_service=mock_service)
        assert hasattr(middleware, "dispatch")

    def test_middleware_inherits_base_http_middleware(self):
        """Test que el middleware hereda de BaseHTTPMiddleware"""
        from starlette.middleware.base import BaseHTTPMiddleware

        assert issubclass(AuditMiddleware, BaseHTTPMiddleware)

    def test_middleware_receives_session_log_service(self):
        """Test que el middleware recibe el servicio de session logs"""
        mock_service = MagicMock()
        middleware = AuditMiddleware(app=MagicMock(), session_log_service=mock_service)
        assert middleware.session_log_service == mock_service

    def test_middleware_has_extract_user_id_method(self):
        """Test que el middleware tiene el método _extract_user_id"""
        mock_service = MagicMock()
        middleware = AuditMiddleware(app=MagicMock(), session_log_service=mock_service)
        assert hasattr(middleware, "_extract_user_id")

    @pytest.mark.asyncio
    async def test_dispatch_calls_session_log_service(self):
        """Test que dispatch llama al servicio de session logs"""
        mock_service = AsyncMock()
        mock_service.log_api_call = AsyncMock()

        middleware = AuditMiddleware(app=MagicMock(), session_log_service=mock_service)

        # Mock del request
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/v1/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {
            "Authorization": "Bearer test_token",
            "user-agent": "test-agent",
        }

        # Mock del response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        # Mock de call_next
        async def mock_call_next(request):
            return mock_response

        # Mock de JWTHandler.verify_token
        with patch(
            "core.middleware.audit_middleware.JWTHandler.verify_token"
        ) as mock_verify:
            mock_verify.return_value = {"sub": "user123"}

            # Ejecutar dispatch
            response = await middleware.dispatch(mock_request, mock_call_next)

            # Verificar que se llamó al servicio
            assert mock_service.log_api_call.called
            assert response == mock_response

    @pytest.mark.asyncio
    async def test_dispatch_does_not_call_service_without_user(self):
        """Test que dispatch NO llama al servicio si no hay usuario autenticado"""
        mock_service = AsyncMock()
        mock_service.log_api_call = AsyncMock()

        middleware = AuditMiddleware(app=MagicMock(), session_log_service=mock_service)

        # Mock del request sin Authorization header
        mock_request = MagicMock(spec=Request)
        mock_request.url.path = "/api/v1/test"
        mock_request.method = "GET"
        mock_request.client.host = "127.0.0.1"
        mock_request.headers = {"user-agent": "test-agent"}

        # Mock del response
        mock_response = MagicMock(spec=Response)
        mock_response.status_code = 200

        # Mock de call_next
        async def mock_call_next(request):
            return mock_response

        # Ejecutar dispatch
        response = await middleware.dispatch(mock_request, mock_call_next)

        # Verificar que NO se llamó al servicio
        assert not mock_service.log_api_call.called
        assert response == mock_response
