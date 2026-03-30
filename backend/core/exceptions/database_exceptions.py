"""
Excepciones personalizadas para errores de base de datos.

Este módulo contiene excepciones específicas para operaciones de MongoDB,
proporcionando un manejo granular de errores sin interrumpir el servicio.

Categorías:
- DatabaseException: Excepción base para errores de BD
- MongoDBException: Excepción base para errores de MongoDB
- MongoDBConnectionException: MongoDB no disponible
- MongoDBWriteException: Error al escribir en MongoDB
- MongoDBReadException: Error al leer de MongoDB
"""

from typing import Optional
from core.exceptions.base import TipsterByteException


class DatabaseException(TipsterByteException):
    """
    Excepción base para errores de base de datos.

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
    """

    def __init__(
        self,
        message: str,
        error_code: str = "DATABASE_ERROR",
        details: Optional[str] = None,
    ):
        super().__init__(message, error_code)
        self.details = details


class MongoDBException(DatabaseException):
    """
    Excepción base para errores específicos de MongoDB.

    Attributes:
        message: Descripción del error
        details: Detalles adicionales del error (opcional)
    """

    pass


class MongoDBConnectionException(MongoDBException):
    """
    MongoDB no está disponible o no se puede conectar.

    Esta excepción se lanza cuando:
    - MongoDB no está corriendo
    - La conexión es rechazada
    - Timeout de conexión

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
        host: Host de MongoDB (opcional)
        port: Puerto de MongoDB (opcional)
    """

    def __init__(
        self,
        message: str = "MongoDB no está disponible",
        error_code: str = "MONGODB_CONNECTION_ERROR",
        details: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ):
        super().__init__(message, error_code, details)
        self.host = host
        self.port = port


class MongoDBWriteException(MongoDBException):
    """
    Error al escribir en MongoDB.

    Esta excepción se lanza cuando:
    - Falla la inserción de un documento
    - Falla la actualización de un documento
    - Error de permisos o espacio en disco

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
        collection: Nombre de la colección afectada (opcional)
    """

    def __init__(
        self,
        message: str = "Error al escribir en MongoDB",
        error_code: str = "MONGODB_WRITE_ERROR",
        details: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        super().__init__(message, error_code, details)
        self.collection = collection


class MongoDBReadException(MongoDBException):
    """
    Error al leer de MongoDB.

    Esta excepción se lanza cuando:
    - Falla la consulta de documentos
    - Error de permisos
    - Timeout de consulta

    Attributes:
        message: Descripción del error
        error_code: Código único del error
        details: Detalles adicionales del error (opcional)
        collection: Nombre de la colección afectada (opcional)
    """

    def __init__(
        self,
        message: str = "Error al leer de MongoDB",
        error_code: str = "MONGODB_READ_ERROR",
        details: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        super().__init__(message, error_code, details)
        self.collection = collection
