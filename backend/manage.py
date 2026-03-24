import asyncio
import sys

from datetime import datetime

# from pathlib import Path
import subprocess
import typer
from loguru import logger

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# --- 1. IMPORTACIONES DE MÓDULOS DEL PROYECTO ---
# Se agrupan las importaciones por su origen para mayor claridad.

# Core
from commands.db.admin.sql.db_utils import truncate_tables
from core.db.sql.database_sql import get_db_context
from scripts.db.seeders.sql_seeder_orchestrator import run_seeders as run_sql_seeders
from core.paths import BACKEND_ROOT
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
# from scripts.db.seeders.sql.seed_database_sql import seed_sql_data_auth_module
from scripts.db.seeders.no_sql.seed_database_no_sql import (
    seed_nosql_data_auth_module,
)  # Asumiendo que el seeder de mongo se llama así para consistencia

# --- IMPORTA EL NUEVO COMANDO ---
from commands import project_cli


# --- Migraciones de datos MongoDB ---
# 001: Añade el campo process_name a access_logs
from scripts.db.migrations.nosql.migration_add_process_name_to_access_logs import (
    run_migration as run_mongo_migration_001,
)

# --- NUEVA IMPORTACIÓN: Funciones del módulo de secretos ---
from core.secrets import (
    generate_key,
    key_exists,
    encrypt as f_encrypt,
    decrypt as f_decrypt,
    FERNET_SECRET_FILE,
)

# --- NUEVA IMPORTACIÓN: Orquestador de Seeders ---
# from scripts.db.seeders.sql_seeder_orchestrator import run_seeders

# --- 2. APLICACIÓN PRINCIPAL DE TYPER ---
# Este es el punto de entrada para todos los comandos.
app = typer.Typer(
    name="TipsterByte FX Manager",
    help="Herramienta de gestión centralizada para el backend del proyecto.",
    no_args_is_help=True,  # Muestra la ayuda si no se pasan argumentos
)


# --- 3. SECCIÓN DE COMANDOS PARA POSTGRESQL (SQL) ---
# Todos los comandos relacionados con la base de dato

# --- Sub-comando para la Base de Datos SQL (PostgreSQL) ---
# db_app = typer.Typer()
# app.add_typer(db_app, name="db", help="Comandos para la gestión de la base de datos SQL.")


# --- REGISTRA EL NUEVO GRUPO DE COMANDOS ---
app.add_typer(
    project_cli.app, name="project", help="Comandos de estado y guía del proyecto."
)


db_app = typer.Typer(name="sql", help="Gestiona la base de datos SQL (PostgreSQL).")
app.add_typer(db_app)


