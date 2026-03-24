"""
Tests unitarios para el módulo de logging mejorado de robots.

Verifica las funciones de utilidad para logs más visuales y trazables.
"""

import pytest
from unittest.mock import patch, MagicMock
from core.robot_logging import (
    LogSymbols,
    get_robot_emoji,
    format_run_context,
    log_robot_start,
    log_robot_end,
    log_step,
    log_semaphore_status,
)


class TestLogSymbols:
    """Tests para la clase LogSymbols."""

    def test_log_symbols_has_required_attributes(self):
        """✅ LogSymbols tiene todos los atributos requeridos."""
        # Assert - Estados
        assert hasattr(LogSymbols, "START")
        assert hasattr(LogSymbols, "SUCCESS")
        assert hasattr(LogSymbols, "ERROR")
        assert hasattr(LogSymbols, "WARNING")
        assert hasattr(LogSymbols, "WAITING")
        assert hasattr(LogSymbols, "INFO")

        # Assert - Tipos de robot
        assert hasattr(LogSymbols, "ROBOT")
        assert hasattr(LogSymbols, "STANDINGS")
        assert hasattr(LogSymbols, "ODDS")
        assert hasattr(LogSymbols, "CALENDAR")

        # Assert - Acciones
        assert hasattr(LogSymbols, "SCRAPING")
        assert hasattr(LogSymbols, "SAVE")
        assert hasattr(LogSymbols, "NETWORK")
        assert hasattr(LogSymbols, "PARSER")
        assert hasattr(LogSymbols, "SEMAPHORE")

        # Assert - Contexto
        assert hasattr(LogSymbols, "RUN_ID")
        assert hasattr(LogSymbols, "TORNEO")
        assert hasattr(LogSymbols, "FUENTE")
        assert hasattr(LogSymbols, "TIME")


class TestGetRobotEmoji:
    """Tests para la función get_robot_emoji."""

    def test_get_robot_emoji_standings(self):
        """✅ Retorna emoji de standings para tipo standings."""
        # Act
        emoji = get_robot_emoji("standings")

        # Assert
        assert emoji == LogSymbols.STANDINGS

    def test_get_robot_emoji_odds(self):
        """✅ Retorna emoji de odds para tipo odds."""
        # Act
        emoji = get_robot_emoji("odds_wplay")

        # Assert
        assert emoji == LogSymbols.ODDS

    def test_get_robot_emoji_calendar(self):
        """✅ Retorna emoji de calendar para tipo calendar."""
        # Act
        emoji = get_robot_emoji("calendar")

        # Assert
        assert emoji == LogSymbols.CALENDAR

    def test_get_robot_emoji_unknown(self):
        """✅ Retorna emoji genérico para tipo desconocido."""
        # Act
        emoji = get_robot_emoji("unknown_type")

        # Assert
        assert emoji == LogSymbols.ROBOT

    def test_get_robot_emoji_case_insensitive(self):
        """✅ Es insensible a mayúsculas/minúsculas."""
        # Act
        emoji_upper = get_robot_emoji("STANDINGS")
        emoji_lower = get_robot_emoji("standings")
        emoji_mixed = get_robot_emoji("Standings")

        # Assert
        assert emoji_upper == emoji_lower == emoji_mixed == LogSymbols.STANDINGS


class TestFormatRunContext:
    """Tests para la función format_run_context."""

    def test_format_run_context_basic(self):
        """✅ Formatea el contexto de ejecución correctamente."""
        # Arrange
        run_id = "12345678-1234-1234-1234-123456789012"
        robot_type = "standings"
        torneo_nombre = "Liga BetPlay"

        # Act
        result = format_run_context(run_id, robot_type, torneo_nombre)

        # Assert
        assert "📊" in result  # Emoji de standings
        assert "12345678" in result  # Primeros 8 caracteres del run_id
        assert "Liga BetPlay" in result

    def test_format_run_context_short_run_id(self):
        """✅ Maneja run_id corto correctamente."""
        # Arrange
        run_id = "1234"
        robot_type = "calendar"
        torneo_nombre = "Copa Libertadores"

        # Act
        result = format_run_context(run_id, robot_type, torneo_nombre)

        # Assert
        assert "1234" in result
        assert "Copa Libertadores" in result


