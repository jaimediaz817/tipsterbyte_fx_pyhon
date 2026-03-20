"""
Utilidades locales para las tareas del módulo leagues_manager.
"""

import uuid
from datetime import datetime


def generate_run_id() -> str:
    """
    Genera un identificador único para una ejecución del scheduler.

    Formato: runid_YYYYMMDD_<uuid4>
    Ejemplo: runid_20260311_a3f1c2d4-8b9e-4f2a-b1c3-d4e5f6a7b8c9

    Returns:
        str: Identificador único para la ejecución
    """
    date_prefix = datetime.now().strftime("%Y%m%d")
    return f"runid_{date_prefix}_{uuid.uuid4()}"