@db_app.command("create-migration")
def db_create_migration(
    message: str = typer.Option(
        None, "-m", "--message", help="Mensaje descriptivo para la migración."
    )
):
    """Genera un nuevo archivo de migración basado en los cambios de los modelos."""
    configure_logging()
    load_all_models()

    if not message:
        logger.info("No se proporcionó mensaje. Usando mensaje autogenerado.")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message = f"auto_migration_{timestamp}"

    logger.info(f"Generando migración con mensaje: '{message}'")

    try:
        # En Windows, usar shell=True para que encuentre el ejecutable correctamente
        import platform

        use_shell = platform.system() == "Windows"

        command = [
            sys.executable,
            "-m",
            "alembic",
            "revision",
            "--autogenerate",
            "-m",
            message,
        ]
        # --- CAMBIO CLAVE: Añadir 'errors="replace"' para manejar caracteres inválidos ---
        # Esto reemplazará cualquier carácter que no sea UTF-8 con un '?' en lugar de fallar.
        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                message,
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=use_shell,
        )
        logger.success(
            "✅ Nueva migración generada exitosamente en 'alembic/versions/'."
        )
        logger.info(
            "Revisa el archivo generado y luego ejecuta 'python manage.py sql migrate' para aplicarlo."
        )

    except subprocess.CalledProcessError as e:
        # --- CAMBIO CLAVE: Manejo de errores más seguro ---
        # Comprobamos si e.stderr no es None antes de intentar usarlo.
        stderr_output = e.stderr.lower() if e.stderr else ""

        if "can't locate revision" in stderr_output:
            logger.error(
                "❌ DESINCRONIZACIÓN DETECTADA: No se puede crear la migración."
            )
            logger.warning(
                "La base de datos apunta a una revisión que ya no existe en los archivos."
            )
            logger.info("\n➡️  SOLUCIÓN RECOMENDADA:")
            logger.info(
                "   Ejecuta 'python manage.py sql state clear-migrations' para resetear el historial y vuelve a intentarlo."
            )
        else:
            # Mostramos stdout y stderr si están disponibles, para un mejor diagnóstico.
            logger.error("❌ Falló la generación de la migración.")
            if e.stdout:
                logger.error(f"--- Salida Estándar ---\n{e.stdout}")
            if e.stderr:
                logger.error(f"--- Salida de Error ---\n{e.stderr}")
            else:
                logger.error(
                    "No se pudo capturar la salida de error (posiblemente un error de bajo nivel)."
                )

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
def db_migrate(
    revision: str = typer.Argument(
        None,
        help="La revisión a la que se quiere migrar. Ejemplo: 'abc123def456'. Si no se especifica, muestra las disponibles.",
    )
):
    """
    Aplica las migraciones de Alembic a la base de datos.

    Ejemplos de uso:
      python manage.py sql migrate                    # Muestra migraciones disponibles
      python manage.py sql migrate head               # Aplica todas las migraciones pendientes
      python manage.py sql migrate abc123def456       # Aplica una migración específica
      python manage.py sql status                     # Ver estado actual
    """
    configure_logging()
    load_all_models()

    # --- CAMBIO CLAVE: Validar si existen archivos de migración ---
    versions_dir = BACKEND_ROOT / "alembic" / "versions"

    print(f"Buscando archivos de migración en: {versions_dir}")
    migration_files = list(versions_dir.glob("*.py"))

    if not migration_files:
        logger.warning("❌ No se encontraron archivos de migración para aplicar.")
        logger.info("-" * 60)
        logger.info("PASOS SUGERIDOS:")
        logger.info("1. Crea un nuevo archivo de migración basado en tus modelos:")
        typer.secho(
            '   python manage.py sql create-migration -m "Mi primera migración"',
            fg=typer.colors.CYAN,
        )
        logger.info("\n2. Una vez creado, aplica la migración con este mismo comando:")
        typer.secho("   python manage.py sql migrate", fg=typer.colors.CYAN)
        logger.info("-" * 60)
        raise typer.Exit()

    # Si NO se especifica revisión, mostrar migraciones disponibles
    if revision is None:
        logger.info(
            "No se especificó una revisión. Mostrando migraciones disponibles..."
        )

        # Obtener migraciones disponibles usando alembic
        try:
            import platform

            use_shell = platform.system() == "Windows"

            result = subprocess.run(
                [sys.executable, "-m", "alembic", "history", "--verbose"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
                errors="replace",
                shell=use_shell,
            )

            migrations = []
            lines = result.stdout.strip().split("\n")

            # Parsear la salida de alembic history
            current_rev = None
            current_msg = None

            for line in lines:
                line = line.strip()

                # Detectar líneas de revisión
                if line.startswith("Rev:"):
                    if current_rev:
                        # Guardar la migración anterior
                        migrations.append(
                            {
                                "revision": current_rev,
                                "message": current_msg or "Sin mensaje",
                            }
                        )

                    # Extraer nueva revisión
                    parts = line.split()
                    if len(parts) >= 2:
                        current_rev = parts[1]
                        # Verificar si tiene marcador (head)
                        if len(parts) >= 3 and parts[2] == "(head)":
                            current_msg = "HEAD - Migración más reciente"
                        else:
                            current_msg = None

                # Detectar líneas de mensaje/comentario
                elif (
                    line.startswith("#")
                    or line.startswith("Revises:")
                    or line.startswith("Parent:")
                ):
                    if line.startswith("#"):
                        # Extraer el mensaje del comentario
                        msg_content = line[1:].strip()
                        if msg_content and not msg_content.startswith("Create Date:"):
                            current_msg = msg_content

            # Agregar la última migración procesada
            if current_rev:
                migrations.append(
                    {
                        "revision": current_rev,
                        "message": current_msg or "Sin mensaje",
                    }
                )

            if not migrations:
                logger.warning("⚠️ No se pudieron obtener las migraciones.")
                logger.info("Intentando aplicar todas las migraciones pendientes...")
            else:
                # Mostrar migraciones disponibles
                typer.echo("\n" + "=" * 70)
                typer.secho(
                    " 🔄 MIGRACIONES DISPONIBLES", fg=typer.colors.CYAN, bold=True
                )
                typer.echo("=" * 70)

                for i, migration in enumerate(migrations[:10], 1):  # Mostrar máximo 10
                    marker = " (HEAD)" if i == 1 else ""
                    typer.echo(f"  {i:2d}. {migration['revision'][:12]}...{marker}")
                    typer.echo(f"      {migration['message']}")

                typer.echo("=" * 70)

                # Mostrar ejemplos de uso
                typer.echo("")
                typer.secho(" 💡 EJEMPLOS DE USO:", fg=typer.colors.GREEN, bold=True)
                typer.echo("-" * 70)
                typer.secho(
                    "  Para aplicar todas las migraciones pendientes:",
                    fg=typer.colors.WHITE,
                )
                typer.secho(
                    "    python manage.py sql migrate head", fg=typer.colors.CYAN
                )
                typer.echo("")
                typer.secho(
                    "  Para aplicar una migración específica:", fg=typer.colors.WHITE
                )
                if migrations:
                    example_rev = (
                        migrations[0]["revision"][:12] if migrations else "abc123def456"
                    )
                    typer.secho(
                        f"    python manage.py sql migrate {example_rev}",
                        fg=typer.colors.CYAN,
                    )
                typer.echo("")
                typer.secho(
                    "  Para ver el estado actual de las migraciones:",
                    fg=typer.colors.WHITE,
                )
                typer.secho("    python manage.py sql status", fg=typer.colors.CYAN)
                typer.echo("-" * 70)
                typer.echo("")

                # Aplicar todas las migraciones (head)
                logger.info("Aplicando todas las migraciones pendientes...")

        except subprocess.CalledProcessError as e:
            logger.warning("⚠️ No se pudieron obtener las migraciones.")
            logger.info("Intentando aplicar todas las migraciones pendientes...")

    logger.info(
        f"🚀 Aplicando migraciones de Alembic hasta la revisión: '{revision}'..."
    )
    try:
        # En Windows, usar shell=True para que encuentre el ejecutable correctamente
        import platform

        use_shell = platform.system() == "Windows"

        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            # capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=use_shell,
        )
        logger.success("✅ Migraciones aplicadas exitosamente.")
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.strip() if e.stderr else "No stderr output."
        logger.error(
            f"❌ Falló la aplicación de las migraciones.\nDetalles:\n{stderr_output}"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"❌ Falló la aplicación de las migraciones. Error: {e}")


