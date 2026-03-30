"""
Tests unitarios para excepciones personalizadas de TipsterByte FX.
"""

import pytest
from core.exceptions import (
    TipsterByteException,
    DatabaseException,
    MongoDBException,
    MongoDBConnectionException,
    MongoDBWriteException,
    MongoDBReadException,
    SessionLogException,
    SessionLogWriteException,
    SessionLogReadException,
    ProcessException,
    ProcessNotFoundException,
    ProcessInactiveException,
    ProcessRunCreationException,
    NoActiveJobsException,
    FuenteException,
    FuenteNotFoundException,
    FuenteInactiveException,
    DetalleInactiveException,
    RobotException,
    RobotNotFoundException,
    ScrapingException,
    ScrapingTimeoutException,
    ScrapingParsingException,
    ConcurrencyException,
    SemaphoreTimeoutException,
    MaxRetriesExceededException,
)


# =====================================================
# TESTS: Excepción Base
# =====================================================


def test_tipster_byte_exception_to_dict():
    """✅ La excepción base debe convertirse a diccionario correctamente."""
    exc = TipsterByteException(
        message="Error de prueba",
        error_code="TEST_ERROR",
        status_code=400,
        context={"key": "value"},
        suggestion="Sugerencia de prueba",
    )

    result = exc.to_dict()

    assert result["error_code"] == "TEST_ERROR"
    assert result["message"] == "Error de prueba"
    assert result["status_code"] == 400
    assert result["context"] == {"key": "value"}
    assert result["suggestion"] == "Sugerencia de prueba"


def test_tipster_byte_exception_str():
    """✅ La excepción base debe tener representación string correcta."""
    exc = TipsterByteException(
        message="Error de prueba",
        error_code="TEST_ERROR",
        suggestion="Sugerencia de prueba",
    )

    result = str(exc)

    assert "[TEST_ERROR]" in result
    assert "Error de prueba" in result
    assert "Sugerencia: Sugerencia de prueba" in result


def test_tipster_byte_exception_without_suggestion():
    """✅ La excepción base debe funcionar sin sugerencia."""
    exc = TipsterByteException(
        message="Error de prueba",
        error_code="TEST_ERROR",
    )

    result = exc.to_dict()

    assert "suggestion" not in result
    assert str(exc) == "[TEST_ERROR] Error de prueba"


# =====================================================
# TESTS: Excepciones de Proceso
# =====================================================


def test_process_not_found_exception():
    """✅ ProcessNotFoundException debe tener contexto correcto."""
    exc = ProcessNotFoundException("PROCESS_TEST")

    assert exc.error_code == "PROCESS_NOT_FOUND"
    assert exc.status_code == 404
    assert exc.context["process_code"] == "PROCESS_TEST"
    assert "PROCESS_TEST" in exc.message


def test_process_inactive_exception():
    """✅ ProcessInactiveException debe tener contexto correcto."""
    exc = ProcessInactiveException("PROCESS_TEST", 42)

    assert exc.error_code == "PROCESS_INACTIVE"
    assert exc.status_code == 400
    assert exc.context["process_code"] == "PROCESS_TEST"
    assert exc.context["process_id"] == 42
    assert exc.context["is_active"] is False


def test_process_run_creation_exception():
    """✅ ProcessRunCreationException debe tener contexto correcto."""
    exc = ProcessRunCreationException("PROCESS_TEST", "run_123")

    assert exc.error_code == "PROCESS_RUN_CREATION_FAILED"
    assert exc.status_code == 500
    assert exc.context["process_code"] == "PROCESS_TEST"
    assert exc.context["run_id"] == "run_123"


def test_no_active_jobs_exception():
    """✅ NoActiveJobsException debe tener status 200 (informativo)."""
    exc = NoActiveJobsException("PROCESS_TEST")

    assert exc.error_code == "NO_ACTIVE_JOBS"
    assert exc.status_code == 200  # No es error crítico
    assert exc.context["process_code"] == "PROCESS_TEST"


# =====================================================
# TESTS: Excepciones de Fuente
# =====================================================


def test_fuente_not_found_exception():
    """✅ FuenteNotFoundException debe aceptar cualquier tipo de ID."""
    # Con int
    exc1 = FuenteNotFoundException(42)
    assert exc1.error_code == "FUENTE_NOT_FOUND"
    assert exc1.context["detalle_id"] == "42"

    # Con string (simulando Column de SQLAlchemy)
    exc2 = FuenteNotFoundException("column_id_123")
    assert exc2.error_code == "FUENTE_NOT_FOUND"
    assert exc2.context["detalle_id"] == "column_id_123"


