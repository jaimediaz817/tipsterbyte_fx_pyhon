from __future__ import annotations
from datetime import datetime, timezone
from typing import Annotated, Optional, Dict, Any
from beanie import Document, Indexed
from pydantic import Field


class VpsMemoryMetrics(Document):
    total_bytes: int
    used_bytes: int
    free_bytes: int
    available_bytes: int
    usage_percent: float


class VpsDiskMetrics(Document):
    mount_point: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    usage_percent: float


class VpsCpuMetrics(Document):
    cores_count: int
    model_name: str
    usage_percent: float


class VpsNetworkMetrics(Document):
    public_ip: Optional[str] = None
    has_internet_connectivity: bool


class VpsSystemInfo(Document):
    os_name: str
    hostname: str
    architecture: str
    kernel_version: str
    uptime_seconds: int
    load_average: str


class VpsHealthCheckModel(Document):
    """
    Modelo Beanie para MongoDB - Resultado completo de chequeo de salud de VPS
    Almacena metricas historicas de estado del servidor remoto
    """

    server_identifier: Annotated[str, Indexed(str)]
    executed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    system_info: VpsSystemInfo
    memory: VpsMemoryMetrics
    cpu: VpsCpuMetrics
    disks: list[VpsDiskMetrics]
    network: VpsNetworkMetrics

    raw_response: str
    success: bool
    execution_duration_ms: int
    error_message: Optional[str] = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "vps_health_checks"
        indexes = [
            "server_identifier",
            "executed_at",
            "success",
            [("server_identifier", "executed_at")],
        ]
