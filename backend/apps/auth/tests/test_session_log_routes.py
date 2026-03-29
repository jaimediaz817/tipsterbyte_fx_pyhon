"""Tests para las rutas de bitácora de sesión"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


class TestSessionLogRoutes:
    """Tests para las rutas de SessionLog"""

    def test_get_user_logs_endpoint_exists(self):
        """Test que el endpoint de obtener logs de usuario existe"""
        from apps.auth.api.v1.routes.session_log_routes import router
        from fastapi.routing import APIRoute

        routes = [route.path for route in router.routes if isinstance(route, APIRoute)]
        assert "/users/{user_id}/logs" in routes

    def test_get_session_logs_endpoint_exists(self):
        """Test que el endpoint de obtener logs por sesión existe"""
        from apps.auth.api.v1.routes.session_log_routes import router
        from fastapi.routing import APIRoute

        routes = [route.path for route in router.routes if isinstance(route, APIRoute)]
        assert "/users/sessions/{session_id}" in routes

    def test_router_has_correct_prefix(self):
        """Test que el router tiene el prefijo correcto"""
        from apps.auth.api.v1.routes.session_log_routes import router

        assert router.prefix == "/users"

    def test_router_has_correct_tags(self):
        """Test que el router tiene los tags correctos"""
        from apps.auth.api.v1.routes.session_log_routes import router

        assert "Session Logs" in router.tags

    def test_routes_have_correct_methods(self):
        """Test que las rutas tienen los métodos HTTP correctos"""
        from apps.auth.api.v1.routes.session_log_routes import router
        from fastapi.routing import APIRoute

        for route in router.routes:
            if isinstance(route, APIRoute):
                if route.path == "/users/{user_id}/logs":
                    assert "GET" in route.methods
                elif route.path == "/users/sessions/{session_id}":
                    assert "GET" in route.methods