class TestLogRobotStart:
    """Tests para la función log_robot_start."""

    @patch("core.robot_logging.logger")
    def test_log_robot_start_calls_logger(self, mock_logger):
        """✅ Llama a logger.info con el formato correcto."""
        # Arrange
        run_id = "12345678-1234-1234-1234-123456789012"
        robot_type = "standings"
        robot_class_name = "StandingsRobot"
        torneo_nombre = "Liga BetPlay"
        fuente_name = "FlashScore"
        detalle_id = 123
        url = "https://example.com"

        # Act
        log_robot_start(
            run_id=run_id,
            robot_type=robot_type,
            robot_class_name=robot_class_name,
            torneo_nombre=torneo_nombre,
            fuente_name=fuente_name,
            detalle_id=detalle_id,
            url=url,
        )

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "INICIANDO ROBOT" in call_args
        assert robot_class_name in call_args
        assert torneo_nombre in call_args
        assert fuente_name in call_args


class TestLogRobotEnd:
    """Tests para la función log_robot_end."""

    @patch("core.robot_logging.logger")
    def test_log_robot_end_success(self, mock_logger):
        """✅ Llama a logger.info para éxito."""
        # Arrange
        run_id = "12345678-1234-1234-1234-123456789012"
        robot_type = "standings"
        robot_class_name = "StandingsRobot"
        torneo_nombre = "Liga BetPlay"

        # Act
        log_robot_end(
            run_id=run_id,
            robot_type=robot_type,
            robot_class_name=robot_class_name,
            torneo_nombre=torneo_nombre,
            success=True,
        )

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "COMPLETADO" in call_args
        assert robot_class_name in call_args

    @patch("core.robot_logging.logger")
    def test_log_robot_end_error(self, mock_logger):
        """✅ Llama a logger.error para error."""
        # Arrange
        run_id = "12345678-1234-1234-1234-123456789012"
        robot_type = "odds_wplay"
        robot_class_name = "OddsWPlayRobot"
        torneo_nombre = "Premier League"
        error = Exception("Test error")

        # Act
        log_robot_end(
            run_id=run_id,
            robot_type=robot_type,
            robot_class_name=robot_class_name,
            torneo_nombre=torneo_nombre,
            success=False,
            error=error,
        )

        # Assert
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "FALLÓ" in call_args
        assert "Test error" in call_args


class TestLogStep:
    """Tests para la función log_step."""

    @patch("core.robot_logging.logger")
    def test_log_step_info(self, mock_logger):
        """✅ Llama a logger.info para nivel info."""
        # Arrange
        robot_id = "Robot-STANDINGS"
        run_id = "12345678-1234-1234-1234-123456789012"
        step = "SCRAPING"
        message = "Extrayendo datos"

        # Act
        log_step(
            robot_id=robot_id,
            run_id=run_id,
            step=step,
            message=message,
            level="info",
        )

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert robot_id in call_args
        assert step in call_args
        assert message in call_args

    @patch("core.robot_logging.logger")
    def test_log_step_warning(self, mock_logger):
        """✅ Llama a logger.warning para nivel warning."""
        # Arrange
        robot_id = "Robot-ODDS"
        run_id = "12345678-1234-1234-1234-123456789012"
        step = "TIMEOUT"
        message = "Timeout alcanzado"

        # Act
        log_step(
            robot_id=robot_id,
            run_id=run_id,
            step=step,
            message=message,
            level="warning",
        )

        # Assert
        mock_logger.warning.assert_called_once()

    @patch("core.robot_logging.logger")
    def test_log_step_error(self, mock_logger):
        """✅ Llama a logger.error para nivel error."""
        # Arrange
        robot_id = "Robot-CALENDAR"
        run_id = "12345678-1234-1234-1234-123456789012"
        step = "PARSING"
        message = "Error parseando HTML"

        # Act
        log_step(
            robot_id=robot_id,
            run_id=run_id,
            step=step,
            message=message,
            level="error",
        )

        # Assert
        mock_logger.error.assert_called_once()


class TestLogSemaphoreStatus:
    """Tests para la función log_semaphore_status."""

    @patch("core.robot_logging.logger")
    def test_log_semaphore_status_configured(self, mock_logger):
        """✅ Loggea estado del semáforo configurado."""
        # Arrange
        robot_type = "standings"
        concurrency = 3

        # Act
        log_semaphore_status(
            robot_type=robot_type,
            concurrency=concurrency,
            waiting=False,
        )

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "Semáforo configurado" in call_args
        assert str(concurrency) in call_args

    @patch("core.robot_logging.logger")
    def test_log_semaphore_status_waiting(self, mock_logger):
        """✅ Loggea estado de espera del semáforo."""
        # Arrange
        robot_type = "odds_wplay"
        concurrency = 1

        # Act
        log_semaphore_status(
            robot_type=robot_type,
            concurrency=concurrency,
            waiting=True,
        )

        # Assert
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "esperando cupo" in call_args