def test_fuente_inactive_exception():
    """✅ FuenteInactiveException debe tener contexto correcto."""
    exc = FuenteInactiveException(1, "FlashScore")

    assert exc.error_code == "FUENTE_INACTIVE"
    assert exc.status_code == 400
    assert exc.context["fuente_id"] == 1
    assert exc.context["fuente_name"] == "FlashScore"
    assert exc.context["is_active"] is False


def test_detalle_inactive_exception():
    """✅ DetalleInactiveException debe tener contexto correcto."""
    exc = DetalleInactiveException(10, "LaLiga", "FlashScore")

    assert exc.error_code == "DETALLE_INACTIVE"
    assert exc.status_code == 400
    assert exc.context["detalle_id"] == 10
    assert exc.context["torneo_nombre"] == "LaLiga"
    assert exc.context["fuente_name"] == "FlashScore"
    assert exc.context["is_active"] is False


# =====================================================
# TESTS: Excepciones de Robot
# =====================================================


def test_robot_not_found_exception():
    """✅ RobotNotFoundException debe tener contexto correcto."""
    exc = RobotNotFoundException("news")

    assert exc.error_code == "ROBOT_NOT_FOUND"
    assert exc.status_code == 500
    assert exc.context["robot_type"] == "news"
    assert exc.suggestion is not None
    assert "@register_robot" in exc.suggestion


def test_scraping_exception():
    """✅ ScrapingException debe incluir error original."""
    original_error = ValueError("Error de parsing")
    exc = ScrapingException(
        robot_id="Robot-STANDINGS",
        url="https://example.com",
        original_error=original_error,
    )

    assert exc.error_code == "SCRAPING_ERROR"
    assert exc.status_code == 500
    assert exc.context["robot_id"] == "Robot-STANDINGS"
    assert exc.context["url"] == "https://example.com"
    assert exc.context["original_error_type"] == "ValueError"
    assert exc.context["original_error_message"] == "Error de parsing"


def test_scraping_exception_without_original_error():
    """✅ ScrapingException debe funcionar sin error original."""
    exc = ScrapingException(
        robot_id="Robot-STANDINGS",
        url="https://example.com",
    )

    assert exc.error_code == "SCRAPING_ERROR"
    assert "original_error_type" not in exc.context


def test_scraping_timeout_exception():
    """✅ ScrapingTimeoutException debe tener contexto correcto."""
    exc = ScrapingTimeoutException("Robot-STANDINGS", "https://example.com", 30)

    assert exc.error_code == "SCRAPING_TIMEOUT"
    assert exc.status_code == 504
    assert exc.context["robot_id"] == "Robot-STANDINGS"
    assert exc.context["url"] == "https://example.com"
    assert exc.context["timeout_seconds"] == 30


def test_scraping_parsing_exception():
    """✅ ScrapingParsingException debe tener contexto correcto."""
    exc = ScrapingParsingException(
        "Robot-STANDINGS", "https://example.com", "div.table"
    )

    assert exc.error_code == "SCRAPING_PARSING_ERROR"
    assert exc.status_code == 500
    assert exc.context["robot_id"] == "Robot-STANDINGS"
    assert exc.context["url"] == "https://example.com"
    assert exc.context["selector"] == "div.table"


# =====================================================
# TESTS: Excepciones de Concurrencia
# =====================================================


def test_semaphore_timeout_exception():
    """✅ SemaphoreTimeoutException debe tener contexto correcto."""
    exc = SemaphoreTimeoutException("standings", 60)

    assert exc.error_code == "SEMAPHORE_TIMEOUT"
    assert exc.status_code == 503
    assert exc.context["robot_type"] == "standings"
    assert exc.context["wait_time_seconds"] == 60


def test_max_retries_exceeded_exception():
    """✅ MaxRetriesExceededException debe incluir último error."""
    last_error = ConnectionError("Timeout de conexión")
    exc = MaxRetriesExceededException("Robot-STANDINGS", 3, last_error)

    assert exc.error_code == "MAX_RETRIES_EXCEEDED"
    assert exc.status_code == 500
    assert exc.context["robot_id"] == "Robot-STANDINGS"
    assert exc.context["max_retries"] == 3
    assert exc.context["last_error_type"] == "ConnectionError"
    assert exc.context["last_error_message"] == "Timeout de conexión"


# =====================================================
# TESTS: Herencia de Excepciones
# =====================================================


def test_process_exceptions_inherit_from_process_exception():
    """✅ Excepciones de proceso deben heredar de ProcessException."""
    assert issubclass(ProcessNotFoundException, ProcessException)
    assert issubclass(ProcessInactiveException, ProcessException)
    assert issubclass(ProcessRunCreationException, ProcessException)
    assert issubclass(NoActiveJobsException, ProcessException)


