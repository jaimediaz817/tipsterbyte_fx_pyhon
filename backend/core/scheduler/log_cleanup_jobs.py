"""
Jobs de Limpieza de Logs para el Scheduler
==========================================

Este módulo contiene los jobs programados para la limpieza automática de logs.
Se integra con el scheduler existente usando el patrón Factory.
"""

from services.log_cleanup_service import LogCleanupService
from services.models.cleanup_history import CleanupHistoryEntry, get_cleanup_history
from datetime import datetime
from loguru import logger
import time


def create_log_cleanup_job():
    """
    Factory que crea la función de job para limpieza de logs.
    Registra automáticamente en el historial de auditoría.
    """

    def job_function():
        start_time = time.time()
        logger.info("🧹 Iniciando limpieza programada de logs...")

        try:
            service = LogCleanupService()
            result = service.run_cleanup()
            duration = time.time() - start_time

            # Registrar en historial de auditoría
            history = get_cleanup_history()
            history_entry = CleanupHistoryEntry(
                timestamp=datetime.now(),
                profile_name="scheduler",
                action="cleanup",
                files_count=result.archived_files + result.deleted_files,
                freed_space_mb=result.freed_space_mb,
                errors=result.errors,
                duration_seconds=duration,
            )
            history.add_entry(history_entry)

            if result.success:
                logger.success(
                    f"✅ Limpieza completada: "
                    f"{result.archived_files} archivados, "
                    f"{result.deleted_files} eliminados, "
                    f"{result.freed_space_mb:.2f} MB liberados "
                    f"({duration:.2f}s)"
                )
            else:
                logger.warning(
                    f"⚠️ Limpieza completada con errores: " f"{result.errors}"
                )

        except Exception as e:
            duration = time.time() - start_time
            logger.exception(f"❌ Error en limpieza de logs ({duration:.2f}s): {e}")

            # Registrar error en historial
            try:
                history = get_cleanup_history()
                history_entry = CleanupHistoryEntry(
                    timestamp=datetime.now(),
                    profile_name="scheduler",
                    action="cleanup_error",
                    files_count=0,
                    freed_space_mb=0.0,
                    errors=[str(e)],
                    duration_seconds=duration,
                )
                history.add_entry(history_entry)
            except Exception:
                pass  # No fallar si no se puede registrar el error

    return job_function


# Mapa de procesos de limpieza para registrar en el scheduler
LOG_CLEANUP_PROCESS_MAP = {
    "PROCESS_LOG_CLEANUP": create_log_cleanup_job(),
}
