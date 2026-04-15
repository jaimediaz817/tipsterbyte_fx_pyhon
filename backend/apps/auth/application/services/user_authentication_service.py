"""
Servicio de Autenticación de Usuarios.
✅ SRP: Única responsabilidad: Validar credenciales e iniciar sesión.
"""

from typing import cast
from loguru import logger

from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.infrastructure.security.password_handler import PasswordHandler
from apps.auth.infrastructure.security.jwt_handler import JWTHandler
from apps.auth.application.services.session_log_service import SessionLogService


class UserAuthenticationService:
    """
    Servicio exclusivo para la lógica de autenticación y login.

    ✅ Single Responsibility Principle
    ✅ Única razón para cambiar: Cuando cambie la logica de autenticación
    """

    def __init__(
        self,
        user_repository: UserRepository,
        session_log_service: SessionLogService,
    ):
        self.user_repository = user_repository
        self.session_log_service = session_log_service

    async def login(self, dto: LoginDTO) -> TokenDTO:
        """
        Inicia sesión de un usuario.

        Args:
            dto: Credenciales de login (username/email y password)

        Returns:
            TokenDTO con el access token generado

        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Buscar usuario por username o email
        user = await self.user_repository.get_by_username(dto.username)
        if not user:
            user = await self.user_repository.get_by_email(dto.username)

        if not user:
            logger.warning(f"⚠️ Intento de login con credenciales inválidas")
            raise ValueError("Credenciales inválidas")

        user = cast(User, user)

        # Verificar si el usuario está activo
        if not user.is_active:  # type: ignore[truthy-bool]
            logger.warning(f"⚠️ Intento de login de usuario inactivo: {user.username}")
            raise ValueError("Usuario inactivo")

        # Verificar contraseña
        if not PasswordHandler.verify_password(dto.password, user.hashed_password):  # type: ignore[arg-type]
            logger.warning(
                f"⚠️ Intento de login con contraseña incorrecta: {user.username}"
            )
            raise ValueError("Credenciales inválidas")

        # Verificar si necesita re-hash de contraseña
        if PasswordHandler.needs_rehash(user.hashed_password):  # type: ignore[arg-type]
            logger.info(f"🔄 Re-hasheando contraseña para usuario: {user.username}")
            user.hashed_password = PasswordHandler.hash_password(dto.password)  # type: ignore[assignment]
            await self.user_repository.update(user)

        # Generar tokens JWT
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = JWTHandler.create_refresh_token(data={"sub": str(user.id)})

        # Log de login
        await self.session_log_service.log_action(
            user_id=user.id,  # type: ignore[arg-type]
            session_id=f"login_{user.id}",
            action="login",
            ip_address="unknown",
            user_agent="unknown",
            endpoint="/api/v1/auth/login",
            method="POST",
            status_code=200,
            response_time_ms=0,
        )

        logger.info(f"✅ Login exitoso: {user.username}")
        return TokenDTO(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
