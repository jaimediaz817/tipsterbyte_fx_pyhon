import asyncio

from datetime import datetime
from pathlib import Path
import subprocess
import typer
from loguru import logger

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# Core
from core.db.no_sql.schema_initializer import (
    check_mongo_connection,
    initialize_mongo_schema,
)
from core.config import Settings
from core.db.sql.init_sql_all_models import load_all_models
from core.logger import configure_logging

# Scripts de gestión de estado de las bases de datos
from commands.db.admin.sql.sql_state_manager import app as sql_state_app
from commands.db.admin.no_sql.mongo_state_manager import app as mongo_state_app


# Scripts para poblar las bases de datos (Seeders)
from scripts.db.seeders.sql.seed_database_sql import seed_sql_data_auth_module
from scripts.db.seeders.no_sql.seed_database_no_sql import seed_nosql_data_auth_module # Asumiendo que el seeder de mongo se llama así para consistencia

# --- Migraciones de datos MongoDB ---
# 001: Añade el campo process_name a access_logs
from scripts.db.migrations.nosql.migration_add_process_name_to_access_logs import (
    run_migration as run_mongo_migration_001
)

# --- NUEVA IMPORTACIÓN: Funciones del módulo de secretos ---
from core.secrets import (
    generate_key,
    key_exists,
    encrypt as f_encrypt,
    decrypt as f_decrypt,
    FERNET_SECRET_FILE
)

# --- 2. APLICACIÓN PRINCIPAL DE TYPER ---
# Este es el punto de entrada para todos los comandos.
app = typer.Typer(
    name="TipsterByte FX Manager",
    help="Herramienta de gestión centralizada para el backend del proyecto.",
    no_args_is_help=True # Muestra la ayuda si no se pasan argumentos
)



# --- 3. SECCIÓN DE COMANDOS PARA POSTGRESQL (SQL) ---
# Todos los comandos relacionados con la base de dato

# --- Sub-comando para la Base de Datos SQL (PostgreSQL) ---
# db_app = typer.Typer()
# app.add_typer(db_app, name="db", help="Comandos para la gestión de la base de datos SQL.")


db_app = typer.Typer(name="sql", help="Gestiona la base de datos SQL (PostgreSQL).")
app.add_typer(db_app)

@db_app.command("create-migration")
def db_create_migration(message: str = typer.Option(None, "-m", "--message", help="Mensaje descriptivo para la migración.")):
    """Genera un nuevo archivo de migración basado en los cambios de los modelos."""
    configure_logging()
    load_all_models()

    if not message:
        logger.info("No se proporcionó mensaje. Usando mensaje autogenerado.")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message = f"auto_migration_{timestamp}"
    
    logger.info(f"Generando migración con mensaje: '{message}'")
    
    try:
        command = ["alembic", "revision", "--autogenerate", "-m", message]
        # --- CAMBIO CLAVE: Añadir 'errors="replace"' para manejar caracteres inválidos ---
        # Esto reemplazará cualquier carácter que no sea UTF-8 con un '?' en lugar de fallar.
        subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            errors='replace'
        )
        logger.success("✅ Nueva migración generada exitosamente en 'alembic/versions/'.")
        logger.info("Revisa el archivo generado y luego ejecuta 'python manage.py sql migrate' para aplicarlo.")

    except subprocess.CalledProcessError as e:
        # --- CAMBIO CLAVE: Manejo de errores más seguro ---
        # Comprobamos si e.stderr no es None antes de intentar usarlo.
        stderr_output = e.stderr.lower() if e.stderr else ""
        
        if "can't locate revision" in stderr_output:
            logger.error("❌ DESINCRONIZACIÓN DETECTADA: No se puede crear la migración.")
            logger.warning("La base de datos apunta a una revisión que ya no existe en los archivos.")
            logger.info("\n➡️  SOLUCIÓN RECOMENDADA:")
            logger.info("   Ejecuta 'python manage.py sql state clear-migrations' para resetear el historial y vuelve a intentarlo.")
        else:
            # Mostramos stdout y stderr si están disponibles, para un mejor diagnóstico.
            logger.error("❌ Falló la generación de la migración.")
            if e.stdout:
                logger.error(f"--- Salida Estándar ---\n{e.stdout}")
            if e.stderr:
                logger.error(f"--- Salida de Error ---\n{e.stderr}")
            else:
                logger.error("No se pudo capturar la salida de error (posiblemente un error de bajo nivel).")

        raise typer.Exit(code=1)

# def db_create_migration(message: str | None = typer.Argument(None, help="Mensaje descriptivo. Si se omite, se genera uno automático.")):
#     """
#     Genera un nuevo archivo de migración de Alembic.
#     Si no se proporciona un mensaje descriptivo, se genera uno automáticamente con un timestamp.
#     Args:
#         message (str | None): Mensaje descriptivo para la migración. Si se omite, se genera uno automático.
#     Uso:
#         Para crear una migración con un mensaje personalizado, ejecuta:
#             python manage.py db create-migration "Tu mensaje descriptivo"
#         Si omites el mensaje, se generará uno automáticamente.
#     """
#     """Genera un nuevo archivo de migración de Alembic."""
#     configure_logging()
#     load_all_models()
    
