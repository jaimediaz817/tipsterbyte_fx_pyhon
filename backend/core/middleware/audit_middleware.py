"""
Middleware de auditoría para registrar automáticamente las requests HTTP.

Principios aplicados:
- Inversión de dependencias: Depende del servicio, no del modelo
- Separación de responsabilidades: Solo intercepta, no persiste
- Mínimo conocimiento: No conoce implementación interna
"""

import time
from typing import Callable, Optional
from uuid import uuid4

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.security.jwt_handler import JWTHandler


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra automáticamente todas las requests HTTP
    en la colección session_logs de MongoDB usando el servicio.

    Principios de arquitectura aplicados:
    - SRP: Solo intercepta requests, no persiste directamente
    - DIP: Depende de la abstracción (SessionLogService), no del modelo
    - Clean Architecture: Respeta las capas Middleware → Servicio → Repositorio → Modelo
    """

    def __init__(self, app, session_log_service: SessionLogService):
        """
        Inicializa el middleware con el servicio de session logs.

        Args:
            app: Aplicación FastAPI
            session_log_service: Servicio para registrar logs (inyección de dependencias)
        """
        super().__init__(app)
        self.session_log_service = session_log_service

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa la request y registra el log de auditoría.

        Args:
            request: Request de FastAPI
            call_next: Siguiente middleware o endpoint

        Returns:
            Response de la API
        """
        start_time = time.time()

        # Procesar la request
        response = await call_next(request)

        # Calcular tiempo de respuesta
        response_time = (time.time() - start_time) * 1000  # Convertir a milisegundos

        # Extraer user_id del JWT si está presente
        user_id = self._extract_user_id(request)

        # Solo registrar si hay un usuario autenticado
        if user_id:
            try:
                # Generar session_id único si no existe
                session_id = request.headers.get("X-Session-ID", str(uuid4()))

                # ✅ USAR EL SERVICIO (no el modelo directamente)
                await self.session_log_service.log_api_call(
                    user_id=user_id,
                    session_id=session_id,
                    ip_address=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", "unknown"),
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                )

                logger.debug(
                    f"✅ Audit log registrado: {request.method} {request.url.path} "
                    f"[{response.status_code}] - Usuario: {user_id}"
                )

            except Exception as e:
                # ✅ LOGGEAR ERROR (no ignorar silenciosamente)
                logger.error(
                    f"❌ Error al registrar audit log: {e} | "
                    f"Endpoint: {request.method} {request.url.path} | "
                    f"Usuario: {user_id}"
                )
                # No interrumpir la request si hay error en el logging
                pass

        return response

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        Extrae user_id del token JWT.

        Args:
            request: Request de FastAPI

        Returns:
            user_id si el token es válido, None en caso contrario
        """
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = JWTHandler.verify_token(token)
                if payload:
                    return payload.get("sub")
        except Exception as e:
            logger.debug(f"No se pudo extraer user_id del token: {e}")
        return None
