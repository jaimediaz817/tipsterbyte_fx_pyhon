"""
Modelos del Servicio de Limpieza de Logs
=========================================

Este módulo contiene los modelos de datos para el servicio de limpieza de logs.
"""

from .cleanup_history import (
    CleanupHistory,
    CleanupHistoryEntry,
    get_cleanup_history,
)

__all__ = [
    "CleanupHistory",
    "CleanupHistoryEntry",
    "get_cleanup_history",
]