# --- CAMBIO CLAVE: Añadimos el comando 'seed' ---
# @db_app.command("seed")
# def db_seed():

#     """
#     Puebla la base de datos con datos iniciales (roles, usuario admin, etc.).
#     """
#     configure_logging()
#     # --- CAMBIO CLAVE: Llama a la función aquí ---
#     load_all_models()
#     seed_sql_data_auth_module()


# --- 4. DEFINICIÓN DE COMANDOS DIRECTOS ---
# Comandos que no pertenecen a un subgrupo.


@db_app.command("seed")
def seed_sql_data(
    seeder_name: str = typer.Argument(
        None,
        help="Nombre de la clase del seeder a ejecutar (ej. 'AuthSeeder'). Si no se especifica, se ejecutan todos.",
    ),
    update: bool = typer.Option(
        False,
        "--update",
        help="Forzar la actualización de los registros existentes con los valores del seeder.",
    ),
):
    """Puebla la base de datos SQL con datos iniciales usando los seeders."""
    print("Iniciando el proceso de seeding SQL... seeder name: " + str(seeder_name))
    configure_logging()
    load_all_models()
    configure_logging()
    run_sql_seeders(specific_seeder=seeder_name, update_existing=update)


# Anidamos la app de backup/restore/reset dentro de los comandos de 'db'
db_app.add_typer(
    sql_state_app,
    name="state",
    help="Gestiona el estado de la BD (backups/restauraciones/reseteos).",
)


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
mongo_app.add_typer(
    mongo_state_app,
    name="state",
    help="Gestiona el estado de la BD NoSQL (backup/restore/reset).",
)