def test_fuente_exceptions_inherit_from_fuente_exception():
    """✅ Excepciones de fuente deben heredar de FuenteException."""
    assert issubclass(FuenteNotFoundException, FuenteException)
    assert issubclass(FuenteInactiveException, FuenteException)
    assert issubclass(DetalleInactiveException, FuenteException)


def test_robot_exceptions_inherit_from_robot_exception():
    """✅ Excepciones de robot deben heredar de RobotException."""
    assert issubclass(RobotNotFoundException, RobotException)
    assert issubclass(ScrapingException, RobotException)
    assert issubclass(ScrapingTimeoutException, RobotException)
    assert issubclass(ScrapingParsingException, RobotException)


def test_concurrency_exceptions_inherit_from_concurrency_exception():
    """✅ Excepciones de concurrencia deben heredar de ConcurrencyException."""
    assert issubclass(SemaphoreTimeoutException, ConcurrencyException)
    assert issubclass(MaxRetriesExceededException, ConcurrencyException)


def test_all_exceptions_inherit_from_tipster_byte_exception():
    """✅ Todas las excepciones deben heredar de TipsterByteException."""
    assert issubclass(DatabaseException, TipsterByteException)
    assert issubclass(SessionLogException, TipsterByteException)
    assert issubclass(ProcessException, TipsterByteException)
    assert issubclass(FuenteException, TipsterByteException)
    assert issubclass(RobotException, TipsterByteException)
    assert issubclass(ConcurrencyException, TipsterByteException)


# =====================================================
# TESTS: Excepciones de MongoDB
# =====================================================


def test_mongodb_connection_exception():
    """✅ MongoDBConnectionException debe tener contexto correcto."""
    exc = MongoDBConnectionException(
        host="localhost",
        port=27017,
    )

    assert exc.error_code == "MONGODB_CONNECTION_ERROR"
    assert exc.status_code == 500
    assert exc.host == "localhost"
    assert exc.port == 27017
    assert "MongoDB no está disponible" in exc.message


def test_mongodb_write_exception():
    """✅ MongoDBWriteException debe tener contexto correcto."""
    exc = MongoDBWriteException(
        collection="session_logs",
    )

    assert exc.error_code == "MONGODB_WRITE_ERROR"
    assert exc.status_code == 500
    assert exc.collection == "session_logs"
    assert "Error al escribir en MongoDB" in exc.message


def test_mongodb_read_exception():
    """✅ MongoDBReadException debe tener contexto correcto."""
    exc = MongoDBReadException(
        collection="session_logs",
    )

    assert exc.error_code == "MONGODB_READ_ERROR"
    assert exc.status_code == 500
    assert exc.collection == "session_logs"
    assert "Error al leer de MongoDB" in exc.message


def test_mongodb_exceptions_inherit_from_mongodb_exception():
    """✅ Excepciones de MongoDB deben heredar de MongoDBException."""
    assert issubclass(MongoDBConnectionException, MongoDBException)
    assert issubclass(MongoDBWriteException, MongoDBException)
    assert issubclass(MongoDBReadException, MongoDBException)


def test_mongodb_exception_inherits_from_database_exception():
    """✅ MongoDBException debe heredar de DatabaseException."""
    assert issubclass(MongoDBException, DatabaseException)


# =====================================================
# TESTS: Excepciones de Session Log
# =====================================================


def test_session_log_write_exception():
    """✅ SessionLogWriteException debe tener contexto correcto."""
    exc = SessionLogWriteException(
        user_id="user_123",
        session_id="session_456",
    )

    assert exc.error_code == "SESSION_LOG_WRITE_ERROR"
    assert exc.status_code == 500
    assert exc.user_id == "user_123"
    assert exc.session_id == "session_456"
    assert "Error al escribir session log" in exc.message


def test_session_log_read_exception():
    """✅ SessionLogReadException debe tener contexto correcto."""
    exc = SessionLogReadException(
        user_id="user_123",
    )

    assert exc.error_code == "SESSION_LOG_READ_ERROR"
    assert exc.status_code == 500
    assert exc.user_id == "user_123"
    assert "Error al leer session logs" in exc.message


def test_session_log_exceptions_inherit_from_session_log_exception():
    """✅ Excepciones de Session Log deben heredar de SessionLogException."""
    assert issubclass(SessionLogWriteException, SessionLogException)
    assert issubclass(SessionLogReadException, SessionLogException)


def test_session_log_exception_inherits_from_tipster_byte_exception():
    """✅ SessionLogException debe heredar de TipsterByteException."""
    assert issubclass(SessionLogException, TipsterByteException)
