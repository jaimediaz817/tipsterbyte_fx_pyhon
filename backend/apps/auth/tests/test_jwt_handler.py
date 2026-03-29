"""Tests para JWT Handler"""

import pytest
from apps.auth.infrastructure.security.jwt_handler import JWTHandler


class TestJWTHandler:
    """Tests para el handler de JWT"""

    def test_create_access_token(self):
        """Test crear access token"""
        data = {"sub": "123", "username": "john_doe", "roles": ["user"]}
        token = JWTHandler.create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        """Test crear refresh token"""
        data = {"sub": "123"}
        token = JWTHandler.create_refresh_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self):
        """Test verificar token válido"""
        data = {"sub": "123", "username": "john_doe", "roles": ["user"]}
        token = JWTHandler.create_access_token(data)
        payload = JWTHandler.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "123"
        assert payload["type"] == "access"

    def test_verify_token_invalid(self):
        """Test verificar token inválido"""
        payload = JWTHandler.verify_token("invalid-token-12345")
        assert payload is None

    def test_get_user_id_from_token(self):
        """Test extraer user_id del token"""
        data = {"sub": "456", "username": "jane_doe"}
        token = JWTHandler.create_access_token(data)
        user_id = JWTHandler.get_user_id_from_token(token)
        assert user_id == 456

    def test_get_username_from_token(self):
        """Test extraer username del token"""
        data = {"sub": "789", "username": "test_user"}
        token = JWTHandler.create_access_token(data)
        username = JWTHandler.get_username_from_token(token)
        assert username == "test_user"

    def test_get_roles_from_token(self):
        """Test extraer roles del token"""
        data = {"sub": "1", "roles": ["admin", "user"]}
        token = JWTHandler.create_access_token(data)
        roles = JWTHandler.get_roles_from_token(token)
        assert roles == ["admin", "user"]

    def test_get_token_type(self):
        """Test obtener tipo de token"""
        data = {"sub": "1"}
        access_token = JWTHandler.create_access_token(data)
        refresh_token = JWTHandler.create_refresh_token(data)
        assert JWTHandler.get_token_type(access_token) == "access"
        assert JWTHandler.get_token_type(refresh_token) == "refresh"
