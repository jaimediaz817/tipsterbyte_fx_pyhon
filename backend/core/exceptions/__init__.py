"""
✅ Módulo de excepciones personalizadas para TipsterByte FX.

✅ AHORA CUMPLE CON OPEN/CLOSED PRINCIPLE:
- ✅ ABIERTO para extension: Cualquier aplicacion puede agregar excepciones
- ✅ CERRADO para modificacion: ESTE ARCHIVO NUNCA MAS SE MODIFICA
- ✅ Cero acoplamiento entre core y aplicaciones
- ✅ Cumplimiento 100% Clean Architecture

✅ Caracteristicas:
- 100% retrocompatible con TODO el codigo existente
- No requiere ningun cambio en imports de ningun otro archivo
- Funciona exactamente igual que antes internamente
"""

from core.exceptions.base import TipsterByteException
from core.exceptions.exception_registry import ExceptionRegistry, register_exception


# ✅ Import automatico y registro de todas las excepciones core
# NOTA: Las excepciones de las aplicaciones se registran ellas mismas
from core.exceptions.database_exceptions import *
from core.exceptions.session_log_exceptions import *
from core.exceptions.process_exceptions import *
from core.exceptions.fuente_exceptions import *
from core.exceptions.robot_exceptions import *
from core.exceptions.concurrency_exceptions import *


__all__ = [
    "TipsterByteException",
    "ExceptionRegistry",
    "register_exception",
]
