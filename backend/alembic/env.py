from logging.config import fileConfig
from pathlib import Path
import sys

# --- CAMBIO CLAVE: Lógica robusta para encontrar y añadir la raíz del backend al path ---
# Esto es CRUCIAL para que Alembic pueda importar módulos como 'core' y 'apps'.
# try:
#     # Intenta importar desde la ruta centralizada (cuando se ejecuta desde manage.py)
#     from core.paths import BACKEND_ROOT
# except ImportError:
#     # Si falla (ej. al ejecutar 'alembic' directamente), la calcula manualmente.
#     # Esto hace que el script sea funcional en ambos escenarios.
#     backend_root_path = Path(__file__).resolve().parents[1]
#     if str(backend_root_path) not in sys.path:
#         sys.path.insert(0, str(backend_root_path))
#     from core.paths import BACKEND_ROOT

# --- CAMBIO CLAVE: Lógica robusta para encontrar y añadir la raíz del backend al path ---
# Esto asegura que podamos importar desde 'core' y 'apps' sin problemas.
try:
    # Intenta una ruta relativa que funcione desde la mayoría de los contextos de ejecución
    backend_root = Path(__file__).resolve().parents[1]
    if not (backend_root / "core").is_dir():
        # Si la primera no funciona, prueba una estructura diferente
        backend_root = Path(__file__).resolve().parents[2]
    
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
except IndexError:
    print("Error: No se pudo determinar la ruta raíz del backend. Asegúrate de que la estructura del proyecto sea la esperada.")
    sys.exit(1)

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from core.db.sql.base_class import Base
# TODO: modificar para el caso de uso de un ORM diferente o cambios en la estructura de la base de datos
# from core.db.sql.init_sql_all_models import *
from core.db.sql.init_sql_all_models import load_all_models

# Importar settings para acceder a DATABASE_URL
from core.config import settings  # Ajusta la ruta según tu estructura de proyecto

# TODO: COMENTADO!
# Asegurar que la ruta raíz del backend esté disponible
# sys.path.append(str(Path(__file__).resolve().parent.parent))

# --- CAMBIO CLAVE: Ejecutar la función para que Alembic "vea" los modelos ---
# Esta es la línea más importante. Al llamarla, todos los archivos de modelos
# en tu proyecto son importados, y sus tablas se registran en Base.metadata.
load_all_models()


# Configuración de Alembic
config = context.config

# Cargar DATABASE_URL desde config
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# Configurar logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata para autogeneración
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
