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


class MongoCollectionNotInitializedException(MongoDBException):
    """
    Excepción lanzada cuando un modelo de Beanie existe pero la colección no ha sido inicializada.

    Esta excepción ocurre cuando:
    - El modelo está definido correctamente en código
    - Pero NUNCA se ejecutó `nosql init-schema`
    - La colección no existe fisicamente en MongoDB

    Attributes:
        message: Descripción del error
        collection: Nombre de la colección faltante
        model_name: Nombre de la clase del modelo
        suggested_command: Comando que resuelve el problema
    """

    def __init__(
        self,
        collection: str,
        model_name: str,
        message: Optional[str] = None,
        details: Optional[str] = None,
    ):
        if message is None:
            message = f"La colección '{collection}' para el modelo '{model_name}' no existe en MongoDB"

        super().__init__(
            message=message,
            error_code="MONGODB_COLLECTION_NOT_INITIALIZED",
            details=details,
        )
        self.collection = collection
        self.model_name = model_name
        self.suggested_command = "python backend/manage.py nosql init-schema"
