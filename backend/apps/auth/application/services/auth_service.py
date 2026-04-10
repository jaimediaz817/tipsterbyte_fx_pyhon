"""
Servicio de autenticación.
Gestiona registro, login, logout y gestión de tokens JWT.
"""

from typing import Optional, cast
from loguru import logger

from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.infrastructure.security.password_handler import PasswordHandler
from apps.auth.infrastructure.security.jwt_handler import JWTHandler
from apps.auth.application.services.session_log_service import SessionLogService


class AuthService:
    """
    Servicio para gestionar autenticación de usuarios.

    Principios aplicados:
    - SRP: Solo lógica de autenticación
    - DIP: Depende de abstracciones (repositorio, servicios)
    - Clean Architecture: Capa de aplicación
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
        # user.id es int (Column[int] de SQLAlchemy se resuelve a int en runtime)
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

    async def logout(self, user_id: int) -> dict:
        """
        Cierra sesión de un usuario.

        Args:
            user_id: ID del usuario

        Returns:
            Mensaje de confirmación
        """
        # Log de logout
        await self.session_log_service.log_action(
            user_id=user_id,
            session_id=f"logout_{user_id}",
            action="logout",
            ip_address="unknown",
            user_agent="unknown",
            endpoint="/api/v1/auth/logout",
            method="POST",
            status_code=200,
            response_time_ms=0,
        )

        logger.info(f"✅ Logout exitoso para usuario ID: {user_id}")
        return {"message": "Sesión cerrada exitosamente"}

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

        # Verificar si está activo
        if not user.is_active:  # type: ignore[truthy-bool]
            logger.warning(f"⚠️ Usuario inactivo: {user.username}")
            raise ValueError("Usuario inactivo")

        logger.debug(f"✅ Usuario actual obtenido: {user.username}")
        return user
