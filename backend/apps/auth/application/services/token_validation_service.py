"""
Servicio de Validación de Tokens.
✅ SRP: Única responsabilidad: Validar token JWT y obtener usuario.
"""

from typing import cast
from loguru import logger

from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.infrastructure.security.jwt_handler import JWTHandler


class TokenValidationService:
    """
    Servicio exclusivo para la validación de tokens JWT.

    ✅ Single Responsibility Principle
    ✅ Única razón para cambiar: Cuando cambie la logica de validacion de tokens
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_current_user(self, token: str) -> User:
        """
        Obtiene el usuario actual a partir de un token JWT.

        Args:
            token: Token JWT

        Returns:
            Usuario actual

        Raises:
            ValueError: Si el token es inválido o el usuario no existe
        """
        # Verificar token
        payload = JWTHandler.verify_token(token)
        if not payload:
            logger.warning("⚠️ Token JWT inválido")
            raise ValueError("Token inválido")

        # Obtener user_id del payload
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("⚠️ Token JWT sin user_id")
            raise ValueError("Token inválido")

        # Buscar usuario
        user = await self.user_repository.get_by_id(int(user_id))
        if not user:
            logger.warning(f"⚠️ Usuario no encontrado para token: {user_id}")
            raise ValueError("Usuario no encontrado")

        user = cast(User, user)

        # Verificar si está activo
        if not user.is_active:  # type: ignore[truthy-bool]
            logger.warning(f"⚠️ Usuario inactivo: {user.username}")
            raise ValueError("Usuario inactivo")

        logger.debug(f"✅ Usuario actual obtenido: {user.username}")
        return user
