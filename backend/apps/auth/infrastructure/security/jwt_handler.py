"""
JWT Handler para autenticación y autorización
Maneja la creación, verificación y refresh de tokens JWT
"""

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from loguru import logger
from core.config import settings


class JWTHandler:
    """
    Handler para operaciones con JWT tokens

    Funcionalidades:
    - Crear access tokens (corto plazo)
    - Crear refresh tokens (largo plazo)
    - Verificar y decodificar tokens
    - Extraer información del usuario del token
    """

    # Configuración desde settings
    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = settings.JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    @staticmethod
    def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un access token JWT

        Args:
            data: Datos a incluir en el token (sub, username, roles, etc.)
            expires_delta: Tiempo de expiración personalizado (opcional)

        Returns:
            Token JWT codificado como string

        Example:
            token = JWTHandler.create_access_token({
                "sub": "123",
                "username": "john_doe",
                "roles": ["user", "admin"]
            })
        """
        to_encode = data.copy()

        # Calcular tiempo de expiración
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=JWTHandler.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Agregar claims estándar
        to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "access"})

        # Codificar token
        encoded_jwt = jwt.encode(
            to_encode, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM
        )

        logger.debug(
            f"✅ Access token creado para usuario: {data.get('username', 'unknown')}"
        )
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Crea un refresh token JWT (mayor duración)

        Args:
            data: Datos a incluir en el token (mínimo: sub)

        Returns:
            Refresh token JWT codificado como string
        """
        to_encode = data.copy()

        # Calcular tiempo de expiración (más largo)
        expire = datetime.now(UTC) + timedelta(
            days=JWTHandler.REFRESH_TOKEN_EXPIRE_DAYS
        )

        # Agregar claims estándar
        to_encode.update({"exp": expire, "iat": datetime.now(UTC), "type": "refresh"})

        # Codificar token
        encoded_jwt = jwt.encode(
            to_encode, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM
        )

        logger.debug(
            f"✅ Refresh token creado para usuario: {data.get('sub', 'unknown')}"
        )
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT

        Args:
            token: Token JWT a verificar

        Returns:
            Payload del token si es válido, None si es inválido o expirado

        Example:
            payload = JWTHandler.verify_token(token)
            if payload:
                user_id = payload.get("sub")
        """
        try:
            payload = jwt.decode(
                token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM]
            )
            return payload

        except JWTError as e:
            logger.warning(f"⚠️ Error al verificar token: {e}")
            return None

    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]:
        """
        Extrae el ID del usuario desde un token JWT

        Args:
            token: Token JWT

        Returns:
            ID del usuario si el token es válido, None en caso contrario
        """
        payload = JWTHandler.verify_token(token)
        if payload:
            user_id = payload.get("sub")
            return int(user_id) if user_id else None
        return None

    @staticmethod
    def get_username_from_token(token: str) -> Optional[str]:
        """
        Extrae el username desde un token JWT

        Args:
            token: Token JWT

        Returns:
            Username si el token es válido, None en caso contrario
        """
        payload = JWTHandler.verify_token(token)
        if payload:
            return payload.get("username")
        return None

    @staticmethod
    def get_roles_from_token(token: str) -> list:
        """
        Extrae los roles del usuario desde un token JWT

        Args:
            token: Token JWT

        Returns:
            Lista de roles si el token es válido, lista vacía en caso contrario
        """
        payload = JWTHandler.verify_token(token)
        if payload:
            return payload.get("roles", [])
        return []

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Verifica si un token ha expirado

        Args:
            token: Token JWT

        Returns:
            True si el token ha expirado, False en caso contrario
        """
        payload = JWTHandler.verify_token(token)
        if not payload:
            return True

        exp = payload.get("exp")
        if not exp:
            return True

        return datetime.now(UTC) > datetime.fromtimestamp(exp, UTC)

    @staticmethod
    def get_token_type(token: str) -> Optional[str]:
        """
        Obtiene el tipo de token (access o refresh)

        Args:
            token: Token JWT

        Returns:
            Tipo de token ('access' o 'refresh'), None si es inválido
        """
        payload = JWTHandler.verify_token(token)
        if payload:
            return payload.get("type")
        return None
