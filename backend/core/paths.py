# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\core\paths.py
from pathlib import Path
import sys

def _find_project_root(anchor_file: str = 'pyproject.toml') -> Path:
    """
    Busca hacia arriba desde la ubicación de este archivo para encontrar la raíz del proyecto,
    identificada por la presencia de un archivo 'ancla' como 'pyproject.toml'.
    Esta función es interna y no debe ser usada fuera de este módulo.
    """
    current_path = Path(__file__).resolve()
    while not (current_path / anchor_file).exists():
        if current_path.parent == current_path:
            raise FileNotFoundError(
                f"No se pudo encontrar la raíz del proyecto (buscando '{anchor_file}'). "
                "Asegúrate de que el proyecto mantiene la estructura esperada."
            )
        current_path = current_path.parent
    return current_path

# --- CONSTANTES DE RUTA PARA USAR EN TODO EL PROYECTO ---
# Se calculan una sola vez cuando se importa este módulo.
try:
    # PROJECT_ROOT es la carpeta principal, ej: '.../tipsterByte_fx/'
    # Esta es la ruta que contiene 'backend/', 'pyproject.toml', etc.
    PROJECT_ROOT = _find_project_root()
    
    # BACKEND_ROOT es la carpeta 'backend' dentro del proyecto.
    # Se construye a partir de PROJECT_ROOT para evitar cualquier duplicación.
    BACKEND_ROOT = PROJECT_ROOT / "backend"
    CORE_ROOT    = BACKEND_ROOT / "core"
    ALEMBIC_ROOT = BACKEND_ROOT / "alembic"
    LOGS_ROOT    = BACKEND_ROOT / "logs"
    
    # --- AÑADIR ESTAS LÍNEAS PARA DEPURAR ---
    print("\n" + "-" * 80)
    print(f"DEBUG: PROJECT_ROOT = {PROJECT_ROOT}")
    print(f"DEBUG: BACKEND_ROOT = {BACKEND_ROOT}")    
    print("-" * 80 + "\n")
    # -----------------------------------------    

except FileNotFoundError as e:
    print(f"ERROR CRÍTICO: {e}", file=sys.stderr)
    sys.exit(1)