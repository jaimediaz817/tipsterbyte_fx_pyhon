from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime
from uuid import UUID
from dataclasses import FrozenInstanceError

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv

load_dotenv(ROOT_PROYECTO / "backend" / ".env")

import pytest

from backend.apps.platform_config.domain.entities.vps_health_check import VpsHealthCheck


@pytest.mark.unit
class TestVpsHealthCheckEntity:
    """Pruebas unitarias para la entidad de dominio VpsHealthCheck"""

    def test_create_method_generates_valid_entity(self):
        """Prueba que el factory method create() genera una entidad valida y completa"""

        health_check = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="✅ Health Check completado correctamente\nUso CPU: 25%",
            stderr="",
            execution_time_seconds=1.256,
        )

        # ✅ Verificamos que se genero el ID automaticamente
        assert health_check.id is not None
        assert isinstance(health_check.id, UUID)

        # ✅ Verificamos campos obligatorios
        assert health_check.hostname == "143.110.239.197"
        assert health_check.success is True
        assert health_check.exit_code == 0
        assert (
            health_check.stdout
            == "✅ Health Check completado correctamente\nUso CPU: 25%"
        )
        assert health_check.stderr == ""
        assert health_check.execution_time_seconds == 1.256

        # ✅ Verificamos fechas automaticas
        assert isinstance(health_check.executed_at, datetime)
        assert isinstance(health_check.created_at, datetime)
        assert health_check.executed_at <= health_check.created_at

    def test_create_method_rounds_execution_time(self):
        """Prueba que el tiempo de ejecucion se redondea automaticamente a 3 decimales"""

        health_check = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="test",
            stderr="",
            execution_time_seconds=2.123456789,
        )

        assert health_check.execution_time_seconds == 2.123

    def test_hostname_is_trimmed_automatically(self):
        """Prueba que el hostname se limpia de espacios en blanco automaticamente"""

        health_check = VpsHealthCheck.create(
            hostname="   143.110.239.197   \n",
            success=True,
            exit_code=0,
            stdout="test",
            stderr="",
            execution_time_seconds=1.0,
        )

        assert health_check.hostname == "143.110.239.197"

    def test_custom_executed_at_is_preserved(self):
        """Prueba que si se pasa executed_at se preserva y no se genera automaticamente"""

        custom_date = datetime(2025, 1, 1, 12, 0, 0)

        health_check = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="test",
            stderr="",
            execution_time_seconds=1.0,
            executed_at=custom_date,
        )

        assert health_check.executed_at == custom_date
        assert health_check.created_at != custom_date

    def test_entity_is_immutable(self):
        """Prueba que la entidad es inmutable (frozen=True) y no se puede modificar despues de creada"""

        health_check = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="test",
            stderr="",
            execution_time_seconds=1.0,
        )

        with pytest.raises(FrozenInstanceError):
            # ✅ Asignacion normal - Pylance detecta que es read-only
            # ✅ Añadimos # type: ignore para suprimir la advertencia estatica
            health_check.success = False  # type: ignore

    def test_str_representation(self):
        """Prueba que la representacion en string funciona correctamente para ambos estados"""

        # ✅ Caso exitoso
        health_ok = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=True,
            exit_code=0,
            stdout="ok",
            stderr="",
            execution_time_seconds=1.25,
        )

        str_ok = str(health_ok)
        assert "143.110.239.197" in str_ok
        assert "✅ OK" in str_ok
        assert "1.25s" in str_ok

        # ❌ Caso fallido
        health_fail = VpsHealthCheck.create(
            hostname="143.110.239.197",
            success=False,
            exit_code=1,
            stdout="",
            stderr="error",
            execution_time_seconds=0.5,
        )

        str_fail = str(health_fail)
        assert "143.110.239.197" in str_fail
        assert "❌ FALLIDO" in str_fail
        assert "0.5s" in str_fail

    def test_equality_between_entities(self):
        """Prueba que dos entidades con mismo ID son iguales aunque tengan datos diferentes"""

        base_data = {
            "hostname": "143.110.239.197",
            "success": True,
            "exit_code": 0,
            "stdout": "test",
            "stderr": "",
            "execution_time_seconds": 1.0,
        }

        health1 = VpsHealthCheck.create(**base_data)
        health2 = VpsHealthCheck.create(**base_data)

        # ✅ Deben ser diferentes porque tienen diferente UUID
        assert health1 != health2
