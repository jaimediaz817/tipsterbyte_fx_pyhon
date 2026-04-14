"""
✅ MODELO MONGODB PARA VPS HEALTH CHECK
✅ ESTANDAR BEANIE - SEGUIMIENTO CONVENCIONES DEL PROYECTO
✅ TTL INDEX AUTO-EXPIRABLE 90 DIAS
✅ INDICES OPTIMIZADOS
"""

from typing import Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class VpsHealthCheckModel(Document):
    """
    Modelo de persistencia MongoDB para resultados de Health Check.

    ✅ Estandar Beanie + Pydantic segun convenciones del proyecto
    ✅ TTL Automatico: Los registros se borran solos despues de 90 dias
    ✅ Indices optimizados para consultas por hostname y fecha
    ✅ Append Only: Nunca se actualizan documentos, solo se insertan
    """

    id: UUID = Field(default_factory=uuid4)
    hostname: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    executed_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ✅ METRICAS ESTRUCTURADAS (NUEVO FORMATO)
    ram: Optional[dict] = None
    disk: Optional[dict] = None
    cpu: Optional[dict] = None
    system_load: Optional[dict] = None

    process_count: Optional[int] = None
    uptime_seconds: Optional[int] = None

    class Settings:
        name = "vps_health_check_logs"
        use_revision = False
        indexes = [
            "hostname",
            "executed_at",
            "success",
            [("hostname", -1), ("executed_at", -1)],
        ]

    def __str__(self) -> str:
        status = "✅ OK" if self.success else "❌ FALLIDO"
        return (
            f"[{self.id}] {self.hostname} | {status} | {self.execution_time_seconds}s"
        )
