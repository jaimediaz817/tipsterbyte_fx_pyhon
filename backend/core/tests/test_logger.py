"""
Tests unitarios para el módulo logger.
Cubre: InterceptHandler, _safe_add_sink, configure_logging y funciones auxiliares.
"""

import logging
import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path


class TestInterceptHandler:
    """Tests para la clase InterceptHandler."""

    def test_emit_with_valid_level_real(self):
        """Test que ejecuta emit() real con nivel válido."""
        from core.logger import InterceptHandler

        handler = InterceptHandler()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

    def test_emit_with_custom_level(self):
        """Test que ejecuta emit() con nivel custom para cubrir ValueError path."""
        from core.logger import InterceptHandler

        handler = InterceptHandler()
        record = logging.LogRecord(
            name="test_logger",
            level=25,
            pathname="test.py",
            lineno=10,
            msg="Custom level message",
            args=(),
            exc_info=None,
        )
        record.levelname = "CUSTOM"

        handler.emit(record)

    def test_emit_with_exception_info(self):
        """Test que ejecuta emit() con exc_info."""
        from core.logger import InterceptHandler

        handler = InterceptHandler()
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error message",
            args=(),
            exc_info=exc_info,
        )

        handler.emit(record)

    def test_emit_from_logging_module(self):
        """Test que ejecuta emit() desde módulo logging para cubrir while loop."""
        from core.logger import InterceptHandler
        import logging

        handler = InterceptHandler()

        # Crear record con pathname del módulo logging
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=logging.__file__,
            lineno=10,
            msg="Test from logging module",
            args=(),
            exc_info=None,
        )

        handler.emit(record)


class TestSafeAddSink:
    """Tests para la función _safe_add_sink."""

    def test_safe_add_sink_success(self):
        """Test que _safe_add_sink agrega sink correctamente."""
        from core.logger import _safe_add_sink
        from loguru import logger
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            log_path = Path(temp_dir) / "test.log"
            _safe_add_sink(log_path, rotation="10 MB")
        finally:
            logger.remove()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_safe_add_sink_with_invalid_rotation(self):
        """Test que _safe_add_sink maneja rotación inválida."""
        from core.logger import _safe_add_sink
        from loguru import logger
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            log_path = Path(temp_dir) / "test.log"
            # Usar rotación inválida para forzar el path de error
            _safe_add_sink(log_path, rotation="invalid_rotation_value")
        finally:
            logger.remove()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_safe_add_sink_with_invalid_path(self):
        """Test que _safe_add_sink maneja path inválido."""
        from core.logger import _safe_add_sink
        from loguru import logger

        # Path inválido que causará error
        invalid_path = Path("/invalid/path/that/does/not/exist/test.log")
        _safe_add_sink(invalid_path, rotation="10 MB")


class TestConfigureLogging:
    """Tests para la función configure_logging."""

    def test_configure_logging_real_execution(self):
        """Test que ejecuta configure_logging real."""
        from core.logger import configure_logging
        from loguru import logger
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            with patch("core.logger.LOGS_ROOT", Path(temp_dir)):
                with patch("core.logger.settings") as mock_settings:
                    mock_settings.LOG_LEVEL = "INFO"
                    configure_logging()
                    logger.info("Test message")
        finally:
            logger.remove()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_configure_logging_with_filters(self):
        """Test que ejecuta configure_logging y prueba los filtros."""
        from core.logger import configure_logging
        from loguru import logger
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            with patch("core.logger.LOGS_ROOT", Path(temp_dir)):
                with patch("core.logger.settings") as mock_settings:
                    mock_settings.LOG_LEVEL = "DEBUG"
                    configure_logging()

                    # Probar diferentes tipos de logs para activar filtros
                    logger.info("General info message")
                    logger.debug("Debug message")
                    logger.error("Error message")

                    # Crear un logger de core para activar system_filter
                    core_logger = logging.getLogger("core.config")
                    core_logger.info("Core config message")

                    # Crear un logger de scheduler
                    scheduler_logger = logging.getLogger("core.scheduler.jobs")
                    scheduler_logger.info("Scheduler message")

                    # Crear un logger de apps
                    apps_logger = logging.getLogger("apps.leagues_manager")
                    apps_logger.info("Apps message")
        finally:
            logger.remove()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_configure_logging_with_robots(self):
        """Test que ejecuta configure_logging y prueba filtro de robots."""
        from core.logger import configure_logging
        from loguru import logger
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()
        try:
            with patch("core.logger.LOGS_ROOT", Path(temp_dir)):
                with patch("core.logger.settings") as mock_settings:
                    mock_settings.LOG_LEVEL = "INFO"
                    configure_logging()

                    # Crear un logger de robots
                    robot_logger = logging.getLogger(
                        "apps.leagues_manager.robots.standings"
                    )
                    robot_logger.info("Robot message")
        finally:
            logger.remove()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
