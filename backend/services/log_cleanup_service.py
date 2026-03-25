"""
Servicio de Limpieza Automática de Logs
========================================

Servicio aislado que gestiona la archivación y eliminación de logs antiguos.
Puede funcionar independientemente o integrado con el scheduler.

Uso manual:
    from services.log_cleanup_service import LogCleanupService

    service = LogCleanupService()
    result = service.run_cleanup()
    print(result)
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from loguru import logger

# Agregar directorio backend al path para imports
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core.config import settings
from core.paths import LOGS_ROOT


@dataclass
class CleanupResult:
    """Resultado de una operación de limpieza."""

    success: bool = True
    archived_files: int = 0
    deleted_files: int = 0
    freed_space_mb: float = 0.0
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "archived_files": self.archived_files,
            "deleted_files": self.deleted_files,
            "freed_space_mb": round(self.freed_space_mb, 2),
            "errors": self.errors,
            "timestamp": self.timestamp.isoformat(),
        }

    def __str__(self) -> str:
        status = "✅ ÉXITO" if self.success else "❌ ERROR"
        return (
            f"{status} | "
            f"Archivados: {self.archived_files} | "
            f"Eliminados: {self.deleted_files} | "
            f"Espacio liberado: {self.freed_space_mb:.2f} MB"
        )


class LogCleanupService:
    """
    Servicio para limpieza automática de logs.

    Responsabilidades:
    1. Archivar logs activos más antiguos de N días
    2. Eliminar logs archivados más antiguos de M días
    3. Reportar espacio en disco utilizado
    """

    def __init__(
        self,
        logs_dir: Optional[Path] = None,
        archive_dir: Optional[Path] = None,
        retention_days: Optional[int] = None,
        archive_retention_days: Optional[int] = None,
    ):
        """
        Inicializa el servicio de limpieza.

        Args:
            logs_dir: Directorio de logs activos (default: LOGS_ROOT)
            archive_dir: Directorio de logs archivados (default: settings.LOG_ARCHIVE_DIR)
            retention_days: Días de retención de logs activos (default: settings.LOG_RETENTION_DAYS)
            archive_retention_days: Días de retención de logs archivados (default: settings.LOG_ARCHIVE_RETENTION_DAYS)
        """
        self.logs_dir = logs_dir or LOGS_ROOT
        self.archive_dir = archive_dir or Path(settings.LOG_ARCHIVE_DIR)
        self.retention_days = retention_days or settings.LOG_RETENTION_DAYS
        self.archive_retention_days = (
            archive_retention_days or settings.LOG_ARCHIVE_RETENTION_DAYS
        )

        # Crear directorio de archivo si no existe
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        logger.debug(
            f"🧹 LogCleanupService inicializado: "
            f"logs={self.logs_dir}, "
            f"archive={self.archive_dir}, "
            f"retention={self.retention_days}d, "
            f"archive_retention={self.archive_retention_days}d"
        )

    def get_disk_usage(self) -> dict:
        """
        Obtiene información de uso de disco de los directorios de logs.

        Returns:
            dict con información de espacio utilizado
        """

        def _get_dir_size(path: Path) -> float:
            """Calcula el tamaño de un directorio en MB."""
            if not path.exists():
                return 0.0
            total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            return total / (1024 * 1024)  # Convertir a MB

        logs_size = _get_dir_size(self.logs_dir)
        archive_size = _get_dir_size(self.archive_dir)

        return {
            "logs_dir": str(self.logs_dir),
            "logs_size_mb": round(logs_size, 2),
            "archive_dir": str(self.archive_dir),
            "archive_size_mb": round(archive_size, 2),
            "total_size_mb": round(logs_size + archive_size, 2),
        }

    def _get_files_older_than(self, directory: Path, days: int) -> list[Path]:
        """
        Obtiene archivos más antiguos que N días.

        Args:
            directory: Directorio a escanear
            days: Número de días de antigüedad

        Returns:
            Lista de archivos Path que son más antiguos que N días
        """
        if not directory.exists():
            return []

        cutoff_date = datetime.now() - timedelta(days=days)
        old_files = []

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Usar fecha de modificación del archivo
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    old_files.append(file_path)

        return old_files

    def archive_old_logs(self) -> CleanupResult:
        """
        Archiva logs activos más antiguos que retention_days.

        Mueve archivos de logs_dir a archive_dir preservando estructura.

        Returns:
            CleanupResult con el resultado de la operación
        """
        result = CleanupResult()

        logger.info(f"📦 Iniciando archivación de logs > {self.retention_days} días...")

        old_files = self._get_files_older_than(self.logs_dir, self.retention_days)

        if not old_files:
            logger.info("✅ No hay logs antiguos para archivar")
            return result

        for file_path in old_files:
            try:
                # Verificar que el archivo aún existe (puede haber sido movido por Loguru)
                if not file_path.exists():
                    logger.debug(
                        f"  ⏭️ Archivo ya no existe, saltando: {file_path.name}"
                    )
                    continue

                # Calcular ruta de destino preservando estructura relativa
                relative_path = file_path.relative_to(self.logs_dir)
                dest_path = self.archive_dir / relative_path

                # Crear directorio de destino si no existe
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Verificar nuevamente que el archivo existe antes de moverlo
                # (evita condición de carrera en Windows)
                if not file_path.exists():
                    logger.debug(
                        f"  ⏭️ Archivo desapareció antes de mover: {file_path.name}"
                    )
                    continue

                # Mover archivo usando shutil.move() (más robusto en Windows)
                # Capturar el mtime antes de mover para logging
                try:
                    file_size_mb = file_path.stat().st_size / (1024 * 1024)
                    shutil.move(str(file_path), str(dest_path))
                except FileNotFoundError:
                    # Archivo fue eliminado entre la verificación y el movimiento
                    logger.debug(
                        f"  ⏭️ Archivo desapareció durante movimiento: {file_path.name}"
                    )
                    continue
                result.freed_space_mb += file_size_mb
                result.archived_files += 1

                logger.debug(f"  📦 Archivado: {relative_path}")

            except FileNotFoundError as e:
                # Archivo fue movido o eliminado mientras lo procesábamos
                logger.debug(
                    f"  ⏭️ Archivo desapareció durante procesamiento: {file_path.name} - {e}"
                )
                continue

            except PermissionError as e:
                # Archivo está siendo usado por otro proceso (común en Windows)
                logger.debug(
                    f"  ⏭️ Archivo en uso por otro proceso: {file_path.name} - {e}"
                )
                continue

            except OSError as e:
                # Error de sistema operativo (común en Windows con archivos abiertos)
                logger.debug(
                    f"  ⏭️ Error de OS procesando archivo: {file_path.name} - {e}"
                )
                continue

            except Exception as e:
                error_msg = f"Error archivando {file_path.name}: {e}"
                result.errors.append(error_msg)
                logger.warning(f"  ⚠️ {error_msg}")

        if result.errors:
            result.success = False

        logger.info(
            f"📦 Archivación completada: {result.archived_files} archivos, "
            f"{result.freed_space_mb:.2f} MB"
        )

        return result

    def delete_archived_logs(self) -> CleanupResult:
        """
        Elimina logs archivados más antiguos que archive_retention_days.

        Returns:
            CleanupResult con el resultado de la operación
        """
        result = CleanupResult()

        logger.info(
            f"🗑️ Iniciando eliminación de logs archivados > "
            f"{self.archive_retention_days} días..."
        )

        old_files = self._get_files_older_than(
            self.archive_dir, self.archive_retention_days
        )

        if not old_files:
            logger.info("✅ No hay logs archivados antiguos para eliminar")
            return result

        for file_path in old_files:
            try:
                # Calcular tamaño antes de eliminar
                file_size_mb = file_path.stat().st_size / (1024 * 1024)

                # Eliminar archivo
                file_path.unlink()

                result.freed_space_mb += file_size_mb
                result.deleted_files += 1

                logger.debug(f"  🗑️ Eliminado: {file_path.name}")

            except Exception as e:
                error_msg = f"Error eliminando {file_path.name}: {e}"
                result.errors.append(error_msg)
                logger.warning(f"  ⚠️ {error_msg}")

        if result.errors:
            result.success = False

        logger.info(
            f"🗑️ Eliminación completada: {result.deleted_files} archivos, "
            f"{result.freed_space_mb:.2f} MB liberados"
        )

        return result

    def run_cleanup(self) -> CleanupResult:
        """
        Ejecuta el proceso completo de limpieza:
        1. Archivar logs antiguos
        2. Eliminar logs archivados muy antiguos

        Returns:
            CleanupResult combinado con el resultado total
        """
        logger.info("=" * 60)
        logger.info("🧹 INICIANDO LIMPIEZA AUTOMÁTICA DE LOGS")
        logger.info("=" * 60)

        # Mostrar uso de disco antes
        usage_before = self.get_disk_usage()
        logger.info(
            f"📊 Espacio en disco antes: "
            f"logs={usage_before['logs_size_mb']} MB, "
            f"archive={usage_before['archive_size_mb']} MB"
        )

        # Fase 1: Archivar
        archive_result = self.archive_old_logs()

        # Fase 2: Eliminar
        delete_result = self.delete_archived_logs()

        # Combinar resultados
        combined = CleanupResult(
            success=archive_result.success and delete_result.success,
            archived_files=archive_result.archived_files,
            deleted_files=delete_result.deleted_files,
            freed_space_mb=archive_result.freed_space_mb + delete_result.freed_space_mb,
            errors=archive_result.errors + delete_result.errors,
        )

        # Mostrar uso de disco después
        usage_after = self.get_disk_usage()
        logger.info(
            f"📊 Espacio en disco después: "
            f"logs={usage_after['logs_size_mb']} MB, "
            f"archive={usage_after['archive_size_mb']} MB"
        )

        logger.info("=" * 60)
        logger.info(f"🧹 LIMPIEZA COMPLETADA: {combined}")
        logger.info("=" * 60)

        return combined


def run_manual_cleanup() -> CleanupResult:
    """
    Ejecuta limpieza manual con configuración por defecto.

    Útil para pruebas o ejecución desde scripts.

    Returns:
        CleanupResult con el resultado
    """
    service = LogCleanupService()
    return service.run_cleanup()


def get_logs_disk_usage() -> dict:
    """
    Obtiene información de uso de disco de logs.

    Returns:
        dict con información de espacio
    """
    service = LogCleanupService()
    return service.get_disk_usage()


if __name__ == "__main__":
    # Configurar logging para pruebas
    from loguru import logger as test_logger

    test_logger.remove()
    test_logger.add(sys.stdout, level="DEBUG")

    print("\n" + "=" * 60)
    print("🧪 PRUEBA MANUAL DE LIMPIEZA DE LOGS")
    print("=" * 60 + "\n")

    # Ejecutar limpieza
    result = run_manual_cleanup()

    print("\n📊 RESULTADO:")
    print(f"  ✅ Éxito: {result.success}")
    print(f"  📦 Archivados: {result.archived_files}")
    print(f"  🗑️ Eliminados: {result.deleted_files}")
    print(f"  💾 Espacio liberado: {result.freed_space_mb:.2f} MB")

    if result.errors:
        print(f"\n❌ ERRORES ({len(result.errors)}):")
        for error in result.errors:
            print(f"  - {error}")

    print("\n" + "=" * 60)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 60 + "\n")
