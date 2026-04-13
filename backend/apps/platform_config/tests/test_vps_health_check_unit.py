from __future__ import annotations
import pytest
from datetime import datetime
from typing import Dict, Any, Optional

from backend.apps.platform_config.domain.entities.vps_health_check import (
    VpsHealthCheck,
    VpsSystemInfo,
    VpsMemoryMetrics,
    VpsCpuMetrics,
    VpsDiskMetrics,
    VpsNetworkMetrics,
)


@pytest.mark.unit
class TestVpsHealthCheckEntity:
    """Pruebas unitarias para la entidad de dominio VpsHealthCheck"""

    def create_test_health_check(
        self, overrides: Optional[Dict[str, Any]] = None
    ) -> VpsHealthCheck:
        """Crea una instancia de prueba con valores por defecto saludables"""
        defaults = {
            "server_identifier": "vps_tipsterbyte_jdiaz",
            "system_info": VpsSystemInfo(
                os_name="Ubuntu 22.04.4 LTS",
                hostname="tipsterbyte-prod",
                architecture="x86_64",
                kernel_version="5.15.0-97-generic",
                uptime_seconds=86400,
                load_average="0.5 0.3 0.2",
            ),
            "memory": VpsMemoryMetrics(
                total_bytes=8 * 1024 * 1024 * 1024,  # 8GB
                used_bytes=4 * 1024 * 1024 * 1024,  # 4GB
                free_bytes=2 * 1024 * 1024 * 1024,  # 2GB
                available_bytes=int(3.5 * 1024 * 1024 * 1024),  # 3.5GB
                usage_percent=50.0,
            ),
            "cpu": VpsCpuMetrics(
                cores_count=4, model_name="Intel Xeon E-2276G", usage_percent=25.0
            ),
            "disks": [
                VpsDiskMetrics(
                    mount_point="/",
                    total_bytes=100 * 1024 * 1024 * 1024,  # 100GB
                    used_bytes=40 * 1024 * 1024 * 1024,  # 40GB
                    free_bytes=60 * 1024 * 1024 * 1024,  # 60GB
                    usage_percent=40.0,
                )
            ],
            "network": VpsNetworkMetrics(
                public_ip="143.110.239.197", has_internet_connectivity=True
            ),
            "raw_response": '{"status": "ok"}',
            "success": True,
            "execution_duration_ms": 1250,
            "error_message": None,
        }

        if overrides:
            defaults.update(overrides)

        return VpsHealthCheck(**defaults)

    def test_entity_creation_successful(self):
        """Prueba que la entidad se crea correctamente con valores validos"""
        health_check = self.create_test_health_check()

        assert health_check.server_identifier == "vps_tipsterbyte_jdiaz"
        assert health_check.success is True
        assert health_check.id is not None
        assert isinstance(health_check.executed_at, datetime)

    def test_is_healthy_returns_true_when_all_ok(self):
        """Prueba que is_healthy() devuelve True cuando todos los parametros estan en limites aceptables"""
        health_check = self.create_test_health_check()

        assert health_check.is_healthy() is True

    def test_is_healthy_returns_false_when_memory_over_90(self):
        """Prueba que se marca como no saludable cuando memoria > 90%"""
        health_check = self.create_test_health_check(
            {
                "memory": VpsMemoryMetrics(
                    total_bytes=8 * 1024 * 1024 * 1024,
                    used_bytes=int(7.5 * 1024 * 1024 * 1024),
                    free_bytes=int(0.5 * 1024 * 1024 * 1024),
                    available_bytes=int(0.5 * 1024 * 1024 * 1024),
                    usage_percent=93.75,
                )
            }
        )

        assert health_check.is_healthy() is False

    def test_is_healthy_returns_false_when_disk_over_95(self):
        """Prueba que se marca como no saludable cuando algun disco > 95%"""
        health_check = self.create_test_health_check(
            {
                "disks": [
                    VpsDiskMetrics(
                        mount_point="/",
                        total_bytes=100 * 1024 * 1024 * 1024,
                        used_bytes=96 * 1024 * 1024 * 1024,
                        free_bytes=4 * 1024 * 1024 * 1024,
                        usage_percent=96.0,
                    )
                ]
            }
        )

        assert health_check.is_healthy() is False

    def test_is_healthy_returns_false_when_no_internet(self):
        """Prueba que se marca como no saludable cuando no hay conectividad"""
        health_check = self.create_test_health_check(
            {
                "network": VpsNetworkMetrics(
                    public_ip=None, has_internet_connectivity=False
                )
            }
        )

        assert health_check.is_healthy() is False

    def test_get_warnings_returns_empty_when_everything_ok(self):
        """Prueba que no hay advertencias cuando todo esta bien"""
        health_check = self.create_test_health_check()

        warnings = health_check.get_warnings()

        assert len(warnings) == 0

    def test_get_warnings_returns_memory_warning_when_over_80(self):
        """Prueba que genera advertencia de memoria cuando > 80%"""
        health_check = self.create_test_health_check(
            {
                "memory": VpsMemoryMetrics(
                    total_bytes=8 * 1024 * 1024 * 1024,
                    used_bytes=int(6.8 * 1024 * 1024 * 1024),
                    free_bytes=int(1.2 * 1024 * 1024 * 1024),
                    available_bytes=int(1.2 * 1024 * 1024 * 1024),
                    usage_percent=85.0,
                )
            }
        )

        warnings = health_check.get_warnings()

        assert len(warnings) == 1
        assert "Memoria alta: 85.0%" in warnings[0]

    def test_get_warnings_returns_disk_warning_when_over_80(self):
        """Prueba que genera advertencia de disco cuando > 80%"""
        health_check = self.create_test_health_check(
            {
                "disks": [
                    VpsDiskMetrics(
                        mount_point="/",
                        total_bytes=100 * 1024 * 1024 * 1024,
                        used_bytes=85 * 1024 * 1024 * 1024,
                        free_bytes=15 * 1024 * 1024 * 1024,
                        usage_percent=85.0,
                    )
                ]
            }
        )

        warnings = health_check.get_warnings()

        assert len(warnings) == 1
        assert "Disco / alto: 85.0%" in warnings[0]

    def test_get_warnings_returns_multiple_warnings(self):
        """Prueba que devuelve multiples advertencias cuando varios parametros estan altos"""
        health_check = self.create_test_health_check(
            {
                "memory": VpsMemoryMetrics(
                    total_bytes=8 * 1024 * 1024 * 1024,
                    used_bytes=int(6.8 * 1024 * 1024 * 1024),
                    free_bytes=int(1.2 * 1024 * 1024 * 1024),
                    available_bytes=int(1.2 * 1024 * 1024 * 1024),
                    usage_percent=85.0,
                ),
                "cpu": VpsCpuMetrics(
                    cores_count=4, model_name="Intel Xeon E-2276G", usage_percent=82.0
                ),
                "disks": [
                    VpsDiskMetrics(
                        mount_point="/",
                        total_bytes=100 * 1024 * 1024 * 1024,
                        used_bytes=85 * 1024 * 1024 * 1024,
                        free_bytes=15 * 1024 * 1024 * 1024,
                        usage_percent=85.0,
                    )
                ],
            }
        )

        warnings = health_check.get_warnings()

        assert len(warnings) == 3
        assert any("Memoria alta" in w for w in warnings)
        assert any("Disco / alto" in w for w in warnings)
        assert any("CPU alta" in w for w in warnings)
