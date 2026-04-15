"""
✅ Servicio de Autenticación - FACHADA RETROCOMPATIBLE
⚠️  ESTA CLASE AHORA ES SOLO UNA FACHADA
✅ No contiene ninguna logica de negocio propia
✅ Delega 100% a servicios individuales con SRP
✅ 100% Retrocompatible - Ningun cambio en API publica
✅ Mantiene exactamente la misma firma que el original
"""

from typing import Optional

from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.application.services.session_log_service import SessionLogService

# Servicios individuales con SRP aplicado
from apps.auth.application.services.user_registration_service import (
    UserRegistrationService,
)
from apps.auth.application.services.user_authentication_service import (
    UserAuthenticationService,
)
from apps.auth.application.services.session_management_service import (
    SessionManagementService,
)
from apps.auth.application.services.token_validation_service import (
    TokenValidationService,
)


class AuthService:
    """
    ✅ FACHADA RETROCOMPATIBLE

    Esta clase permanece EXACTAMENTE IGUAL para el exterior.
    Ningun cliente notara ningun cambio.
    Toda la logica esta delegada a servicios con responsabilidad unica.

    ✅ Single Responsibility Principle: Solo es una fachada
    ✅ 100% Retrocompatible
    ✅ Ningun codigo existente se rompe
    """

    def __init__(
        self,
        user_repository: UserRepository,
        session_log_service: SessionLogService,
    ):
        # Inicializar servicios individuales
        self._registration_service = UserRegistrationService(
            user_repository, session_log_service
        )
        self._authentication_service = UserAuthenticationService(
            user_repository, session_log_service
        )
        self._session_service = SessionManagementService(session_log_service)
        self._token_service = TokenValidationService(user_repository)

    async def register(self, dto: RegisterDTO) -> TokenDTO:
        """
        Registra un nuevo usuario en el sistema.

        ⚠️ DELEGADO A: UserRegistrationService
        """
        return await self._registration_service.register(dto)

    async def login(self, dto: LoginDTO) -> TokenDTO:
        """
        Inicia sesión de un usuario.

        ⚠️ DELEGADO A: UserAuthenticationService
        """
        return await self._authentication_service.login(dto)

    async def logout(self, user_id: int) -> dict:
        """
        Cierra sesión de un usuario.

        ⚠️ DELEGADO A: SessionManagementService
        """
        return await self._session_service.logout(user_id)

    async def get_current_user(self, token: str) -> User:
        """
        Obtiene el usuario actual a partir de un token JWT.

        ⚠️ DELEGADO A: TokenValidationService
        """
        return await self._token_service.get_current_user(token)
