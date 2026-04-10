"""
Rutas de autenticación.
Endpoints para registro, login, logout y gestión de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.application.services.auth_service import AuthService
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.repositories.session_log_repository import (
    SessionLogRepository,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Security scheme para JWT
security = HTTPBearer()


def get_auth_service() -> AuthService:
    """Dependency para obtener instancia de AuthService."""
    user_repo = UserRepository()
    session_log_repo = SessionLogRepository()
    session_log_service = SessionLogService(session_log_repo)
    return AuthService(user_repo, session_log_service)


@router.post(
    "/register",
    response_model=TokenDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo usuario",
    description="Crea una nueva cuenta de usuario y retorna un token JWT",
)
async def register(
    dto: RegisterDTO,
    service: AuthService = Depends(get_auth_service),
):
    """
    Registra un nuevo usuario en el sistema.

    - **username**: Nombre de usuario único (3-50 caracteres)
    - **email**: Email válido del usuario
    - **password**: Contraseña segura (mínimo 8 caracteres, mayúsculas, minúsculas, números, especiales)

    Returns:
        TokenDTO con el access token generado
    """
    try:
        return await service.register(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=TokenDTO,
    summary="Iniciar sesión",
    description="Autentica un usuario y retorna un token JWT",
)
async def login(
    dto: LoginDTO,
    service: AuthService = Depends(get_auth_service),
):
    """
    Inicia sesión con credenciales de usuario.

    - **username**: Nombre de usuario o email
    - **password**: Contraseña del usuario

    Returns:
        TokenDTO con el access token generado
    """
    try:
        return await service.login(dto)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/logout",
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario actual",
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service),
):
    """
    Cierra la sesión del usuario actual.

    Requiere token JWT válido en el header Authorization.

    Returns:
        Mensaje de confirmación
    """
    try:
        # Obtener usuario actual desde el token
        user = await service.get_current_user(credentials.credentials)

        # Realizar logout
        result = await service.logout(getattr(user, "id"))

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/me",
    summary="Obtener usuario actual",
    description="Retorna la información del usuario autenticado",
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service),
):
    """
    Obtiene la información del usuario actual autenticado.

    Requiere token JWT válido en el header Authorization.

    Returns:
        Información del usuario actual
    """
    try:
        user = await service.get_current_user(credentials.credentials)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": (
                user.created_at.isoformat() if user.created_at is not None else None
            ),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get(
    "/ping",
    summary="Health check de autenticación",
    description="Verifica que el servicio de autenticación está funcionando",
)
async def auth_ping():
    """
    Health check del subsistema de autenticación.

    Returns:
        Estado del servicio
    """
    return {"ok": True, "service": "auth", "message": "pong"}
