import os
import typer
from loguru import logger
import docker
import subprocess
import sys
from docker.errors import NotFound

from core.db.no_sql.db_inspector import get_mongo_db_status
from core.db.sql.admin.db_inspector import get_sql_db_status

styles = {
    "ok": "<green>",
    "warn": "<yellow>",
    "error": "<red>",
    "info": "<cyan>",
    "bold": "<bold>",
    "end": "</>",
}

def print_styled(message: str, style: str = "info"):
    start_tag = styles.get(style, "")
    end_tag = styles.get("end", "")
    bold_start = styles.get("bold", "")
    bold_end = styles.get("end", "")
    command_part = ""
    if "`" in message:
        parts = message.split("`")
        message = parts[0]
        command_part = parts[1]
    logger.opt(ansi=True).info(
        f"{start_tag}➡️  {message}{bold_start}{command_part}{bold_end}{end_tag}"
    )

def execute_manage_command(args: list[str]) -> bool:
    """Ejecuta un subcomando de manage.py y muestra la salida en tiempo real."""
    full_command = [sys.executable, "manage.py"] + args
    logger.info(f"⚙️  Ejecutando: {' '.join(full_command)}")
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                print(line.strip())
        process.wait()
        if process.returncode == 0:
            logger.success("✅ Comando ejecutado exitosamente.")
            return True
        else:
            logger.error(f"❌ El comando falló con código {process.returncode}.")
            return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False

def ask_and_execute(question: str, command: list[str]) -> bool:
    """Pregunta al usuario si desea ejecutar un comando y lo ejecuta si responde 'y'."""
    typer.echo("")
    confirmed = typer.confirm(f"❓ {question}")
    if confirmed:
        return execute_manage_command(command)
    else:
        logger.warning("⏭️  Paso omitido por el usuario.")
        return False

def print_header(title: str):
    """Imprime un encabezado con estilo."""
    typer.echo("\n" + "═" * 60)
    typer.echo(f"        {title}")
    typer.echo("═" * 60)

# =========================================================
# MENÚ RESET
# =========================================================
def menu_reset():
    while True:
        print_header("🔴 Opciones de Reset - TipsterByte FX")
        typer.echo("")
        typer.echo("  ── PostgreSQL ──────────────────────────────────────────")
        typer.echo("  1. 🗑️  Eliminar archivos de migración")
        typer.echo("         → sql state clear-migrations")
        typer.echo("  2. 💣  Borrar todas las tablas SQL")
        typer.echo("         → sql state clear-all-tables")
        typer.echo("  3. ☢️  Reset SQL completo (tablas + migraciones)")
        typer.echo("         → sql state reset --hard")
        typer.echo("")
        typer.echo("  ── MongoDB ─────────────────────────────────────────────")
        typer.echo("  4. 🧹  Limpiar documentos (mantiene colecciones)")
        typer.echo("         → nosql state clear")
        typer.echo("  5. 💣  Reset MongoDB completo (drop base de datos)")
        typer.echo("         → nosql state reset")
        typer.echo("")
        typer.echo("  ── Total ───────────────────────────────────────────────")
        typer.echo("  6. ☢️  Reset TOTAL (SQL + MongoDB a estado cero)")
        typer.echo("")
        typer.echo("  0. ↩️  Volver al menú principal")
        typer.echo("═" * 60)

        opcion = typer.prompt("❓ Elige una opción [0/1/2/3/4/5/6]")

        if opcion == "0":
            break

        elif opcion == "1":
            if typer.confirm("⚠️  ¿Seguro que deseas eliminar los archivos de migración?"):
                execute_manage_command(["sql", "state", "clear-migrations"])

        elif opcion == "2":
            if typer.confirm("⚠️  ¿Seguro que deseas borrar TODAS las tablas SQL?"):
                execute_manage_command(["sql", "state", "clear-all-tables"])

        elif opcion == "3":
            if typer.confirm("☢️  ¿Seguro que deseas hacer un reset SQL completo (tablas + migraciones)?"):
                execute_manage_command(["sql", "state", "reset", "--hard"])

        elif opcion == "4":
            if typer.confirm("⚠️  ¿Seguro que deseas limpiar todos los documentos de MongoDB?"):
                execute_manage_command(["nosql", "state", "clear"])

        elif opcion == "5":
            if typer.confirm("💣  ¿Seguro que deseas hacer un reset completo de MongoDB?"):
                execute_manage_command(["nosql", "state", "reset"])

        elif opcion == "6":
            typer.echo("")
            typer.echo("☢️  ATENCIÓN: Esta acción reseteará TODO el proyecto a estado cero.")
            typer.echo("     - Borrará todas las tablas SQL")
            typer.echo("     - Eliminará todos los archivos de migración")
            typer.echo("     - Dropeará la base de datos MongoDB")
            typer.echo("")
            if typer.confirm("☢️  ¿Estás COMPLETAMENTE seguro? Esta acción es IRREVERSIBLE"):
                logger.warning("☢️  Iniciando reset TOTAL del proyecto...")
                execute_manage_command(["sql", "state", "reset", "--hard"])
                execute_manage_command(["nosql", "state", "reset"])
                logger.success("✅ Reset TOTAL completado. El proyecto está en estado cero.")
        else:
            logger.warning("⚠️  Opción no válida. Elige entre 0 y 6.")

