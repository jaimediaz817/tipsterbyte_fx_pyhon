"""
Repositorio para operaciones de bitácora de sesión en MongoDB.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pymongo import DESCENDING

from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog


class SessionLogRepository:
    """
    Repositorio para gestionar operaciones CRUD de SessionLog en MongoDB.
    """

    async def save(self, log: SessionLog) -> SessionLog:
        """
        Guarda un log en MongoDB.

        Args:
            log: Instancia de SessionLog a guardar

        Returns:
            SessionLog guardado con ID asignado
        """
        await log.insert()
        return log

    async def get_by_user(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SessionLog]:
        """
        Obtiene logs de un usuario por rango de fechas.

        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio
            end_date: Fecha de fin
            action: Filtrar por tipo de acción (opcional)
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de SessionLog
        """
        query = SessionLog.find(
            SessionLog.user_id == user_id,
            SessionLog.timestamp >= start_date,
            SessionLog.timestamp <= end_date,
        )

        if action:
            query = query.find(SessionLog.action == action)

        return (
            await query.sort(("timestamp", DESCENDING))
            .skip(offset)
            .limit(limit)
            .to_list()
        )

    async def count_by_user(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> int:
        """
        Cuenta logs de un usuario por rango de fechas.

        Args:
            user_id: ID del usuario
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Número total de logs
        """
        return await SessionLog.find(
            SessionLog.user_id == user_id,
            SessionLog.timestamp >= start_date,
            SessionLog.timestamp <= end_date,
        ).count()

    async def get_by_session_id(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SessionLog]:
        """
        Obtiene logs por session_id.

        Args:
            session_id: ID de la sesión
            limit: Límite de resultados
            offset: Offset para paginación

        Returns:
            Lista de SessionLog
        """
        return (
            await SessionLog.find(SessionLog.session_id == session_id)
            .sort(("timestamp", DESCENDING))
            .skip(offset)
            .limit(limit)
            .to_list()
        )

    async def delete_old_logs(self, days: int = 90) -> int:
        """
        Elimina logs más antiguos que X días.

        Args:
            days: Número de días de retención

        Returns:
            Número de documentos eliminados
        """
        cutoff_date = datetime.utcnow() - __import__("datetime").timedelta(days=days)
        result = await SessionLog.find(SessionLog.timestamp < cutoff_date).delete()
        return result.deleted_count if result else 0
