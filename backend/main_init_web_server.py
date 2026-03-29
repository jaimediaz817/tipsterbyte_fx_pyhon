from fastapi.routing import APIRoute
import typer
from core.scheduler import start_scheduler
from core.routes.scheduler_routes import router as scheduler_router
from apps.leagues_manager.api.v1.routes.soccer_league_routes import (
    router as leagues_router,
)
from apps.platform_config.api.v1.routes.platform_config_routes import (
    router as platform_config_router,
)

# from core.scheduler import start_scheduler
from core.db.sql.database_sql import create_db_and_tables
from core.middleware import TraceIDMiddleware
from core.logger import configure_logging
from core.secrets import load_key
from contextlib import asynccontextmanager
import sys
from fastapi import FastAPI
from loguru import logger

# Importar routers
from core.routes.system_routes import router as system_router

# --- CAMBIO CLAVE: Importamos el router del controlador instanciado ---
from apps.auth.api.v1.authenticator_controller import router as auth_router
from apps.auth.api.v1.routes.session_log_routes import router as session_log_router

configure_logging()


def _display_available_routes():
    """Muestra una tabla organizada de todas las rutas de la API en la consola."""

    routes_by_version = {}
    print("\n--- Rutas Disponibles ---")
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Extraer la versión del prefijo del path (ej. /api/v1/...)
            path_parts = route.path.strip("/").split("/")
            version = "v_base"  # Versión por defecto para rutas sin prefijo de versión

            if (
                len(path_parts) > 1
                and path_parts[0] == "api"
                and path_parts[1].startswith("v")
            ):
                version = path_parts[1]
            elif path_parts[0] == "system":
                version = "system"

            if version not in routes_by_version:
                routes_by_version[version] = []

            routes_by_version[version].append(
                {
                    "path": route.path,
                    "name": route.name,
                    "methods": ", ".join(route.methods),
                }
            )

    typer.secho(
        "\n--- API Endpoints Disponibles ---", fg=typer.colors.BRIGHT_GREEN, bold=True
    )

    for version, routes in sorted(routes_by_version.items()):
        version_display = version.replace("_", " ").title()
        typer.secho(f"\n📦 Versión: {version_display}", fg=typer.colors.CYAN, bold=True)

        for route_info in sorted(routes, key=lambda r: r["path"]):
            methods_str = typer.style(
                f"[{route_info['methods']}]".ljust(18), fg=typer.colors.YELLOW
            )
            path_str = typer.style(route_info["path"], fg=typer.colors.WHITE)
            typer.echo(f"  {methods_str}{path_str}")

    typer.echo("-" * 35 + "\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    # Validar que exista la clave Fernet
    try:
        load_key()
    except FileNotFoundError as e:
        logger.error(f"❌ ERROR FATAL: {e}")
        sys.exit(1)

    # ✅ Iniciar el scheduler
    try:
        logger.info("🚀 Iniciando scheduler de procesos programados...")

        # TODO: EVALUAR PARA CREAR Y HABILITAR
        # tb-hu-refactor-tasks-runner-flujo_y_databases-01: start_scheduler en el _init__.py del scheduler
        start_scheduler()
    except Exception as e:
        logger.error(f"⚠️ Error al iniciar el scheduler: {e}")

    logger.info("Startup complete. Metrics exposed.")
    # --- USO DE database.py ---
    # Crear las tablas de la base de datos al arrancar
    try:
        logger.info("🗄️  Inicializando base de datos y creando tablas...")
        create_db_and_tables()
        logger.info("✅ Base de datos y tablas listas.")
    except Exception as e:
        logger.error(
            f"❌ ERROR FATAL: No se pudo conectar o crear las tablas de la BD. {e}"
        )
        sys.exit(1)  # La aplicación no puede funcionar sin BD

    # --- CAMBIO CLAVE: Mostrar las rutas disponibles ---
    # Lo hacemos al final del inicio para asegurarnos de que todas las rutas ya están registradas.
    _display_available_routes()

    yield  # La aplicación se ejecuta aquí

    logger.info("👋 Apagando la aplicación...")


# Instancia FastAPI


api_description = """
## Sistema de Automatización TipsterByte FX 🚀

API central para procesos programados, ingestión y administración del backend.

### 🛠️ CLI de Gestión (manage.py)

Para ver todos los comandos disponibles:
```bash
python manage.py --help
```

#### ✅ SQL (PostgreSQL)
Crear migración:
```bash
python manage.py sql create-migration -m "mi_migracion"
```

Aplicar migraciones:
```bash
python manage.py sql migrate
```

Gestión de estado (backup/restore/reset):
```bash
python manage.py sql state --help
```

Seeders SQL:
```bash
python manage.py seed-sql
python manage.py seed-sql AuthSeeder --update
python manage.py seed-sql PlatformConfigSeeder --update
```

Truncar tablas (peligroso):
```bash
python manage.py truncate-sql tabla1 tabla2
```

#### ✅ NoSQL (MongoDB)
Validar conexión:
```bash
python manage.py nosql validate-connection
```

Inicializar esquema e índices:
```bash
python manage.py nosql init-schema
```

Seeders NoSQL:
```bash
python manage.py nosql seed
```

Gestión de estado (backup/restore/reset):
```bash
python manage.py nosql state --help
```

Migraciones de datos:
```bash
python manage.py nosql-migrate run
```

#### 🔐 Secretos (Fernet)
Generar clave:
```bash
python manage.py secrets generate
```

Mostrar estado:
```bash
python manage.py secrets show
```

Cifrar/descifrar:
```bash
python manage.py secrets encrypt "texto"
python manage.py secrets decrypt "token"
```

#### 🌐 Servidor
Iniciar Uvicorn:
```bash
python manage.py server run --host 127.0.0.1 --port 8000
```
"""
# Aquí puedes definir metadatos para la documentación
tags_metadata = [
    {
        "name": "V1 - Sports Ingestion",
        "description": "Endpoints para la ingesta de datos deportivos (Ligas, Equipos, etc.).",
    },
    {
        "name": "V1 - Authentication",
        "description": "Operaciones con usuarios y autenticación.",
    },
]

app = FastAPI(
    title="TipsterByte generación de parleys - Automation API",
    description=api_description,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

app.add_middleware(TraceIDMiddleware)

# Registrar routers
app.include_router(
    system_router,
    prefix="/system",  # <-- ¡AQUÍ ESTÁ LA MAGIA!
    # tags=["System - Estadisticas y Monitoreo"]    # Opcional: puedes definir el tag aquí para todas las rutas del router
)

# NOTE: Router del sistema - estadísticas y monitoreo
app.include_router(
    system_router,
    prefix="/api/v1/system",  # <-- ¡AQUÍ ESTÁ LA MAGIA!
    # tags=["System - Estadisticas y Monitoreo"]    # Opcional: puedes definir el tag aquí para todas las rutas del router
)

# NOTE: Router autenticación - usuarios y login
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    # tags=["auth"]
)

app.include_router(
    scheduler_router,
    prefix="/api/v1",
    # tags=["Gestión de Scheduler - tareas programadas"]
)

app.include_router(
    leagues_router,
)

app.include_router(
    platform_config_router,
)

app.include_router(
    session_log_router, prefix="/api/v1", tags=["Session Logs - Bitácora de Sesión"]
)
