"""
Excepciones personalizadas para errores de Session Logs.

Este módulo contiene excepciones específicas para operaciones de session logs,
proporcionando un manejo granular de errores sin interrumpir el servicio.

Categorías:
- SessionLogException: Excepción base para errores de session logs
- SessionLogWriteException: Error al escribir un session log
- SessionLogReadException: Error al leer session logs
"""

from typing import Optional
from core.exceptions.base import TipsterByteException


class SessionLogException(TipsterByteException):
    """
    Excepción base para errores de session logs.

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
    """

    def __init__(
        self,
        message: str,
        error_code: str = "SESSION_LOG_ERROR",
        details: Optional[str] = None,
    ):
        super().__init__(message, error_code)
        self.details = details


class SessionLogWriteException(SessionLogException):
    """
    Error al escribir un session log.

    Esta excepción se lanza cuando:
    - Falla la inserción de un session log en MongoDB
    - Error de conexión a MongoDB
    - Error de validación del log

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
        user_id: ID del usuario afectado (opcional)
        session_id: ID de la sesión afectada (opcional)
    """

    def __init__(
        self,
        message: str = "Error al escribir session log",
        error_code: str = "SESSION_LOG_WRITE_ERROR",
        details: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        super().__init__(message, error_code, details)
        self.user_id = user_id
        self.session_id = session_id


class SessionLogReadException(SessionLogException):
    """
    Error al leer session logs.

    Esta excepción se lanza cuando:
    - Falla la consulta de session logs
    - Error de conexión a MongoDB
    - Timeout de consulta

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
        user_id: ID del usuario afectado (opcional)
    """

    def __init__(
        self,
        message: str = "Error al leer session logs",
        error_code: str = "SESSION_LOG_READ_ERROR",
        details: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        super().__init__(message, error_code, details)
        self.user_id = user_id
