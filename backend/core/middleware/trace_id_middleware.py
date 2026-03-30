"""
Middleware para generar y propagar Trace IDs en cada request.
Genera un identificador único de traza para correlacionar logs y requests.
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from contextvars import ContextVar
from loguru import logger

# Context variable para almacenar el trace_id durante la ejecución del request
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    """Obtiene el trace_id actual del contexto."""
    return trace_id_var.get()


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware que genera un Trace ID único para cada request HTTP.

    El Trace ID se almacena en:
    - Context variable para acceso en toda la aplicación
    - Header de respuesta X-Trace-ID para el cliente
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generar o extraer trace_id del header entrante
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))

        # Almacenar en context variable
        trace_id_var.set(trace_id)

        # Agregar trace_id al contexto del request para acceso fácil
        request.state.trace_id = trace_id

        # Log con trace_id
        logger.bind(trace_id=trace_id).debug(
            f"Request: {request.method} {request.url.path}"
        )

        # Procesar request
        response = await call_next(request)

        # Agregar trace_id al header de respuesta
        response.headers["X-Trace-ID"] = trace_id

        return response
