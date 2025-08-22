# Crear el archivo "Índice de Modelos" también en core.
# Necesitamos un archivo que importe todos los modelos para que Alembic y SQLAlchemy los conozcan.
# Como esta es una función central para la base de datos, también pertenece a core.
# Lo llamaremos all_models.py para que su propósito sea evidente.

# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\core\all_models.py
"""
Este archivo importa todos los modelos SQL de todos los subsistemas.
Su único propósito es registrar los modelos en los metadatos de la Base de SQLAlchemy.
Debe ser importado ANTES de cualquier operación que necesite conocer todos los modelos,
como la creación de tablas o las migraciones con Alembic.
"""

# Importa los modelos del subsistema de autenticación
# from backend.apps.auth.infrastructure.models.sql.user_model import User
# from backend.apps.auth.infrastructure.models.sql.role_model import Role
# from backend.apps.auth.infrastructure.models.sql.user_roles_model import user_roles

# Cuando crees el subsistema de 'sports_ingestion' con modelos, los importarás aquí:
# from backend.apps.sports_ingestion.infrastructure.models.sql.some_model import SomeModel

# ... y así sucesivamente para cada subsistema con modelos SQL.
#----------------------------------------------------------------------------------------------------------------
"""
Este archivo importa DINÁMICAMENTE todos los modelos SQL de todos los subsistemas.
Su único propósito es registrar los modelos en los metadatos de la Base de SQLAlchemy.
"""
import importlib
from pathlib import Path

# --- CAMBIO CLAVE: Importar la ruta directamente desde el módulo de rutas ---
from core.paths import BACKEND_ROOT

from loguru import logger

def load_all_models():
    """
    Encuentra e importa dinámicamente todos los archivos de modelos que siguen
    la convención de estar en '.../infrastructure/models/sql/'.
    """
    logger.info("🤖 Iniciando escaneo dinámico de modelos SQL...")
    
    
    # Ruta a la carpeta 'apps' que contiene todos los subsistemas
    backend_root = BACKEND_ROOT
    apps_dir = backend_root / "apps"

    # Contador de modelos cargados
    models_loaded = 0

    # Busca recursivamente todos los archivos .py dentro de la estructura de modelos
    for model_file in apps_dir.rglob("infrastructure/models/sql/*.py"):
        # Ignora los archivos __init__.py
        if model_file.name == "__init__.py":
            continue

        # Convierte la ruta del archivo a un formato de módulo de Python
        # Ejemplo: backend/apps/auth/infrastructure/models/sql/user_model.py
        # se convierte en: backend.apps.auth.infrastructure.models.sql.user_model
        
        # Obtenemos la ruta relativa desde la raíz del proyecto 'backend'
        relative_path = model_file.relative_to(apps_dir.parent)
        # Reemplazamos el separador de carpetas por '.' y quitamos la extensión '.py'
        module_path = str(relative_path).replace("\\", "/").replace("/", ".").replace(".py", "")

        try:
            # Usa importlib para importar el módulo dinámicamente
            importlib.import_module(module_path)
            logger.trace(f"✅ Modelo cargado exitosamente desde: {module_path}")
            models_loaded += 1
        except ImportError as e:
            logger.error(f"❌ Fallo al importar el modelo desde {module_path}. Error: {e}")

    logger.info(f"🤖 Escaneo completado. Se cargaron {models_loaded} modelos SQL.")

# TODO: # --- CAMBIO CLAVE: Elimina o comenta esta línea ---
# Llama a la función para que se ejecute cuando este archivo sea importado
# load_all_models()