# =========================================================
# MENÚ PRINCIPAL
# =========================================================
app = typer.Typer(
    help="Comandos para verificar el estado y guiar la configuración del proyecto."
)

@app.command(name="status", help="Menú principal del Project Manager.")
def project_status():

    while True:
        print_header("🚀 TipsterByte FX - Project Manager")
        typer.echo("")
        typer.echo("  1. 📋 Verificar/Configurar el proyecto (project status)")
        typer.echo("  2. 🔴 Resetear el proyecto (estado cero)")
        typer.echo("  0. ❌ Salir")
        typer.echo("")
        typer.echo("═" * 60)

        opcion = typer.prompt("❓ Elige una opción [0/1/2]")

        if opcion == "0":
            logger.info("👋 Hasta luego!")
            break

        elif opcion == "1":
            _run_project_status()

        elif opcion == "2":
            menu_reset()

        else:
            logger.warning("⚠️  Opción no válida. Elige 0, 1 o 2.")

# =========================================================
# LÓGICA PROJECT STATUS (extraída a función privada)
# =========================================================
def _run_project_status():
    logger.info("🚀 Verificando el estado del proyecto TipsterByte...")

    # =====================================================
    # PASO 1: Docker
    # =====================================================
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 1/5: Verificando Docker...")
    try:
        client = docker.from_env()
        pg_container = client.containers.get("db_pg_tipsterbyte_fx")
        mongo_container = client.containers.get("db_mongo_tipsterbyte_fx")

        if pg_container.status == "running" and mongo_container.status == "running":
            print_styled("Docker: Contenedores PostgreSQL y MongoDB están en ejecución.", "ok")
        else:
            print_styled("Docker: Algunos contenedores no están en ejecución.", "warn")
            logger.error("❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)")
            return
    except (NotFound, Exception):
        print_styled("Docker: No se encontraron los contenedores.", "error")
        logger.error("❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)")
        return

    # =====================================================
    # PASO 2: Migraciones SQL
    # =====================================================
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 2/5: Verificando migraciones SQL (PostgreSQL)...")
    sql_status = get_sql_db_status()
    code_only = sql_status.get("code_only", [])
    is_migrated = len(code_only) == 0

    if is_migrated:
        print_styled("PostgreSQL: La base de datos está migrada (tablas creadas).", "ok")
    else:
        print_styled(f"PostgreSQL: Faltan {len(code_only)} tabla(s) por migrar.", "warn")

        migration_created = ask_and_execute(
            "¿Deseas crear el archivo de migración ahora? (python manage.py sql create-migration)",
            ["sql", "create-migration", "-m", "initial_project_structure"]
        )
        if migration_created:
            migrated_now = ask_and_execute(
                "¿Deseas aplicar las migraciones ahora? (python manage.py sql migrate)",
                ["sql", "migrate"]
            )
            if migrated_now:
                sql_status = get_sql_db_status()
                is_migrated = len(sql_status.get("code_only", [])) == 0
                if is_migrated:
                    print_styled("PostgreSQL: ¡Tablas creadas exitosamente!", "ok")
            else:
                logger.warning("⚠️  Sin migraciones aplicadas, los seeders SQL no se ejecutarán.")
        else:
            logger.warning("⚠️  Sin archivo de migración no se puede continuar con SQL.")

    # =====================================================
    # PASO 3: Seeders SQL
    # =====================================================
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 3/5: Verificando datos iniciales SQL...")
    if not is_migrated:
        logger.warning("⏭️  Saltando seeders SQL: las tablas no están migradas.")
    else:
        tables_with_data = sum(
            1 for count in sql_status.get("table_counts", {}).values() if count > 0
        )
        if tables_with_data > 0:
            print_styled(f"PostgreSQL: Hay datos en {tables_with_data} tabla(s).", "ok")
        else:
            print_styled("PostgreSQL: La base de datos está vacía (sin datos iniciales).", "warn")
            ask_and_execute(
                "¿Deseas ejecutar los seeders SQL ahora? (python manage.py seed-sql)",
                ["seed-sql"]
            )

    # =====================================================
    # PASO 4: Esquema MongoDB
    # =====================================================
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 4/5: Verificando esquema MongoDB...")
    mongo_status = get_mongo_db_status()

    if not mongo_status.get("connected"):
        print_styled(f"MongoDB: No se pudo conectar. Error: {mongo_status.get('error')}", "error")
        logger.info("👉 Revisa MONGO_USER / MONGO_PASSWORD en tu .env")
        return

    if mongo_status.get("collections_exist"):
        collections = mongo_status.get("collections", [])
        print_styled(f"MongoDB: Esquema inicializado. {len(collections)} colección(es) encontrada(s).", "ok")
    else:
        print_styled("MongoDB: El esquema no ha sido inicializado (sin colecciones).", "warn")
        schema_created = ask_and_execute(
            "¿Deseas inicializar el esquema de MongoDB ahora? (python manage.py nosql init-schema)",
            ["nosql", "init-schema"]
        )
        if schema_created:
            mongo_status = get_mongo_db_status()

    # =====================================================
    # PASO 5: Seeders MongoDB
    # =====================================================
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 5/5: Verificando datos iniciales MongoDB...")
    if not mongo_status.get("collections_exist"):
        logger.warning("⏭️  Saltando seeders MongoDB: el esquema no está inicializado.")
    else:
        if mongo_status.get("has_data"):
            print_styled("MongoDB: La base de datos tiene datos iniciales.", "ok")
        else:
            print_styled("MongoDB: Las colecciones están vacías.", "warn")
            ask_and_execute(
                "¿Deseas ejecutar los seeders de MongoDB ahora? (python manage.py nosql seed)",
                ["nosql", "seed"]
            )

    # =====================================================
    # RESUMEN FINAL
    # =====================================================
    typer.echo("\n" + "═" * 60)
    final_sql = get_sql_db_status()
    final_mongo = get_mongo_db_status()

    all_ok = (
        len(final_sql.get("code_only", [])) == 0
        and len(final_sql.get("synced", [])) > 0
        and final_mongo.get("collections_exist", False)
        and final_mongo.get("has_data", False)
    )

    if all_ok:
        logger.opt(ansi=True).success("🎉 ¡El proyecto está completamente configurado y listo!")
        print_styled("Inicia el servidor con `python manage.py server run`", "ok")
    else:
        logger.opt(ansi=True).warning("⚠️  Aún hay pasos pendientes. Vuelve a ejecutar `python manage.py project status`")
    typer.echo("═" * 60)






























