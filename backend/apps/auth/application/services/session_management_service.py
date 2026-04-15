"""
Servicio de Gestión de Sesiones.
✅ SRP: Única responsabilidad: Gestionar cierre de sesiones.
"""

from loguru import logger

from apps.auth.application.services.session_log_service import SessionLogService


class SessionManagementService:
    """
    Servicio exclusivo para la gestión de sesiones de usuario.

    ✅ Single Responsibility Principle
    ✅ Única razón para cambiar: Cuando cambie la logica de cierre de sesion
    """

    def __init__(self, session_log_service: SessionLogService):
        self.session_log_service = session_log_service

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
