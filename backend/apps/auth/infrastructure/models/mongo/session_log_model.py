"""
Modelo de bitácora de sesión para MongoDB.
Registra todas las acciones y eventos de sesión de los usuarios.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID
from beanie import Document
from pydantic import Field


class SessionLog(Document):
    """
    Registra un evento de sesión o acción de un usuario.
    Este documento vive en MongoDB y se relaciona con un usuario de PostgreSQL
    a través del campo 'user_id'.
    """

    user_id: int = Field(description="ID del usuario en PostgreSQL")
    session_id: str = Field(description="Identificador único de la sesión")
    action: str = Field(
        description="Tipo de acción realizada (login, logout, api_call, etc.)"
    )
    action_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Detalles adicionales de la acción en formato JSON",
    )
    ip_address: str = Field(description="Dirección IP del cliente")
    user_agent: str = Field(description="User-Agent del navegador/dispositivo")
    endpoint: str = Field(description="Endpoint de la API accedido")
    method: str = Field(description="Método HTTP (GET, POST, PUT, DELETE)")
    status_code: int = Field(description="Código de estado HTTP de la respuesta")
    response_time_ms: float = Field(description="Tiempo de respuesta en milisegundos")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Marca de tiempo UTC del evento",
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        description="Duración de la sesión en segundos (solo para logs de sesión)",
    )

    class Settings:
        name = "session_logs"  # Nombre de la colección en MongoDB
        indexes = [
            "user_id",
            "session_id",
            "timestamp",
            "action",
            [
                ("user_id", 1),
                ("timestamp", -1),
            ],  # Índice compuesto para consultas por usuario y fecha
        ]
