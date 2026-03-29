"""Tests para SessionLog Model (sin inicialización de Beanie)"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone
from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog


class TestSessionLogModel:
    """Tests para el modelo SessionLog de MongoDB (unitarios, sin DB)"""

    def test_session_log_fields_exist(self):
        """Test que el modelo SessionLog tiene todos los campos esperados"""
        # Verificar que la clase tiene los campos definidos
        fields = SessionLog.model_fields

        assert "user_id" in fields
        assert "session_id" in fields
        assert "action" in fields
        assert "action_details" in fields
        assert "ip_address" in fields
        assert "user_agent" in fields
        assert "endpoint" in fields
        assert "method" in fields
        assert "status_code" in fields
        assert "response_time_ms" in fields
        assert "timestamp" in fields
        assert "duration_seconds" in fields

    def test_session_log_field_types(self):
        """Test que los campos tienen los tipos correctos"""
        fields = SessionLog.model_fields

        # Verificar tipos de campos
        assert fields["user_id"].annotation.__name__ == "UUID"
        assert fields["session_id"].annotation == str
        assert fields["action"].annotation == str
        assert fields["ip_address"].annotation == str
        assert fields["user_agent"].annotation == str
        assert fields["endpoint"].annotation == str
        assert fields["method"].annotation == str
        assert fields["status_code"].annotation == int
        assert fields["response_time_ms"].annotation == float
        # Optional[float] se representa como Union[float, None]
        assert fields["duration_seconds"].annotation == float | None

    def test_session_log_collection_name(self):
        """Test que el nombre de la colección es correcto"""
        assert SessionLog.Settings.name == "session_logs"

    def test_session_log_indexes_defined(self):
        """Test que los índices están definidos correctamente"""
        indexes = SessionLog.Settings.indexes

        assert "user_id" in indexes
        assert "session_id" in indexes
        assert "timestamp" in indexes
        assert "action" in indexes

        # Verificar índice compuesto
        compound_index = None
        for idx in indexes:
            if isinstance(idx, list):
                compound_index = idx
                break

        assert compound_index is not None
        assert ("user_id", 1) in compound_index
        assert ("timestamp", -1) in compound_index

    def test_session_log_docstring(self):
        """Test que el modelo tiene documentación"""
        assert SessionLog.__doc__ is not None
        assert (
            "bitácora" in SessionLog.__doc__.lower()
            or "sesión" in SessionLog.__doc__.lower()
        )