# import os
# import typer
# from loguru import logger
# import docker
# import subprocess
# import sys
# from docker.errors import NotFound

# from core.db.no_sql.db_inspector import get_mongo_db_status
# from core.db.sql.admin.db_inspector import get_sql_db_status

# styles = {
#     "ok": "<green>",
#     "warn": "<yellow>",
#     "error": "<red>",
#     "info": "<cyan>",
#     "bold": "<bold>",
#     "end": "</>",
# }

# def print_styled(message: str, style: str = "info"):
#     start_tag = styles.get(style, "")
#     end_tag = styles.get("end", "")
#     bold_start = styles.get("bold", "")
#     bold_end = styles.get("end", "")
#     command_part = ""
#     if "`" in message:
#         parts = message.split("`")
#         message = parts[0]
#         command_part = parts[1]
#     logger.opt(ansi=True).info(
#         f"{start_tag}➡️  {message}{bold_start}{command_part}{bold_end}{end_tag}"
#     )

# def execute_manage_command(args: list[str]) -> bool:
#     """Ejecuta un subcomando de manage.py y muestra la salida en tiempo real."""
#     full_command = [sys.executable, "manage.py"] + args
#     logger.info(f"⚙️  Ejecutando: {' '.join(full_command)}")
#     try:
#         # --- CAMBIO CLAVE: Forzar UTF-8 en el entorno del subproceso ---
#         env = os.environ.copy()
#         env["PYTHONIOENCODING"] = "utf-8"
#         env["PYTHONUTF8"] = "1"

