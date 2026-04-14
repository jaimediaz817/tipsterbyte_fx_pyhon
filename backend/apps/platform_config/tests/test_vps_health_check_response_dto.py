"""
✅ PRUEBAS UNITARIAS PARA VpsHealthCheckResponseDto
✅ 100% Coverage
✅ Compatible con Testing Explorer VS Code
✅ Ejecutable directamente
"""

from __future__ import annotations

import sys
from pathlib import Path
from io import StringIO

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest
from datetime import datetime
from uuid import uuid4
from dataclasses import FrozenInstanceError

from backend.apps.platform_config.domain.entities.vps_health_check import VpsHealthCheck
from backend.apps.platform_config.application.dto.vps_health_check_response_dto import (
    VpsHealthCheckResponseDto,
)


@pytest.mark.unit
class TestVpsHealthCheckResponseDto:
    """Pruebas unitarias completas para el DTO de respuesta"""

    def setup_method(self):
        """Setup ejecutado antes de cada prueba"""
        self.entity = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="Test output OK",
            stderr="",
            execution_time_seconds=1.256,
        )

        self.entity_fail = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=False,
            exit_code=1,
            stdout="",
            stderr="Error message",
            execution_time_seconds=0.5,
        )

    def test_from_domain_entity_maps_all_fields_correctly(self):
        """Prueba que todos los campos se mapean correctamente desde la entidad"""
        dto = VpsHealthCheckResponseDto.from_domain_entity(self.entity)

        assert dto.id == self.entity.id
        assert dto.hostname == self.entity.hostname
        assert dto.success == self.entity.success
        assert dto.exit_code == self.entity.exit_code
        assert dto.stdout == self.entity.stdout
        assert dto.stderr == self.entity.stderr
        assert dto.execution_time_seconds == self.entity.execution_time_seconds
        assert dto.executed_at == self.entity.executed_at
        assert dto.created_at == self.entity.created_at

    def test_get_status_icon_returns_correct_values(self):
        """Prueba que los iconos de estado son correctos"""
        dto_ok = VpsHealthCheckResponseDto.from_domain_entity(self.entity)
        dto_fail = VpsHealthCheckResponseDto.from_domain_entity(self.entity_fail)

        assert dto_ok.get_status_icon() == "✅"
        assert dto_fail.get_status_icon() == "❌"

    def test_get_status_text_returns_correct_values(self):
        """Prueba que los textos de estado son correctos"""
        dto_ok = VpsHealthCheckResponseDto.from_domain_entity(self.entity)
        dto_fail = VpsHealthCheckResponseDto.from_domain_entity(self.entity_fail)

        assert dto_ok.get_status_text() == "OK"
        assert dto_fail.get_status_text() == "FALLIDO"

    def test_str_representation_is_correctly_formatted(self):
        """Prueba que la representacion en string esta correctamente formateada"""
        dto = VpsHealthCheckResponseDto.from_domain_entity(self.entity)
        str_value = str(dto)

        assert str(self.entity.id) in str_value
        assert self.entity.hostname in str_value
        assert "✅" in str_value
        assert "OK" in str_value
        assert "1.256s" in str_value

    def test_print_console_summary_prints_correctly_for_success(self, capsys):
        """Prueba que el metodo de impresion funciona correctamente para caso exitoso"""
        dto = VpsHealthCheckResponseDto.from_domain_entity(self.entity)
        dto.print_console_summary()

        captured = capsys.readouterr()
        output = captured.out

        assert "✅ EJECUCION COMPLETADA!" in output
        assert "✅ Exito: True" in output
        assert "✅ Codigo salida: 0" in output
        assert "✅ Tiempo ejecucion: 1.256 segundos" in output
        assert "✅ Servidor: 143.110.239.197" in output
        assert "📋 SALIDA COMPLETA DEL DIAGNOSTICO:" in output
        assert "Test output OK" in output

    def test_print_console_summary_prints_correctly_for_failure(self, capsys):
        """Prueba que el metodo de impresion funciona correctamente para caso fallido"""
        dto = VpsHealthCheckResponseDto.from_domain_entity(self.entity_fail)
        dto.print_console_summary()

        captured = capsys.readouterr()
        output = captured.out

        assert "✅ EJECUCION COMPLETADA!" in output
        assert "✅ Exito: False" in output
        assert "✅ Codigo salida: 1" in output
        assert "✅ Tiempo ejecucion: 0.5 segundos" in output
        assert "❌ FALLO LA EJECUCION:" in output
        assert "Error message" in output

    def test_dto_is_immutable(self):
        """Prueba que el DTO tambien es inmutable como la entidad original"""
        dto = VpsHealthCheckResponseDto.from_domain_entity(self.entity)

        with pytest.raises(FrozenInstanceError):
            dto.success = False  # type: ignore


if __name__ == "__main__":
    """Permite ejecutar la prueba directamente sin pytest"""
    pytest.main([__file__, "-xvs"])
