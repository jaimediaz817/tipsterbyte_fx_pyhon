"""
DTOs para bitácora de sesión.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class SessionLogResponse(BaseModel):
    """Respuesta de un log de sesión."""

    id: str = Field(description="ID del log en MongoDB")
    user_id: str = Field(description="ID del usuario")
    session_id: str = Field(description="ID de la sesión")
    action: str = Field(description="Tipo de acción")
    action_details: Dict[str, Any] = Field(
        default_factory=dict, description="Detalles de la acción"
    )
    ip_address: str = Field(description="Dirección IP")
    user_agent: str = Field(description="User-Agent")
    endpoint: str = Field(description="Endpoint accedido")
    method: str = Field(description="Método HTTP")
    status_code: int = Field(description="Código de estado HTTP")
    response_time_ms: float = Field(description="Tiempo de respuesta en ms")
    timestamp: datetime = Field(description="Marca de tiempo UTC")
    duration_seconds: Optional[float] = Field(
        None, description="Duración de la sesión en segundos"
    )


class PaginationInfo(BaseModel):
    """Información de paginación."""

    limit: int = Field(description="Límite de resultados")
    offset: int = Field(description="Offset para paginación")
    has_more: bool = Field(description="Si hay más resultados")


class SessionLogsListResponse(BaseModel):
    """Respuesta de lista de logs de sesión."""

    user_id: str = Field(description="ID del usuario")
    total_logs: int = Field(description="Total de logs")
    logs: List[SessionLogResponse] = Field(description="Lista de logs")
    pagination: PaginationInfo = Field(description="Información de paginación")


class SessionLogsBySessionResponse(BaseModel):
    """Respuesta de logs por session_id."""

    session_id: str = Field(description="ID de la sesión")
    logs: List[SessionLogResponse] = Field(description="Lista de logs")
