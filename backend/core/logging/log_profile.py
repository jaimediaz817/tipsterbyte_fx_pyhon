"""
Log Profiles - Sistema de Perfiles de Logging (Strategy Pattern)
================================================================

Este módulo define perfiles de logging que encapsulan:
- Ruta del archivo de log
- Nivel de logging
- Configuración de rotación y retención
- Función de filtrado de registros

Patrón aplicado: Strategy + Factory + Dataclass
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from core.paths import LOGS_ROOT


@dataclass
class LogProfile(ABC):
    """
    Perfil base para configuración de logging.

    Cada perfil define cómo se escribe y filtra una categoría específica de logs.
    """

    name: str
    sink_path: Path
    level: str = "INFO"
    rotation: str = "10 MB"
    retention: str = "7 days"
    compression: str = "zip"

    @abstractmethod
    def filter(self, record: dict) -> bool:
        """
        Función de filtrado para determinar si un registro pertenece a este perfil.

        Args:
            record: Diccionario con información del registro de log

        Returns:
            True si el registro debe escribirse en este sink
        """
        pass

    def to_dict(self) -> dict:
        """Convierte el perfil a diccionario para serialización."""
        return {
            "name": self.name,
            "sink_path": str(self.sink_path),
            "level": self.level,
            "rotation": self.rotation,
            "retention": self.retention,
            "compression": self.compression,
        }

    def __str__(self) -> str:
        return f"LogProfile({self.name}, {self.sink_path.name})"


class SystemProfile(LogProfile):
    """Perfil para logs del sistema (core/*, excluye scheduler)."""

    def __init__(self):
        super().__init__(
            name="system",
            sink_path=LOGS_ROOT / "system.log",
        )

    def filter(self, record: dict) -> bool:
        name = record.get("name", "")
        return bool(name and name.startswith("core") and "scheduler" not in name)


class SchedulerProfile(LogProfile):
    """Perfil para logs del scheduler."""

    def __init__(self):
        super().__init__(
            name="scheduler",
            sink_path=LOGS_ROOT / "scheduler" / "scheduler.log",
            rotation="5 MB",
            retention="14 days",
        )

    def filter(self, record: dict) -> bool:
        name = record.get("name", "")
        return bool(name and "scheduler" in name)


class RobotsProfile(LogProfile):
    """Perfil para logs de robots de leagues_manager."""

    def __init__(self):
        super().__init__(
            name="robots",
            sink_path=LOGS_ROOT / "robots.log",
        )

    def filter(self, record: dict) -> bool:
        n = record.get("name", "")
        return bool(
            n
            and n.startswith("apps.leagues_manager")
            and (".robots." in n or n.endswith(".robots"))
        )


class GeneralProfile(LogProfile):
    """Perfil para logs generales (excluye core, scheduler y apps)."""

    def __init__(self):
        super().__init__(
            name="general",
            sink_path=LOGS_ROOT / "general_app.log",
            rotation="20 MB",
            retention="5 days",
        )

    def filter(self, record: dict) -> bool:
        name = record.get("name", "")
        if name.startswith("core") or "scheduler" in name:
            return False
        if name.startswith("apps."):
            return False
        return True


# ============================================================================
# Registry de Perfiles
# ============================================================================

LOG_PROFILES: dict[str, LogProfile] = {
    "system": SystemProfile(),
    "scheduler": SchedulerProfile(),
    "robots": RobotsProfile(),
    "general": GeneralProfile(),
}


def get_profile(name: str) -> LogProfile | None:
    """
    Obtiene un perfil por nombre.

    Args:
        name: Nombre del perfil

    Returns:
        LogProfile o None si no existe
    """
    return LOG_PROFILES.get(name)


def register_profile(profile: LogProfile) -> None:
    """
    Registra un nuevo perfil en el registry.

    Args:
        profile: Perfil a registrar
    """
    LOG_PROFILES[profile.name] = profile