#     # --- CAMBIO CLAVE: Añadimos la lógica para el mensaje automático ---
#     if not message:
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         message = f"auto_migration_{timestamp}"
#         logger.info("No se proporcionó mensaje. Usando mensaje autogenerado.")

#     logger.info(f"Generando migración con mensaje: '{message}'")
#     try:
#         subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
#         logger.success("✅ Archivo de migración generado exitosamente.")
#     except Exception as e:
#         logger.error(f"❌ Falló la generación de la migración. Error: {e}")

@db_app.command("migrate")
def db_migrate():
    """Aplica todas las migraciones pendientes a la base de datos SQL."""
    configure_logging()
    load_all_models()

    # --- CAMBIO CLAVE: Validar si existen archivos de migración ---
    # versions_dir = Settings.ALEMBIC_VERSIONS_DIR
    versions_dir = Path(__file__).parent / "alembic" / "versions"
    print(f"Buscando archivos de migración en: {versions_dir}")
    migration_files = list(versions_dir.glob("*.py"))

    if not migration_files:
        logger.warning("❌ No se encontraron archivos de migración para aplicar.")
        logger.info("-" * 60)
        logger.info("PASOS SUGERIDOS:")
        logger.info("1. Crea un nuevo archivo de migración basado en tus modelos:")
        typer.secho('   python manage.py sql create-migration -m "Mi primera migración"', fg=typer.colors.CYAN)
        logger.info("\n2. Una vez creado, aplica la migración con este mismo comando:")
        typer.secho("   python manage.py sql migrate", fg=typer.colors.CYAN)
        logger.info("-" * 60)
        raise typer.Exit()

    logger.info(f"Aplicando {len(migration_files)} migracion(es) SQL a la base de datos...")
    try:
        subprocess.run(
            ["alembic", "upgrade", "head"], 
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        logger.success("✅ Migraciones aplicadas exitosamente.")
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."
        logger.error(f"❌ Falló la aplicación de las migraciones.\nDetalles:\n{stderr_output}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Falló la aplicación de las migraciones. Error: {e}")

# --- CAMBIO CLAVE: Añadimos el comando 'seed' ---
@db_app.command("seed")
def db_seed():
    
    """
    Puebla la base de datos con datos iniciales (roles, usuario admin, etc.).
    """
    configure_logging()
    # --- CAMBIO CLAVE: Llama a la función aquí ---
    load_all_models()    
    seed_sql_data_auth_module()

# Anidamos la app de backup/restore/reset dentro de los comandos de 'db'
db_app.add_typer(sql_state_app, name="state", help="Gestiona el estado de la BD (backups/restauraciones/reseteos).")


# --- 4. SECCIÓN DE COMANDOS PARA MONGODB (NOSQL) ---
# Todos los comandos relacionados con la base de datos NoSQL viven aquí.
# Se invocarán con: python manage.py mongo <comando>
mongo_app = typer.Typer(name="nosql", help="Gestiona la base de datos NoSQL (MongoDB).")
app.add_typer(mongo_app)

@mongo_app.command("validate-connection")
def mongo_validate():
    """
    Valida la conexión y autenticación con la base de datos MongoDB.

    Este comando realiza las siguientes acciones:
    1. Intenta conectarse al servidor MongoDB utilizando las credenciales definidas en el archivo de configuración (`settings`).
    2. Ejecuta el comando `ping` en la base de datos para verificar que el servidor está accesible y que las credenciales son válidas.
    3. Busca dinámicamente todos los modelos definidos en el proyecto que heredan de `beanie.Document`.
    4. Muestra en la consola un resumen de los modelos encontrados y, si es posible, el número de documentos en cada colección asociada.

    Uso:
        python manage.py nosql validate-connection

    Salida esperada:
    - Si la conexión es exitosa, se mostrará un mensaje indicando que la conexión y autenticación fueron exitosas.
    - Si se encuentran modelos, se listarán sus nombres y el conteo de documentos en sus colecciones.
    - Si ocurre un error (por ejemplo, credenciales incorrectas o el servidor no está disponible), se mostrará un mensaje de error detallado.

    Este comando es útil para diagnosticar problemas de conexión con MongoDB y verificar que los modelos están correctamente configurados.
    """
    asyncio.run(check_mongo_connection())

@mongo_app.command("init-schema")
def mongo_init_schema():
    """
    Busca todos los modelos de Beanie y crea/verifica sus colecciones e índices en MongoDB.

    PASOS:

    1) 🔌 Valida la conexión con MongoDB utilizando el comando `validate-connection`.

    2) 🔎 Busca dinámicamente todos los modelos definidos en el proyecto que heredan de `beanie.Document`.

    3) ⚙️ Inicializa Beanie con los modelos encontrados, lo que asegura que:
       - Las colecciones asociadas a los modelos se crean si no existen.
       - Los índices definidos en los modelos se crean o verifican.

    4) 🗂️ Verifica manualmente si las colecciones asociadas a los modelos existen en la base de datos:
       - Si una colección no existe, se crea vacía utilizando el cliente de MongoDB (`motor`).
       - Si ya existe, se registra en los logs que la colección está disponible.

    Uso:
      python manage.py nosql init-schema

    Salida esperada:
    - Si la inicialización es exitosa, se mostrará un mensaje indicando que las colecciones e índices han sido creados o verificados.
    - Si una colección no existía previamente, se mostrará un mensaje indicando que fue creada vacía.
    - Si ocurre un error (por ejemplo, problemas con los modelos o la base de datos), se mostrará un mensaje de error detallado.

    Este comando es útil para preparar la base de datos MongoDB antes de iniciar la aplicación, asegurando que todas las colecciones e índices necesarios están configurados correctamente.
    """
    asyncio.run(initialize_mongo_schema())

@mongo_app.command("seed")
def mongo_seed():
    """Puebla la base de datos MongoDB con datos de ejemplo (señales, logs, etc.)."""
    asyncio.run(seed_nosql_data_auth_module())
    
    
# Anidamos los comandos de backup/restore/reset para MongoDB
mongo_app.add_typer(mongo_state_app, name="state", help="Gestiona el estado de la BD NoSQL (backup/restore/reset).")
    
  
# --- CAMBIO CLAVE: Añadimos la nueva sección para migraciones de datos de MongoDB ---
mongo_migrations_app = typer.Typer(name="nosql-migrate", help="Ejecuta migraciones de datos para MongoDB.")
app.add_typer(mongo_migrations_app)

@mongo_migrations_app.command("run")
def run_mongo_migrations():
    """Añade campos faltantes a documentos existentes según los nuevos modelos."""
    configure_logging()
    logger.info("Iniciando proceso de migración de datos de MongoDB...")
    # Aquí podrías tener una lógica para ejecutar varias migraciones en orden
    asyncio.run(run_mongo_migration_001())
    logger.info("Proceso de migración de MongoDB finalizado.")  
    
    
    
    
    
    
    
    
# --- NUEVA SECCIÓN: Comandos para gestión de secretos ---
secrets_app = typer.Typer(name="secrets", help="Gestiona la clave de cifrado Fernet y operaciones relacionadas.")
app.add_typer(secrets_app)

@secrets_app.command("generate")
def secrets_generate(force: bool = typer.Option(False, "--force", "-f", help="Fuerza la sobreescritura si la clave ya existe (rotación).")):
    """Genera una nueva clave de cifrado .fernet.key."""
    configure_logging()
    generate_key(force=force)

@secrets_app.command("show")
def secrets_show():
    """Verifica si la clave de cifrado existe y muestra su ubicación."""
    configure_logging()
    if key_exists():
        logger.info(f"✅ Clave de cifrado disponible. Ubicación del archivo: {FERNET_SECRET_FILE} (o definida en variable de entorno).")
    else:
        logger.warning("❌ No se encontró una clave de cifrado. Ejecuta 'python manage.py secrets generate' para crear una.")

@secrets_app.command("encrypt")
def secrets_encrypt(value: str = typer.Argument(..., help="El texto plano que deseas cifrar.")):
    """Cifra un valor usando la clave actual."""
    configure_logging()
    try:
        encrypted_value = f_encrypt(value)
        logger.info("Valor cifrado:")
        print(encrypted_value)
    except Exception as e:
        logger.error(f"❌ Error durante el cifrado: {e}")

@secrets_app.command("decrypt")
def secrets_decrypt(token: str = typer.Argument(..., help="El token cifrado que deseas descifrar.")):
    """Descifra un token usando la clave actual."""
    configure_logging()
    try:
        decrypted_value = f_decrypt(token)
        logger.info("Valor descifrado:")
        print(decrypted_value)
    except Exception as e:
        logger.error(f"❌ Error durante el descifrado: {e}")    
    
    
    
    
    
    
    
    
# --- 5. SECCIÓN DE COMANDOS PARA EL SERVIDOR WEB ---
# Comandos para iniciar y gestionar el servidor de desarrollo.
# Se invocarán con: python manage.py server <comando>

server_app = typer.Typer(
    name="server", 
    help="Grupo de comandos para gestionar el servidor web de desarrollo (Uvicorn).", 
    no_args_is_help=True
)
app.add_typer(server_app)
# app.add_typer(server_app, name="server", help="Comandos para el servidor web.")

@server_app.command("run")
def server_run(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """
    Inicia el servidor web Uvicorn. Este es el comando principal del grupo 'server'.
    
    Ejemplo de uso:
        python manage.py server run --port 8080
    """
    configure_logging()
    logger.info(f"Iniciando servidor en http://{host}:{port}")
    command = ["uvicorn", "main_init_web_server:app", f"--host={host}", f"--port={port}"]
    if reload:
        command.append("--reload")
    subprocess.run(command)

if __name__ == "__main__":
    app()