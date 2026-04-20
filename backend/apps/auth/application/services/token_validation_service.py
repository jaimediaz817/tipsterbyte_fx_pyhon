"""
Servicio de Validación de Tokens.
✅ SRP: Única responsabilidad: Validar token JWT y obtener usuario.
✅ DIP: Depende de abstracciones, no de implementaciones concretas
"""

from typing import cast, Protocol, Awaitable
from loguru import logger

from apps.auth.infrastructure.security.jwt_handler import JWTHandler


class IUserEntity(Protocol):
    """Interfaz para entidad Usuario (solo atributos que usamos aqui)"""

    @property
    def is_active(self) -> bool: ...
    @property
    def username(self) -> str: ...


class IUserRepository(Protocol):
    """Interfaz para repositorio de usuarios"""

    async def get_by_id(self, user_id: int) -> IUserEntity | None: ...


class TokenValidationService:
    """
    Servicio exclusivo para la validación de tokens JWT.

    ✅ Single Responsibility Principle
    ✅ Dependency Inversion Principle
    ✅ Única razón para cambiar: Cuando cambie la logica de validacion de tokens
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def get_current_user(self, token: str) -> IUserEntity:
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

        # Verificar si está activo
        if not user.is_active:
            logger.warning(f"⚠️ Usuario inactivo: {user.username}")
            raise ValueError("Usuario inactivo")

        logger.debug(f"✅ Usuario actual obtenido: {user.username}")
        return user
