"""
Excepción base para TipsterByte FX.

Todas las excepciones personalizadas del proyecto heredan de esta clase,
lo que permite un manejo centralizado de errores.
"""

from typing import Optional, Dict, Any


class TipsterByteException(Exception):
    """
    Excepción base para TipsterByte FX.

    Attributes:
        message: Mensaje descriptivo del error
        error_code: Código único del error para identificación
        status_code: Código HTTP sugerido para respuestas REST
        context: Diccionario con información adicional del contexto
        suggestion: Sugerencia para resolver el error
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.context = context or {}
        self.suggestion = suggestion
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para logging y respuestas."""
        result = {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
        }
        if self.suggestion:
            result["suggestion"] = self.suggestion
        return result

    def __str__(self) -> str:
        """Representación en string de la excepción."""
        base = f"[{self.error_code}] {self.message}"
        if self.suggestion:
            base += f" | Sugerencia: {self.suggestion}"
        return base