# --- CAMBIO CLAVE: Añadimos la nueva sección para migraciones de datos de MongoDB ---
mongo_migrations_app = typer.Typer(
    name="nosql-migrate", help="Ejecuta migraciones de datos para MongoDB."
)
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
secrets_app = typer.Typer(
    name="secrets",
    help="Gestiona la clave de cifrado Fernet y operaciones relacionadas.",
)
app.add_typer(secrets_app)


@secrets_app.command("generate")
def secrets_generate(
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Fuerza la sobreescritura si la clave ya existe (rotación).",
    )
):
    """Genera una nueva clave de cifrado .fernet.key."""
    configure_logging()
    generate_key(force=force)


@secrets_app.command("show")
def secrets_show():
    """Verifica si la clave de cifrado existe y muestra su ubicación."""
    configure_logging()
    if key_exists():
        logger.info(
            f"✅ Clave de cifrado disponible. Ubicación del archivo: {FERNET_SECRET_FILE} (o definida en variable de entorno)."
        )
    else:
        logger.warning(
            "❌ No se encontró una clave de cifrado. Ejecuta 'python manage.py secrets generate' para crear una."
        )


@secrets_app.command("encrypt")
def secrets_encrypt(
    value: str = typer.Argument(..., help="El texto plano que deseas cifrar.")
):
    """Cifra un valor usando la clave actual."""
    configure_logging()
    try:
        encrypted_value = f_encrypt(value)
        logger.info("Valor cifrado:")
        print(encrypted_value)
    except Exception as e:
        logger.error(f"❌ Error durante el cifrado: {e}")


@secrets_app.command("decrypt")
def secrets_decrypt(
    token: str = typer.Argument(..., help="El token cifrado que deseas descifrar.")
):
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
    no_args_is_help=True,
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
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "main_init_web_server:app",
        f"--host={host}",
        f"--port={port}",
    ]
    if reload:
        command.append("--reload")
    subprocess.run(command)


@db_app.command("truncate")
def truncate_sql_data(
    tables: list[str] = typer.Argument(
        ..., help="Lista de nombres de tablas a truncar (separadas por espacios)."
    )
):
    """
    Vacía por completo el contenido de una o más tablas SQL. ¡USAR CON PRECAUCIÓN!
    """
    configure_logging()
    logger.warning(
        "🔥 ¡ATENCIÓN! Esta operación eliminará TODOS los datos de las tablas especificadas."
    )

    # Pedimos confirmación para evitar desastres
    if not typer.confirm("¿Estás seguro de que quieres continuar?"):
        raise typer.Abort()

    load_all_models()

    with get_db_context() as db:
        truncate_tables(db, tables)

    logger.info("🏁 Proceso de truncado finalizado.")


if __name__ == "__main__":
    app()
