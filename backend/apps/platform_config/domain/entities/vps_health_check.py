"""
✅ ENTIDAD DE DOMINIO VPS HEALTH CHECK
✅ INMUTABLE
✅ VALIDADA
✅ SIN DEPENDENCIAS EXTERNAS
"""

from loguru import logger
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(frozen=True)
class RamMetrics:
    """Value Object inmutable para métricas de Memoria RAM"""

    total_mb: Optional[int] = None
    used_mb: Optional[int] = None
    usage_percent: Optional[float] = None
    total_unit: Optional[str] = None
    used_unit: Optional[str] = None


@dataclass(frozen=True)
class DiskMetrics:
    """Value Object inmutable para métricas de Disco"""

    total_gb: Optional[float] = None
    used_gb: Optional[float] = None
    usage_percent: Optional[float] = None
    total_unit: Optional[str] = None
    used_unit: Optional[str] = None


@dataclass(frozen=True)
class CpuMetrics:
    """Value Object inmutable para métricas de CPU"""

    usage_percent: Optional[float] = None


@dataclass(frozen=True)
class SystemLoadMetrics:
    """Value Object inmutable para carga del sistema"""

    load_1min: Optional[float] = None
    load_5min: Optional[float] = None
    load_15min: Optional[float] = None


@dataclass(frozen=True)
class VpsHealthCheck:
    """
    Entidad de dominio que representa un resultado completo
    de health check ejecutado sobre un servidor remoto.

    ✅ Esta entidad es la unica fuente de verdad.
    ✅ Nunca se modifica despues de creada.
    ✅ Es agnostica a cualquier tecnologia de persistencia.
    """

    id: UUID
    hostname: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    executed_at: datetime
    created_at: datetime

    # ✅ METRICAS ESTRUCTURADAS POR DOMINIO
    ram: RamMetrics
    disk: DiskMetrics
    cpu: CpuMetrics
    system_load: SystemLoadMetrics

    process_count: Optional[int] = None
    uptime_seconds: Optional[int] = None

    # ---------------------------------------------------
    # ✅ COMPATIBILIDAD HACIA ATRAS (DEPRECATED)
    # Mantenemos propiedades antiguas para no romper codigo existente
    # ---------------------------------------------------
    @property
    def ram_total_mb(self) -> Optional[int]:
        return self.ram.total_mb

    @property
    def ram_used_mb(self) -> Optional[int]:
        return self.ram.used_mb

    @property
    def ram_usage_percent(self) -> Optional[float]:
        return self.ram.usage_percent

    @property
    def ram_total_unit(self) -> Optional[str]:
        return self.ram.total_unit

    @property
    def ram_used_unit(self) -> Optional[str]:
        return self.ram.used_unit

    @property
    def disk_total_gb(self) -> Optional[float]:
        return self.disk.total_gb

    @property
    def disk_used_gb(self) -> Optional[float]:
        return self.disk.used_gb

    @property
    def disk_usage_percent(self) -> Optional[float]:
        return self.disk.usage_percent

    @property
    def disk_total_unit(self) -> Optional[str]:
        return self.disk.total_unit

    @property
    def disk_used_unit(self) -> Optional[str]:
        return self.disk.used_unit

    @property
    def cpu_usage_percent(self) -> Optional[float]:
        return self.cpu.usage_percent

    @property
    def load_1min(self) -> Optional[float]:
        return self.system_load.load_1min

    @property
    def load_5min(self) -> Optional[float]:
        return self.system_load.load_5min

    @property
    def load_15min(self) -> Optional[float]:
        return self.system_load.load_15min

    @classmethod
    def create(
        cls,
        hostname: str,
        success: bool,
        exit_code: int,
        stdout: str,
        stderr: str,
        execution_time_seconds: float,
        executed_at: Optional[datetime] = None,
    ) -> "VpsHealthCheck":
        """
        Factory method para crear nuevas instancias validas

        Args:
            hostname: IP o dominio del servidor monitoreado
            success: True si la ejecucion termino correctamente
            exit_code: Codigo de salida nativo del proceso
            stdout: Salida estandar completa
            stderr: Salida de error completa
            execution_time_seconds: Tiempo total de ejecucion
            executed_at: Momento exacto cuando se lanzo la ejecucion

        Returns:
            Instancia valida y lista para usar
        """
        now = datetime.utcnow()

        # ✅ PARSER AUTOMATICO DE METRICAS
        metricas: dict[str, int | float | str | None] = {
            "ram_total_mb": None,
            "ram_used_mb": None,
            "ram_usage_percent": None,
            "cpu_usage_percent": None,
            "disk_total_gb": None,
            "disk_used_gb": None,
            "disk_usage_percent": None,
            "load_1min": None,
            "load_5min": None,
            "load_15min": None,
            "process_count": None,
            "uptime_seconds": None,
            "ram_total_unit": None,
            "ram_used_unit": None,
            "disk_total_unit": None,
            "disk_used_unit": None,
        }

        # ✅ CORREGIR TIPADO: Asegurar que campos enteros son realmente int
        # Eliminamos tipo float de campos que solo admiten int en el constructor
        campos_enteros = [
            "ram_total_mb",
            "ram_used_mb",
            "process_count",
            "uptime_seconds",
        ]
        for campo in campos_enteros:
            valor = metricas[campo]
            if valor is not None:
                metricas[campo] = int(valor)

        if success and stdout:
            import re

            # ✅ PRIMERO LIMPIAMOS TODOS LOS CODIGOS ANSI DE COLORES
            stdout_limpio = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])").sub(
                "", stdout
            )

            # ✅ Parsear RAM
            ram_match = re.search(r"Uso:\s+(\d+)%", stdout_limpio)
            if ram_match:
                metricas["ram_usage_percent"] = float(ram_match.group(1))
                logger.debug(f"✅ RAM Uso detectado: {metricas['ram_usage_percent']}%")

            ram_total_match = re.search(r"Total:\s+([\d.]+)(G|M)", stdout_limpio)
            if ram_total_match:
                valor = float(ram_total_match.group(1))
                unidad = ram_total_match.group(2)
                metricas["ram_total_mb"] = int(valor * 1024 if unidad == "G" else valor)
                metricas["ram_total_unit"] = unidad

            ram_usada_match = re.search(r"Usada:\s+([\d.]+)(G|M)", stdout_limpio)
            if ram_usada_match:
                valor = float(ram_usada_match.group(1))
                unidad = ram_usada_match.group(2)
                metricas["ram_used_mb"] = int(valor * 1024 if unidad == "G" else valor)
                metricas["ram_used_unit"] = unidad

            # ✅ Parsear CPU
            cpu_match = re.search(r"Uso actual:\s+([\d.]+)%", stdout_limpio)
            if cpu_match:
                metricas["cpu_usage_percent"] = float(cpu_match.group(1))

            # ✅ Parsear Disco principal /
            disco_match = re.search(
                r"/:\s+([\d.]+)(G|M) total \| ([\d.]+)(G|M) usado \| [\d.]+(G|M) libre \| (\d+)%",
                stdout_limpio,
            )
            if disco_match:
                valor_total = float(disco_match.group(1))
                unidad_total = disco_match.group(2)
                valor_usado = float(disco_match.group(3))
                unidad_usado = disco_match.group(4)
                porcentaje = float(disco_match.group(6))

                # ✅ Guardar valor normalizado siempre en GB
                metricas["disk_total_gb"] = (
                    valor_total / 1024 if unidad_total == "M" else valor_total
                )
                metricas["disk_used_gb"] = (
                    valor_usado / 1024 if unidad_usado == "M" else valor_usado
                )
                metricas["disk_usage_percent"] = porcentaje

                # ✅ Guardar unidad original detectada
                metricas["disk_total_unit"] = unidad_total
                metricas["disk_used_unit"] = unidad_usado

            # ✅ Parsear Carga del sistema
            carga_match = re.search(
                r"Carga del sistema:\s+([\d.]+),\s+([\d.]+),\s+([\d.]+)", stdout_limpio
            )
            if carga_match:
                metricas["load_1min"] = float(carga_match.group(1))
                metricas["load_5min"] = float(carga_match.group(2))
                metricas["load_15min"] = float(carga_match.group(3))

        # ✅ SOLUCION DEFINITIVA TIPADO PYLANCE
        # Usamos cast() para garantizar al type checker que estos campos son int | None
        from typing import cast

        # ✅ Construir Value Objects estructurados
        ram = RamMetrics(
            total_mb=cast(Optional[int], metricas["ram_total_mb"]),
            used_mb=cast(Optional[int], metricas["ram_used_mb"]),
            usage_percent=cast(Optional[float], metricas["ram_usage_percent"]),
            total_unit=cast(Optional[str], metricas["ram_total_unit"]),
            used_unit=cast(Optional[str], metricas["ram_used_unit"]),
        )

        disk = DiskMetrics(
            total_gb=cast(Optional[float], metricas["disk_total_gb"]),
            used_gb=cast(Optional[float], metricas["disk_used_gb"]),
            usage_percent=cast(Optional[float], metricas["disk_usage_percent"]),
            total_unit=cast(Optional[str], metricas["disk_total_unit"]),
            used_unit=cast(Optional[str], metricas["disk_used_unit"]),
        )

        cpu = CpuMetrics(
            usage_percent=cast(Optional[float], metricas["cpu_usage_percent"]),
        )

        system_load = SystemLoadMetrics(
            load_1min=cast(Optional[float], metricas["load_1min"]),
            load_5min=cast(Optional[float], metricas["load_5min"]),
            load_15min=cast(Optional[float], metricas["load_15min"]),
        )

        return cls(
            id=uuid4(),
            hostname=hostname.strip(),
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            execution_time_seconds=round(execution_time_seconds, 3),
            executed_at=executed_at or now,
            created_at=now,
            ram=ram,
            disk=disk,
            cpu=cpu,
            system_load=system_load,
            process_count=cast(Optional[int], metricas["process_count"]),
            uptime_seconds=cast(Optional[int], metricas["uptime_seconds"]),
        )

    def __str__(self) -> str:
        status = "✅ OK" if self.success else "❌ FALLIDO"
        return (
            f"[{self.id}] {self.hostname} | {status} | {self.execution_time_seconds}s"
        )
