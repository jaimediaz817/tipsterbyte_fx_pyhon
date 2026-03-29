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
        middleware = AuditMiddleware(app=MagicMock())
        assert hasattr(middleware, "dispatch")

    def test_middleware_inherits_base_http_middleware(self):
        """Test que el middleware hereda de BaseHTTPMiddleware"""
        from starlette.middleware.base import BaseHTTPMiddleware

        assert issubclass(AuditMiddleware, BaseHTTPMiddleware)
