"""
Módulo de excepciones personalizadas para TipsterByte FX.

Este módulo contiene todas las excepciones personalizadas del proyecto,
organizadas por categoría para facilitar el debugging y manejo de errores.

Categorías:
- Base: Excepción base del proyecto
- Process: Errores relacionados con procesos
- Fuente: Errores relacionados con fuentes y detalles
- Robot: Errores relacionados con robots de extracción
- Concurrency: Errores relacionados con concurrencia
"""

from core.exceptions.base import TipsterByteException
from core.exceptions.database_exceptions import (
    DatabaseException,
    MongoDBException,
    MongoDBConnectionException,
    MongoDBWriteException,
    MongoDBReadException,
)
from core.exceptions.session_log_exceptions import (
    SessionLogException,
    SessionLogWriteException,
    SessionLogReadException,
)
from core.exceptions.process_exceptions import (
    ProcessException,
    ProcessNotFoundException,
    ProcessInactiveException,
    ProcessRunCreationException,
    NoActiveJobsException,
)
from core.exceptions.fuente_exceptions import (
    FuenteException,
    FuenteNotFoundException,
    FuenteInactiveException,
    DetalleInactiveException,
)
from core.exceptions.robot_exceptions import (
    RobotException,
    RobotNotFoundException,
    ScrapingException,
    ScrapingTimeoutException,
    ScrapingParsingException,
)
from core.exceptions.concurrency_exceptions import (
    ConcurrencyException,
    SemaphoreTimeoutException,
    MaxRetriesExceededException,
)

__all__ = [
    # Base
    "TipsterByteException",
    # Database
    "DatabaseException",
    "MongoDBException",
    "MongoDBConnectionException",
    "MongoDBWriteException",
    "MongoDBReadException",
    # Session Log
    "SessionLogException",
    "SessionLogWriteException",
    "SessionLogReadException",
    # Process
    "ProcessException",
    "ProcessNotFoundException",
    "ProcessInactiveException",
    "ProcessRunCreationException",
    "NoActiveJobsException",
    # Fuente
    "FuenteException",
    "FuenteNotFoundException",
    "FuenteInactiveException",
    "DetalleInactiveException",
    # Robot
    "RobotException",
    "RobotNotFoundException",
    "ScrapingException",
    "ScrapingTimeoutException",
    "ScrapingParsingException",
    # Concurrency
    "ConcurrencyException",
    "SemaphoreTimeoutException",
    "MaxRetriesExceededException",
]
