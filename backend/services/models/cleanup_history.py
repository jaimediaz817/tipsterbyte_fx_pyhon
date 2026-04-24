"""
Historial de Limpiezas de Logs - Auditoría y Fidelidad
======================================================

Este módulo registra cada operación de limpieza realizada,
proporcionando trazabilidad completa para auditoría.

Patrón aplicado: Repository + Dataclass
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


@dataclass
class CleanupHistoryEntry:
    """Entrada individual del historial de limpieza."""

    timestamp: datetime
    profile_name: str
    action: str  # "archive" o "delete"
    files_count: int
    freed_space_mb: float
    files_processed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "profile_name": self.profile_name,
            "action": self.action,
            "files_count": self.files_count,
            "freed_space_mb": round(self.freed_space_mb, 4),
            "files_processed": self.files_processed,
            "errors": self.errors,
            "duration_seconds": round(self.duration_seconds, 3),
        }

    def __str__(self) -> str:
        status = "✅" if not self.errors else "⚠️"
        return (
            f"{status} [{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{self.profile_name}: {self.action} {self.files_count} files, "
            f"{self.freed_space_mb:.2f} MB freed"
        )


class CleanupHistory:
    """
    Historial de limpiezas de logs.

    Registra todas las operaciones de limpieza para:
    - Auditoría de cumplimiento
    - Debugging de problemas
    - Métricas de rendimiento
    - Trazabilidad de archivos eliminados
    """

    def __init__(self, history_file: Optional[Path] = None):
        """
        Inicializa el historial.

        Args:
            history_file: Archivo donde persistir el historial (JSON)
        """
        if history_file is None:
            # ✅ Solucion definitiva ruta absoluta: funciona desde CUALQUIER ubicacion
            from pathlib import Path

            ROOT = Path(__file__).resolve().parents[3]
            self.history_file = ROOT / "backend" / "logs" / "cleanup_history.json"
        else:
            self.history_file = history_file

        self.entries: list[CleanupHistoryEntry] = []
        self._load_history()

    def _load_history(self) -> None:
        """Carga historial desde archivo si existe."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.entries = [
                        CleanupHistoryEntry(
                            timestamp=datetime.fromisoformat(e["timestamp"]),
                            profile_name=e["profile_name"],
                            action=e["action"],
                            files_count=e["files_count"],
                            freed_space_mb=e["freed_space_mb"],
                            files_processed=e.get("files_processed", []),
                            errors=e.get("errors", []),
                            duration_seconds=e.get("duration_seconds", 0.0),
                        )
                        for e in data.get("entries", [])
                    ]
            except Exception:
                self.entries = []

    def _save_history(self) -> None:
        """Persiste historial a archivo."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "last_updated": datetime.now().isoformat(),
                        "total_entries": len(self.entries),
                        "entries": [e.to_dict() for e in self.entries],
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )
        except Exception as e:
            print(f"Error saving cleanup history: {e}")

    def add_entry(self, entry: CleanupHistoryEntry) -> None:
        """Agrega una entrada al historial."""
        self.entries.append(entry)
        self._save_history()

    def get_entries(
        self,
        profile_name: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> list[CleanupHistoryEntry]:
        """
        Obtiene entradas del historial con filtros opcionales.

        Args:
            profile_name: Filtrar por perfil
            action: Filtrar por acción (archive/delete)
            limit: Número máximo de entradas

        Returns:
            Lista de entradas filtradas
        """
        filtered = self.entries

        if profile_name:
            filtered = [e for e in filtered if e.profile_name == profile_name]

        if action:
            filtered = [e for e in filtered if e.action == action]

        return filtered[-limit:]

    def get_stats(self) -> dict:
        """Obtiene estadísticas del historial."""
        if not self.entries:
            return {
                "total_cleanups": 0,
                "total_files_processed": 0,
                "total_freed_mb": 0.0,
                "total_errors": 0,
                "last_cleanup": None,
            }

        total_files = sum(e.files_count for e in self.entries)
        total_freed = sum(e.freed_space_mb for e in self.entries)
        total_errors = sum(len(e.errors) for e in self.entries)

        return {
            "total_cleanups": len(self.entries),
            "total_files_processed": total_files,
            "total_freed_mb": round(total_freed, 2),
            "total_errors": total_errors,
            "last_cleanup": self.entries[-1].timestamp.isoformat(),
        }

    def clear(self) -> None:
        """Limpia el historial."""
        self.entries = []
        self._save_history()

    def __len__(self) -> int:
        return len(self.entries)

    def __str__(self) -> str:
        stats = self.get_stats()
        return (
            f"CleanupHistory("
            f"entries={stats['total_cleanups']}, "
            f"files={stats['total_files_processed']}, "
            f"freed={stats['total_freed_mb']} MB)"
        )


# Singleton para acceso global
_cleanup_history: Optional[CleanupHistory] = None


def get_cleanup_history() -> CleanupHistory:
    """Obtiene instancia singleton del historial."""
    global _cleanup_history
    if _cleanup_history is None:
        _cleanup_history = CleanupHistory()
    return _cleanup_history