#         process = subprocess.Popen(
#             full_command,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             encoding="utf-8",
#             errors="replace",
#             env=env,  # <-- Pasamos el entorno con UTF-8 forzado
#         )
#         if process.stdout:
#             for line in iter(process.stdout.readline, ""):
#                 print(line.strip())
#         process.wait()
#         if process.returncode == 0:
#             logger.success("✅ Comando ejecutado exitosamente.")
#             return True
#         else:
#             logger.error(f"❌ El comando falló con código {process.returncode}.")
#             return False
#     except Exception as e:
#         logger.error(f"❌ Error inesperado: {e}")
#         return False

# def ask_and_execute(question: str, command: list[str]) -> bool:
#     """Pregunta al usuario si desea ejecutar un comando y lo ejecuta si responde 'y'."""
#     typer.echo("")
#     confirmed = typer.confirm(f"❓ {question}")
#     if confirmed:
#         return execute_manage_command(command)
#     else:
#         logger.warning("⏭️  Paso omitido por el usuario.")
#         return False

# app = typer.Typer(
#     help="Comandos para verificar el estado y guiar la configuración del proyecto."
# )

# @app.command(name="status", help="Verifica el estado del proyecto y guía la configuración inicial.")
# def project_status():
#     logger.info("🚀 Verificando el estado del proyecto TipsterByte...")

#     # =========================================================
#     # PASO 1: Docker
#     # =========================================================
#     typer.echo("\n" + "─" * 60)
#     logger.info("📋 PASO 1/5: Verificando Docker...")
#     try:
#         client = docker.from_env()
#         pg_container = client.containers.get("db_pg_tipsterbyte_fx")
#         mongo_container = client.containers.get("db_mongo_tipsterbyte_fx")

#         if pg_container.status == "running" and mongo_container.status == "running":
#             print_styled("Docker: Contenedores PostgreSQL y MongoDB están en ejecución.", "ok")
#         else:
#             print_styled("Docker: Algunos contenedores no están en ejecución.", "warn")
#             logger.error("❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)")
#             return
#     except (NotFound, Exception):
#         print_styled("Docker: No se encontraron los contenedores.", "error")
#         logger.error("❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)")
#         return

#     # =========================================================
#     # PASO 2: Migraciones SQL
#     # =========================================================
#     typer.echo("\n" + "─" * 60)
#     logger.info("📋 PASO 2/5: Verificando migraciones SQL (PostgreSQL)...")
#     sql_status = get_sql_db_status()
#     code_only = sql_status.get("code_only", [])
#     is_migrated = len(code_only) == 0

#     if is_migrated:
#         print_styled("PostgreSQL: La base de datos está migrada (tablas creadas).", "ok")
#     else:
#         print_styled(f"PostgreSQL: Faltan {len(code_only)} tabla(s) por migrar.", "warn")

#         # --- PASO 2A: Primero crear el archivo de migración ---
#         migration_created = ask_and_execute(
#             "¿Deseas crear el archivo de migración inicial ahora? (python manage.py sql create-migration)",
#             ["sql", "create-migration", "-m", "initial_project_structure"]
#         )

#         if migration_created:
#             # --- PASO 2B: Luego aplicar la migración ---
#             migrated_now = ask_and_execute(
#                 "¿Deseas aplicar las migraciones a la base de datos ahora? (python manage.py sql migrate)",
#                 ["sql", "migrate"]
#             )
#             if migrated_now:
#                 sql_status = get_sql_db_status()
#                 is_migrated = len(sql_status.get("code_only", [])) == 0
#                 if is_migrated:
#                     print_styled("PostgreSQL: ¡Tablas creadas exitosamente!", "ok")
#                 else:
#                     logger.warning("⚠️  Las migraciones se aplicaron pero aún hay tablas pendientes.")
#             else:
#                 logger.warning("⚠️  Sin aplicar migraciones, los seeders SQL no se ejecutarán.")
#         else:
#             logger.warning("⚠️  Sin archivo de migración, no se puede continuar con SQL.")

