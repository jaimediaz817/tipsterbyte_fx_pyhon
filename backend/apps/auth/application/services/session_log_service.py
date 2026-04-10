"""
Servicio de bitácora de sesión.
Gestiona el registro y consulta de logs de sesión.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog
from apps.auth.infrastructure.repositories.session_log_repository import (
    SessionLogRepository,
)


class SessionLogService:
    """
    Servicio para gestionar la bitácora de sesión.
    """

    def __init__(self, repository: SessionLogRepository):
        self.repository = repository

    async def log_action(
        self,
        user_id: int,
        session_id: str,
        action: str,
        ip_address: str,
        user_agent: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        action_details: Optional[dict] = None,
        duration_seconds: Optional[float] = None,
    ) -> SessionLog:
        """
        Registra una acción en la bitácora.

        Args:
            user_id: ID del usuario
            session_id: ID de la sesión
            action: Tipo de acción (login, logout, api_call, etc.)
            ip_address: Dirección IP del cliente
            user_agent: User-Agent del navegador
            endpoint: Endpoint de la API accedido
            method: Método HTTP
            status_code: Código de estado HTTP
            response_time_ms: Tiempo de respuesta en milisegundos
            action_details: Detalles adicionales de la acción
            duration_seconds: Duración de la sesión en segundos

        Returns:
            SessionLog creado
        """
        log = SessionLog(
            user_id=user_id,
            session_id=session_id,
            action=action,
            action_details=action_details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.utcnow(),
            duration_seconds=duration_seconds,
        )
        return await self.repository.save(log)

    async def get_user_logs(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        Obtiene logs de un usuario con paginación.

        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio
            end_date: Fecha de fin
            action: Filtrar por tipo de acción
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict con logs, total y paginación
        """
        logs = await self.repository.get_by_user(
            user_id, start_date, end_date, action, limit, offset
        )
        total = await self.repository.count_by_user(user_id, start_date, end_date)

        return {
            "user_id": str(user_id),
            "total_logs": total,
            "logs": [log.dict() for log in logs],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total,
            },
        }

    async def get_session_logs(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        Obtiene logs por session_id.

        Args:
            session_id: ID de la sesión
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Dict con logs
        """
        logs = await self.repository.get_by_session_id(session_id, limit, offset)

        return {
            "session_id": session_id,
            "logs": [log.dict() for log in logs],
        }

    async def log_api_call(
        self,
        user_id: str,
        session_id: str,
        ip_address: str,
        user_agent: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
    ) -> SessionLog:
        """
        Registra una llamada a la API.

        Método de conveniencia para el middleware de auditoría.
        Encapsula la lógica de creación del log con action="api_call".

        Args:
            user_id: ID del usuario (string)
            session_id: ID de la sesión
            ip_address: Dirección IP del cliente
            user_agent: User-Agent del navegador
            endpoint: Endpoint de la API accedido
            method: Método HTTP
            status_code: Código de estado HTTP
            response_time_ms: Tiempo de respuesta en milisegundos

        Returns:
            SessionLog creado
        """
        # Convertir user_id de string a int si es necesario
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id

        return await self.log_action(
            user_id=user_id_int,
            session_id=session_id,
            action="api_call",
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )

    async def cleanup_old_logs(self, days: int = 90) -> int:
        """
        Elimina logs más antiguos que X días.

        Args:
            days: Número de días de retención

        Returns:
            Número de documentos eliminados
        """
        return await self.repository.delete_old_logs(days)
