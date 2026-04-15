"""
Servicio de Registro de Usuarios.
✅ SRP: Única responsabilidad: Registrar nuevos usuarios en el sistema.
"""

from typing import cast
from loguru import logger

from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.infrastructure.security.password_handler import PasswordHandler
from apps.auth.infrastructure.security.jwt_handler import JWTHandler
from apps.auth.application.services.session_log_service import SessionLogService


class UserRegistrationService:
    """
    Servicio exclusivo para la lógica de registro de usuarios.

    ✅ Single Responsibility Principle
    ✅ Única razón para cambiar: Cuando cambie la logica de registro
    """

    def __init__(
        self,
        user_repository: UserRepository,
        session_log_service: SessionLogService,
    ):
        self.user_repository = user_repository
        self.session_log_service = session_log_service

    async def register(self, dto: RegisterDTO) -> TokenDTO:
        """
        Registra un nuevo usuario en el sistema.

        Args:
            dto: Datos del usuario a registrar

        Returns:
            TokenDTO con el access token generado

        Raises:
            ValueError: Si el email o username ya existen
        """
        # Verificar si email ya existe
        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user:
            logger.warning(f"⚠️ Intento de registro con email duplicado: {dto.email}")
            raise ValueError("El email ya está registrado")

        # Verificar si username ya existe
        existing_username = await self.user_repository.get_by_username(dto.username)
        if existing_username:
            logger.warning(
                f"⚠️ Intento de registro con username duplicado: {dto.username}"
            )
            raise ValueError("El nombre de usuario ya existe")

        # Validar fortaleza de contraseña
        is_strong, errors = PasswordHandler.is_strong_password(dto.password)
        if not is_strong:
            logger.warning(f"⚠️ Contraseña débil para usuario: {dto.username}")
            raise ValueError(f"Contraseña débil: {', '.join(errors)}")

        # Hashear contraseña
        hashed_password = PasswordHandler.hash_password(dto.password)

        # Crear usuario
        user = User(
            username=dto.username,
            email=dto.email,
            hashed_password=hashed_password,
        )
        created_user = await self.user_repository.create(user)
        created_user = cast(User, created_user)

        # Generar tokens JWT
        access_token = JWTHandler.create_access_token(
            data={"sub": str(created_user.id), "username": created_user.username}
        )
        refresh_token = JWTHandler.create_refresh_token(
            data={"sub": str(created_user.id)}
        )

        # Log de registro
        # created_user.id es int después de la persistencia en DB
        await self.session_log_service.log_action(
            user_id=created_user.id,  # type: ignore[arg-type]
            session_id=f"register_{created_user.id}",
            action="register",
            ip_address="unknown",
            user_agent="unknown",
            endpoint="/api/v1/auth/register",
            method="POST",
            status_code=201,
            response_time_ms=0,
        )

        logger.info(f"✅ Usuario registrado exitosamente: {dto.username}")
        return TokenDTO(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
