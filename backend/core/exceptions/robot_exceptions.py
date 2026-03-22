"""
Excepciones relacionadas con robots de extracción.

Estas excepciones se lanzan cuando hay errores relacionados
con la ejecución de robots de scraping.
"""

from typing import Optional
from core.exceptions.base import TipsterByteException


class RobotException(TipsterByteException):
    """Excepción base para errores de robot."""

    pass


class RobotNotFoundException(RobotException):
    """No hay robot registrado para el tipo de fuente."""

    def __init__(self, robot_type: str):
        super().__init__(
            message=f"No hay robot registrado para tipo '{robot_type}'",
            error_code="ROBOT_NOT_FOUND",
            status_code=500,
            context={"robot_type": robot_type},
            suggestion=f"Registra un robot para el tipo '{robot_type}' usando @register_robot",
        )


class ScrapingException(RobotException):
    """Error durante el scraping."""

    def __init__(
        self,
        robot_id: str,
        url: str,
        original_error: Optional[Exception] = None,
    ):
        context = {
            "robot_id": robot_id,
            "url": url,
        }
        if original_error:
            context["original_error_type"] = type(original_error).__name__
            context["original_error_message"] = str(original_error)

        super().__init__(
            message=f"Error en scraping con robot '{robot_id}'",
            error_code="SCRAPING_ERROR",
            status_code=500,
            context=context,
            suggestion="Verifica que la URL sea accesible y que el HTML tenga la estructura esperada",
        )


class ScrapingTimeoutException(RobotException):
    """Timeout durante el scraping."""

    def __init__(self, robot_id: str, url: str, timeout_seconds: int):
        super().__init__(
            message=f"Timeout después de {timeout_seconds}s en robot '{robot_id}'",
            error_code="SCRAPING_TIMEOUT",
            status_code=504,
            context={
                "robot_id": robot_id,
                "url": url,
                "timeout_seconds": timeout_seconds,
            },
            suggestion="Aumenta el timeout o verifica que el sitio responda",
        )


class ScrapingParsingException(RobotException):
    """Error de parsing durante el scraping."""

    def __init__(self, robot_id: str, url: str, selector: str):
        super().__init__(
            message=f"Error de parsing en robot '{robot_id}'",
            error_code="SCRAPING_PARSING_ERROR",
            status_code=500,
            context={
                "robot_id": robot_id,
                "url": url,
                "selector": selector,
            },
            suggestion=f"El selector '{selector}' no encontró elementos. Verifica que el HTML tenga la estructura esperada",
        )
