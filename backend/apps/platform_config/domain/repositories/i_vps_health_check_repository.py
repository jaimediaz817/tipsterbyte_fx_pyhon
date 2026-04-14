"""
✅ INTERFAZ ABSTRACTA REPOSITORIO VPS HEALTH CHECK
✅ SEGUNDO PRINCIPIO SOLID: OPEN/CLOSED
✅ INVERSION DE DEPENDENCIAS
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from backend.apps.platform_config.domain.entities.vps_health_check import VpsHealthCheck


class IVpsHealthCheckRepository(ABC):
    """
    Interfaz abstracta para el repositorio de resultados de Health Check.

    ✅ Todas las implementaciones deben cumplir este contrato.
    ✅ El dominio solo conoce esta interfaz, nunca la implementacion concreta.
    ✅ Se puede reemplazar MongoDB por cualquier otra tecnologia sin cambiar nada del dominio.
    """

    @abstractmethod
    def save(self, health_check: VpsHealthCheck) -> None:
        """
        Guarda un resultado de health check.
        Es una operacion append-only, NUNCA actualiza.
        """
        ...

    @abstractmethod
    def get_by_id(self, health_check_id: UUID) -> Optional[VpsHealthCheck]:
        """
        Obtiene un resultado por su identificador unico
        """
        ...

    @abstractmethod
    def get_latest_for_hostname(
        self, hostname: str, limit: int = 10
    ) -> List[VpsHealthCheck]:
        """
        Obtiene los ultimos N resultados para un servidor especifico
        Ordenados de mas nuevo a mas antiguo
        """
        ...

    @abstractmethod
    def get_by_date_range(
        self, start_date: datetime, end_date: datetime, hostname: Optional[str] = None
    ) -> List[VpsHealthCheck]:
        """
        Obtiene todos los resultados dentro de un rango de fechas
        Opcionalmente filtrado por hostname
        """
        ...

    @abstractmethod
    def count_failures_last_hours(self, hostname: str, hours: int = 24) -> int:
        """
        Cuenta cuantas fallidas ha tenido un servidor en las ultimas N horas
        """
        ...
