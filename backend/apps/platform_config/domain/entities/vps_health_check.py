from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from uuid import uuid4


@dataclass
class VpsMemoryMetrics:
    """Metricas de memoria RAM de la VPS"""

    total_bytes: int
    used_bytes: int
    free_bytes: int
    available_bytes: int
    usage_percent: float


@dataclass
class VpsDiskMetrics:
    """Metricas de disco de la VPS"""

    mount_point: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


@dataclass
class VpsCpuMetrics:
    """Metricas de CPU de la VPS"""

    cores_count: int
    model_name: str
    usage_percent: float


@dataclass
class VpsNetworkMetrics:
    """Metricas de red de la VPS"""

    public_ip: Optional[str]
    has_internet_connectivity: bool


@dataclass
class VpsSystemInfo:
    """Informacion basica del sistema operativo"""

    os_name: str
    hostname: str
    architecture: str
    kernel_version: str
    uptime_seconds: int
    load_average: str


@dataclass
class VpsHealthCheck:
    """Entidad de Dominio - Resultado completo de chequeo de salud de VPS"""

    # Campos obligatorios sin default primero
    server_identifier: str
    system_info: VpsSystemInfo
    memory: VpsMemoryMetrics
    cpu: VpsCpuMetrics
    disks: list[VpsDiskMetrics]
    network: VpsNetworkMetrics
    raw_response: str
    success: bool
    execution_duration_ms: int

    # Campos con default al final
    id: str = field(default_factory=lambda: str(uuid4()))
    executed_at: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_healthy(self) -> bool:
        """Indica si la VPS esta en estado saludable"""
        if not self.success:
            return False

        if self.memory.usage_percent > 90:
            return False

        if any(disk.usage_percent > 95 for disk in self.disks):
            return False

        if not self.network.has_internet_connectivity:
            return False

        return True

    def get_warnings(self) -> list[str]:
        """Devuelve lista de advertencias encontradas"""
        warnings = []

        if self.memory.usage_percent > 80:
            warnings.append(f"Memoria alta: {self.memory.usage_percent}%")

        for disk in self.disks:
            if disk.usage_percent > 80:
                warnings.append(f"Disco {disk.mount_point} alto: {disk.usage_percent}%")

        if self.cpu.usage_percent > 75:
            warnings.append(f"CPU alta: {self.cpu.usage_percent}%")

        return warnings
