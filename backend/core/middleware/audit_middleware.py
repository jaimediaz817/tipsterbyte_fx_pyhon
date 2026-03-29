"""
Middleware de auditoría para registrar automáticamente las requests HTTP.
"""

import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog
from apps.auth.infrastructure.security.jwt_handler import JWTHandler


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra automáticamente todas las requests HTTP
    en la colección session_logs de MongoDB.
    """

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
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = JWTHandler.verify_token(token)
            if payload:
                user_id = payload.get("sub")

        # Solo registrar si hay un usuario autenticado
        if user_id:
            try:
                # Generar session_id único si no existe
                session_id = request.headers.get("X-Session-ID", str(uuid4()))

                # Crear log de auditoría
                log = SessionLog(
                    user_id=user_id,
                    session_id=session_id,
                    action="api_call",
                    ip_address=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", "unknown"),
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                )

                # Guardar en MongoDB de forma asíncrona
                await log.insert()

            except Exception as e:
                # No fallar la request si hay error en el logging
                # Solo registrar el error (en producción se usaría logger)
                pass

        return response
