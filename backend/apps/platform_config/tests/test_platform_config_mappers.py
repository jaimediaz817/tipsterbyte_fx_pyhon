"""
Pruebas unitarias para los mappers de platform_config
Estas pruebas garantizan que cualquier cambio en los mappers rompa
explícitamente y sirva de alerta temprana
"""

from __future__ import annotations
from datetime import datetime
from unittest.mock import MagicMock

from apps.platform_config.infrastructure.mappers import (
    map_process_from_model,
    map_scheduled_process_config_from_model,
)


class TestProcessMapper:
    def test_map_process_from_model_with_all_fields(self):
        """Prueba que el mapper procese correctamente todos los campos"""
        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.code = "TEST_PROCESS_001"
        mock_model.name = "Proceso de Prueba"
        mock_model.is_active = True
        mock_model.description = "Descripción del proceso de prueba"
        mock_model.created_at = datetime(2026, 1, 1, 10, 0, 0)
        mock_model.updated_at = datetime(2026, 1, 2, 11, 0, 0)

        result = map_process_from_model(mock_model)

        assert result is not None
        assert result.id == 1
        assert result.code == "TEST_PROCESS_001"
        assert result.name == "Proceso de Prueba"
        assert result.is_active is True
        assert result.description == "Descripción del proceso de prueba"
        assert result.created_at == datetime(2026, 1, 1, 10, 0, 0)
        assert result.updated_at == datetime(2026, 1, 2, 11, 0, 0)

    def test_map_process_from_model_with_null_fields(self):
        """Prueba que el mapper maneje correctamente campos nulos"""
        mock_model = MagicMock()
        mock_model.id = 2
        mock_model.code = "TEST_PROCESS_002"
        mock_model.name = "Proceso Sin Descripción"
        mock_model.is_active = False
        mock_model.description = None
        mock_model.created_at = None
        mock_model.updated_at = None

        result = map_process_from_model(mock_model)

        assert result is not None
        assert result.description is None
        assert result.created_at is None
        assert result.updated_at is None

    def test_map_process_from_model_none_input(self):
        """Prueba que el mapper retorne None cuando se pasa None"""
        result = map_process_from_model(None)
        assert result is None

    def test_map_process_from_model_missing_fields_defaults(self):
        """Prueba valores por defecto cuando faltan campos en el modelo"""
        mock_model = MagicMock(spec=[])  # Sin atributos

        result = map_process_from_model(mock_model)

        assert result is not None
        assert result.id == 0
        assert result.code == ""
        assert result.name == ""
        assert result.is_active is False


class TestScheduledProcessConfigMapper:
    def test_map_scheduled_process_config_from_model_all_fields(self):
        """Prueba mapeo completo de ScheduledProcessConfig"""
        mock_model = MagicMock()
        mock_model.process_name = "cleanup_logs_job"
        mock_model.cron_expression = "0 0 * * *"
        mock_model.enabled = True
        mock_model.description = "Tarea de limpieza de logs diaria"
        mock_model.created_at = datetime(2026, 1, 1)
        mock_model.updated_at = datetime(2026, 1, 15)

        result = map_scheduled_process_config_from_model(mock_model)

        assert result.process_name == "cleanup_logs_job"
        assert result.cron_expression == "0 0 * * *"
        assert result.enabled is True
        assert result.description == "Tarea de limpieza de logs diaria"
        assert result.created_at == datetime(2026, 1, 1)
        assert result.updated_at == datetime(2026, 1, 15)

    def test_map_scheduled_process_config_default_values(self):
        """Prueba valores por defecto cuando no existen campos"""
        mock_model = MagicMock(spec=[])

        result = map_scheduled_process_config_from_model(mock_model)

        assert result.process_name == ""
        assert result.cron_expression == ""
        assert result.enabled is False
        assert result.description is None
