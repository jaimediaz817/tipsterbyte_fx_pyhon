from fastapi.routing import APIRoute
import typer
from core.db.sql.database_sql import create_db_and_tables
from core.middleware import TraceIDMiddleware
from core.logger import configure_logging
from core.secrets import load_key
configure_logging()

from contextlib import asynccontextmanager
import sys

from fastapi import FastAPI
from loguru import logger

# Importar routers
from core.routes.system_routes import router as system_router

# --- CAMBIO CLAVE: Importamos el router del controlador instanciado ---
from apps.auth.api.v1.authenticator_controller import router as auth_router
# from apps.auth.api.v1.routes.authenticator_routes import router as auth_router

def _display_available_routes():
    """Muestra una tabla organizada de todas las rutas de la API en la consola."""
    
    routes_by_version = {}
    print("\n--- Rutas Disponibles ---")
    for route in app.routes:
        if isinstance(route, APIRoute):
            # Extraer la versión del prefijo del path (ej. /api/v1/...)
            path_parts = route.path.strip('/').split('/')
            version = "v_base" # Versión por defecto para rutas sin prefijo de versión
            
            if len(path_parts) > 1 and path_parts[0] == 'api' and path_parts[1].startswith('v'):
                version = path_parts[1]
            elif path_parts[0] == 'system':
                version = 'system'

            if version not in routes_by_version:
                routes_by_version[version] = []
            
            routes_by_version[version].append({
                "path": route.path,
                "name": route.name,
                "methods": ", ".join(route.methods)
            })

    typer.secho("\n--- API Endpoints Disponibles ---", fg=typer.colors.BRIGHT_GREEN, bold=True)
    
    for version, routes in sorted(routes_by_version.items()):
        version_display = version.replace('_', ' ').title()
        typer.secho(f"\n📦 Versión: {version_display}", fg=typer.colors.CYAN, bold=True)
        
        for route_info in sorted(routes, key=lambda r: r['path']):
            methods_str = typer.style(f"[{route_info['methods']}]".ljust(18), fg=typer.colors.YELLOW)
            path_str = typer.style(route_info['path'], fg=typer.colors.WHITE)
            typer.echo(f"  {methods_str}{path_str}")
            
    typer.echo("-" * 35 + "\n")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Handles application startup and shutdown events. """
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
        # start_scheduler()
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
        logger.error(f"❌ ERROR FATAL: No se pudo conectar o crear las tablas de la BD. {e}")
        sys.exit(1) # La aplicación no puede funcionar sin BD
        
    # --- CAMBIO CLAVE: Mostrar las rutas disponibles ---
    # Lo hacemos al final del inicio para asegurarnos de que todas las rutas ya están registradas.
    _display_available_routes()        

    yield # La aplicación se ejecuta aquí

    logger.info("👋 Apagando la aplicación...")

# Instancia FastAPI


api_description = """
## Sistema de Automatización TipsterByte FX 🚀

Esta es la API central para todos los procesos de automatización.

### Herramientas de Gestión (manage.py)

Este proyecto incluye una potente interfaz de línea de comandos (`manage.py`) para facilitar el desarrollo y el mantenimiento.
Para ver todos los comandos disponibles, ejecuta: `python manage.py --help`

#### Migraciones de Base de Datos
*   **Crear una nueva migración:**
    ```bash
    python manage.py db create-migration "Tu mensaje descriptivo"
    ```
*   **Aplicar migraciones:**
    ```bash
    python manage.py db migrate
    ```

#### Gestión de Estado de la Base de Datos
*   **Crear un backup:**
    ```bash
    python manage.py db state backup
    ```
*   **Restaurar desde el último backup:**
    ```bash
    python manage.py db state restore
    ```
*   **Resetear la BD (MODO PELIGROSO - PIERDE DATOS):**
    ```bash
    python manage.py db state reset --hard
    ```
*   **Resetear la BD (MODO SEGURO - PRESERVA DATOS):**
    ```bash
    python manage.py db state reset --with-backup
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
# app.include_router(
#     system_router,
#     prefix="/system",  # <-- ¡AQUÍ ESTÁ LA MAGIA!
#     tags=["System - Estadisticas y Monitoreo"]    # Opcional: puedes definir el tag aquí para todas las rutas del router
# )
# NOTE: 
app.include_router(
    system_router,
    prefix="/system",  # <-- ¡AQUÍ ESTÁ LA MAGIA!
    tags=["System - Estadisticas y Monitoreo"]    # Opcional: puedes definir el tag aquí para todas las rutas del router
)

    # Registrar controladores (routers)
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

@app.get("/")
def root():
    return {"status": "API is running"}