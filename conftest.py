"""
✅ Pytest Configuration Global
Soluciona permanentemente todos los errores de ModuleNotFoundError en pytest
"""

import sys
from pathlib import Path

# Agregar directorio backend al path ANTES de que pytest importe cualquier cosa
ROOT_PROYECTO = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_PROYECTO / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))
