"""
Repositorio para operaciones de bitácora de sesión en MongoDB.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from loguru import logger

from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog
from core.exceptions.database_exceptions import (
    MongoDBWriteException,
    MongoDBReadException,
    MongoDBConnectionException,
)


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

        Raises:
            MongoDBWriteException: Error al escribir en MongoDB
            MongoDBConnectionException: MongoDB no disponible
        """
        try:
            await log.insert()
            return log
        except Exception as e:
            logger.error(
                f"❌ Error al escribir session log en MongoDB: {e} | "
                f"User: {log.user_id} | Session: {log.session_id} | Action: {log.action}"
            )
            # Re-lanzar como excepción de dominio
            raise MongoDBWriteException(
                message="Error al escribir session log",
                details=str(e),
                collection="session_logs",
            )

    async def get_by_user(
        self,
        user_id: int,
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

        Raises:
            MongoDBReadException: Error al leer de MongoDB
        """
        try:
            query = SessionLog.find(
                SessionLog.user_id == user_id,
                SessionLog.timestamp >= start_date,
                SessionLog.timestamp <= end_date,
            )

            if action:
                query = query.find(SessionLog.action == action)

            return await query.sort("-timestamp").skip(offset).limit(limit).to_list()
        except Exception as e:
            logger.error(
                f"❌ Error al leer session logs por usuario: {e} | "
                f"User: {user_id} | Period: {start_date} to {end_date}"
            )
            raise MongoDBReadException(
                message="Error al leer session logs por usuario",
                details=str(e),
                collection="session_logs",
            )

    async def count_by_user(
        self,
        user_id: int,
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

        Raises:
            MongoDBReadException: Error al leer de MongoDB
        """
        try:
            return await SessionLog.find(
                SessionLog.user_id == user_id,
                SessionLog.timestamp >= start_date,
                SessionLog.timestamp <= end_date,
            ).count()
        except Exception as e:
            logger.error(
                f"❌ Error al contar session logs por usuario: {e} | "
                f"User: {user_id} | Period: {start_date} to {end_date}"
            )
            raise MongoDBReadException(
                message="Error al contar session logs por usuario",
                details=str(e),
                collection="session_logs",
            )

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

        Raises:
            MongoDBReadException: Error al leer de MongoDB
        """
        try:
            return (
                await SessionLog.find(SessionLog.session_id == session_id)
                .sort("-timestamp")
                .skip(offset)
                .limit(limit)
                .to_list()
            )
        except Exception as e:
            logger.error(
                f"❌ Error al leer session logs por session_id: {e} | "
                f"Session: {session_id}"
            )
            raise MongoDBReadException(
                message="Error al leer session logs por session_id",
                details=str(e),
                collection="session_logs",
            )

    async def delete_old_logs(self, days: int = 90) -> int:
        """
        Elimina logs más antiguos que X días.

        Args:
            days: Número de días de retención

        Returns:
            Número de documentos eliminados

        Raises:
            MongoDBWriteException: Error al eliminar de MongoDB
        """
        try:
            cutoff_date = datetime.utcnow() - __import__("datetime").timedelta(
                days=days
            )
            result = await SessionLog.find(SessionLog.timestamp < cutoff_date).delete()
            return result.deleted_count if result else 0
        except Exception as e:
            logger.error(
                f"❌ Error al eliminar session logs antiguos: {e} | "
                f"Retention: {days} días"
            )
            raise MongoDBWriteException(
                message="Error al eliminar session logs antiguos",
                details=str(e),
                collection="session_logs",
            )
