"""
Fixture de pytest para tests unitarios del core.
- Configura sys.path para encontrar los módulos
"""

import sys
import os
from pathlib import Path

# --- INICIO: Configuración para asegurar que pytest encuentre los módulos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos dos niveles desde 'tests' para llegar a 'backend'
# tests -> core -> backend
backend_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
# --- FIN: Configuración para asegurar que pytest encuentre los módulos ---