#     # =========================================================
#     # PASO 3: Seeders SQL
#     # =========================================================
#     typer.echo("\n" + "─" * 60)
#     logger.info("📋 PASO 3/5: Verificando datos iniciales SQL...")
#     if not is_migrated:
#         logger.warning("⏭️  Saltando seeders SQL: las tablas no están migradas.")
#     else:
#         tables_with_data = sum(
#             1 for count in sql_status.get("table_counts", {}).values() if count > 0
#         )
#         if tables_with_data > 0:
#             print_styled(f"PostgreSQL: Hay datos en {tables_with_data} tabla(s).", "ok")
#         else:
#             print_styled("PostgreSQL: La base de datos está vacía (sin datos iniciales).", "warn")
#             ask_and_execute(
#                 "¿Deseas ejecutar los seeders SQL ahora? (python manage.py seed-sql)",
#                 ["seed-sql"]
#             )

#     # =========================================================
#     # PASO 4: Esquema MongoDB
#     # =========================================================
#     typer.echo("\n" + "─" * 60)
#     logger.info("📋 PASO 4/5: Verificando esquema MongoDB...")
#     mongo_status = get_mongo_db_status()

#     if not mongo_status.get("connected"):
#         print_styled(f"MongoDB: No se pudo conectar. Error: {mongo_status.get('error')}", "error")
#         logger.info("👉 Revisa MONGO_USER / MONGO_PASSWORD en tu .env")
#         return

#     if mongo_status.get("collections_exist"):
#         collections = mongo_status.get("collections", [])
#         print_styled(f"MongoDB: Esquema inicializado. {len(collections)} colección(es) encontrada(s).", "ok")
#     else:
#         print_styled("MongoDB: El esquema no ha sido inicializado (sin colecciones).", "warn")
#         schema_created = ask_and_execute(
#             "¿Deseas inicializar el esquema de MongoDB ahora? (python manage.py nosql init-schema)",
#             ["nosql", "init-schema"]
#         )
#         if schema_created:
#             mongo_status = get_mongo_db_status()

#     # =========================================================
#     # PASO 5: Seeders MongoDB
#     # =========================================================
#     typer.echo("\n" + "─" * 60)
#     logger.info("📋 PASO 5/5: Verificando datos iniciales MongoDB...")
#     if not mongo_status.get("collections_exist"):
#         logger.warning("⏭️  Saltando seeders MongoDB: el esquema no está inicializado.")
#     else:
#         if mongo_status.get("has_data"):
#             print_styled("MongoDB: La base de datos tiene datos iniciales.", "ok")
#         else:
#             print_styled("MongoDB: Las colecciones están vacías.", "warn")
#             ask_and_execute(
#                 "¿Deseas ejecutar los seeders de MongoDB ahora? (python manage.py nosql seed)",
#                 ["nosql", "seed"]
#             )

#     # =========================================================
#     # RESUMEN FINAL
#     # =========================================================
#     typer.echo("\n" + "═" * 60)
#     final_sql = get_sql_db_status()
#     final_mongo = get_mongo_db_status()

#     all_ok = (
#         # SQL: no hay tablas pendientes de migrar (code_only vacío)
#         len(final_sql.get("code_only", [])) == 0
#         # SQL: hay tablas sincronizadas (al menos una)
#         and len(final_sql.get("synced", [])) > 0
#         # MongoDB: colecciones creadas y con datos
#         and final_mongo.get("collections_exist", False)
#         and final_mongo.get("has_data", False)
#     )

#     if all_ok:
#         # Quitar los debugs temporales
#         logger.opt(ansi=True).success("🎉 ¡El proyecto está completamente configurado y listo!")
#         print_styled("Inicia el servidor con `python manage.py server run`", "ok")
#     else:
#         logger.opt(ansi=True).warning("⚠️  Aún hay pasos pendientes. Vuelve a ejecutar `python manage.py project status`")
#     typer.echo("═" * 60)



