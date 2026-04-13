import os
import typer
from loguru import logger
import subprocess
import sys
from typing import Any

# Importación opcional de docker (solo se usa para verificar contenedores)
try:
    import docker
    from docker.errors import NotFound

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None
    NotFound = Exception

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


def _clear_pycache():
    """Limpia todos los directorios __pycache__ del proyecto."""
    import shutil
    from pathlib import Path

    logger.info("🧹 Iniciando limpieza de cache (__pycache__)...")

    # Directorio raíz del backend
    backend_root = Path(__file__).resolve().parent.parent

    pycache_dirs = list(backend_root.rglob("__pycache__"))

    if not pycache_dirs:
        print_styled("No se encontraron directorios __pycache__ para limpiar.", "info")
        return

    print_styled(
        f"Se encontraron {len(pycache_dirs)} directorio(s) __pycache__.", "info"
    )

    if typer.confirm("¿Deseas eliminarlos?"):
        deleted_count = 0
        for pycache_dir in pycache_dirs:
            try:
                shutil.rmtree(pycache_dir)
                logger.trace(f"Eliminado: {pycache_dir}")
                deleted_count += 1
            except Exception as e:
                logger.error(f"No se pudo eliminar {pycache_dir}: {e}")

        print_styled(
            f"✅ Limpieza completada. Se eliminaron {deleted_count} directorio(s).",
            "ok",
        )
    else:
        logger.warning("⏭️  Limpieza cancelada por el usuario.")


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
            if typer.confirm(
                "⚠️  ¿Seguro que deseas eliminar los archivos de migración?"
            ):
                execute_manage_command(["sql", "state", "clear-migrations"])

        elif opcion == "2":
            if typer.confirm("⚠️  ¿Seguro que deseas borrar TODAS las tablas SQL?"):
                execute_manage_command(["sql", "state", "clear-all-tables"])

        elif opcion == "3":
            if typer.confirm(
                "☢️  ¿Seguro que deseas hacer un reset SQL completo (tablas + migraciones)?"
            ):
                execute_manage_command(["sql", "state", "reset", "--hard"])

        elif opcion == "4":
            if typer.confirm(
                "⚠️  ¿Seguro que deseas limpiar todos los documentos de MongoDB?"
            ):
                execute_manage_command(["nosql", "state", "clear"])

        elif opcion == "5":
            if typer.confirm(
                "💣  ¿Seguro que deseas hacer un reset completo de MongoDB?"
            ):
                execute_manage_command(["nosql", "state", "reset"])

        elif opcion == "6":
            typer.echo("")
            typer.echo(
                "☢️  ATENCIÓN: Esta acción reseteará TODO el proyecto a estado cero."
            )
            typer.echo("     - Borrará todas las tablas SQL")
            typer.echo("     - Eliminará todos los archivos de migración")
            typer.echo("     - Dropeará la base de datos MongoDB")
            typer.echo("")
            if typer.confirm(
                "☢️  ¿Estás COMPLETAMENTE seguro? Esta acción es IRREVERSIBLE"
            ):
                logger.warning("☢️  Iniciando reset TOTAL del proyecto...")
                execute_manage_command(["sql", "state", "reset", "--hard"])
                execute_manage_command(["nosql", "state", "reset"])
                logger.success(
                    "✅ Reset TOTAL completado. El proyecto está en estado cero."
                )
        else:
            logger.warning("⚠️  Opción no válida. Elige entre 0 y 6.")


# =========================================================
# MENÚ PRINCIPAL
# =========================================================
app = typer.Typer(
    help="Comandos para verificar el estado y guiar la configuración del proyecto."
)


# =========================================================
# COMANDO CONFIG - Diagnóstico de Configuración
# =========================================================
@app.command(
    name="config", help="Muestra el estado actual de la configuración del sistema."
)
def project_config():
    """Muestra diagnóstico completo de todas las variables de configuración."""
    from core.config import settings

    typer.echo("\n" + "=" * 70)
    typer.secho(
        "        CONFIGURACION ACTUAL - TipsterByte FX", fg=typer.colors.CYAN, bold=True
    )
    typer.echo("=" * 70)

    # ── EXTRACCION AUTOMATICA DE CAMPOS ──
    # Usamos dir() + __annotations__ para obtener TODOS los campos definidos en Settings
    # Excluimos métodos privados y atributos internos de Pydantic
    all_attrs = dir(settings)
    fields = {}
    for attr_name in all_attrs:
        # Excluir métodos, atributos privados y atributos internos de Pydantic
        if (
            not attr_name.startswith("_")
            and attr_name
            not in ["model_config", "model_fields", "model_computed_fields"]
            and not callable(getattr(settings, attr_name, None))
        ):
            fields[attr_name] = True

    # Categorizar campos automaticamente
    categories = _categorize_fields(fields)

    # Mostrar cada categoria
    for category, field_names in categories.items():
        if field_names:
            typer.echo(f"\n-- {category.upper()} " + "-" * (60 - len(category)))
            for field_name in field_names:
                value = getattr(settings, field_name, None)
                # Determinar status automaticamente
                status = _determine_status(field_name, value)
                # Enmascarar valores sensibles automaticamente
                mask = _should_mask(field_name)
                _print_setting(field_name, value, status, mask=mask)

    typer.echo("\n" + "=" * 70)


def _categorize_fields(fields: dict) -> dict[str, list[str]]:
    """Categoriza automáticamente los campos por tipo."""
    # Campos internos de Pydantic que NO son configuraciones del usuario
    PYDANTIC_INTERNAL_FIELDS = {
        "model_config",
        "model_extra",
        "model_fields_set",
        "model_computed_fields",
    }

    categories = {
        "ENTORNO": [],
        "LOGGING": [],
        "BASE DE DATOS": [],
        "CONCURRENCIA": [],
        "LOGS": [],
        "SELENIUM": [],
        "OTROS": [],
    }

    for field_name in fields.keys():
        # Excluir campos internos de Pydantic y campos privados
        if field_name.startswith("_") or field_name in PYDANTIC_INTERNAL_FIELDS:
            continue

        # Categorizar por nombre del campo
        field_lower = field_name.lower()

        if any(x in field_lower for x in ["env", "debug", "environment"]):
            categories["ENTORNO"].append(field_name)
        elif any(x in field_lower for x in ["log_level", "logging", "file_logging"]):
            categories["LOGGING"].append(field_name)
        elif any(x in field_lower for x in ["database", "postgres", "mongo", "db"]):
            categories["BASE DE DATOS"].append(field_name)
        elif any(x in field_lower for x in ["concurrent", "pool", "overflow"]):
            categories["CONCURRENCIA"].append(field_name)
        elif any(
            x in field_lower for x in ["retention", "archive", "cleanup", "alembic"]
        ):
            categories["LOGS"].append(field_name)
        elif any(x in field_lower for x in ["selenium", "hub"]):
            categories["SELENIUM"].append(field_name)
        else:
            categories["OTROS"].append(field_name)

    return categories


def _determine_status(field_name: str, value: Any) -> str:
    """Determina automáticamente el status basado en el tipo y valor."""
    if isinstance(value, bool):
        return "ok" if value else "warn"
    if isinstance(value, str):
        if any(x in field_name.lower() for x in ["url", "uri", "database"]):
            return "info"
    return "info"


def _should_mask(field_name: str) -> bool:
    """Determina si un campo debe ser enmascarado (contiene credenciales)."""
    sensitive_keywords = ["password", "secret", "uri", "url", "database", "key"]
    return any(keyword in field_name.lower() for keyword in sensitive_keywords)


def _print_setting(key: str, value: Any, status: str = "info", mask: bool = False):
    """Imprime una configuración con formato y colores."""
    colors = {
        "ok": typer.colors.GREEN,
        "warn": typer.colors.YELLOW,
        "error": typer.colors.RED,
        "info": typer.colors.CYAN,
    }

    color = colors.get(status, typer.colors.WHITE)

    # Formatear valor
    if mask and isinstance(value, str):
        if "://" in value:
            # Enmascarar credenciales
            parts = value.split("://")
            if len(parts) > 1:
                value_str = f"{parts[0]}://***"
            else:
                value_str = value
        else:
            value_str = value[:20] + "***" if len(value) > 20 else value
    elif isinstance(value, bool):
        value_str = "True" if value else "False"
    else:
        value_str = str(value)

    # Indicador de estado
    status_indicator = ""
    if isinstance(value, bool):
        status_indicator = " [ACTIVO]" if value else " [INACTIVO]"

    typer.echo(f"  {key:<35} = ", nl=False)
    typer.secho(f"{value_str}", fg=color, bold=True, nl=False)
    if status_indicator:
        typer.secho(status_indicator, fg=color)
    else:
        typer.echo()


@app.command(name="status", help="Menú principal del Project Manager.")
def project_status():

    while True:
        print_header("🚀 TipsterByte FX - Project Manager")
        typer.echo("")
        typer.echo("  1. 📋 Verificar/Configurar el proyecto (project status)")
        typer.echo("  2. 🔴 Resetear el proyecto (estado cero)")
        typer.echo("  3. 🧹 Refrescar Cache (limpiar __pycache__)")
        typer.echo("  0. ❌ Salir")
        typer.echo("")
        typer.echo("═" * 60)

        opcion = typer.prompt("❓ Elige una opción [0/1/2/3]")

        if opcion == "0":
            logger.info("👋 Hasta luego!")
            break

        elif opcion == "1":
            _run_project_status()

        elif opcion == "2":
            menu_reset()

        elif opcion == "3":
            _clear_pycache()

        else:
            logger.warning("⚠️  Opción no válida. Elige 0, 1, 2 o 3.")


# =========================================================
# LÓGICA PROJECT STATUS (refactorizada con funciones auxiliares)
# =========================================================


def _check_docker() -> bool:
    """Verifica el estado de los contenedores Docker. Retorna True si todo está OK."""
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 1/5: Verificando Docker...")

    if not DOCKER_AVAILABLE:
        print_styled(
            "Docker: Módulo docker no instalado. Saltando verificación.", "warn"
        )
        logger.info(
            "💡 Para habilitar la verificación de Docker, instala: pip install docker"
        )
        return True

    try:
        assert docker is not None
        client = docker.from_env()

        # Buscar contenedores por patrón (compatibilidad con _dev y _prod)
        todos_contenedores = client.containers.list(all=True)

        pg_container = None
        mongo_container = None

        for contenedor in todos_contenedores:
            nombre: str | None = getattr(contenedor, "name", None)
            if nombre and nombre.startswith("db_pg_tipsterbyte_fx"):
                pg_container = contenedor
            if nombre and nombre.startswith("db_mongo_tipsterbyte_fx"):
                mongo_container = contenedor

        if not pg_container or not mongo_container:
            print_styled("Docker: No se encontraron los contenedores.", "error")
            logger.error(
                "❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)"
            )
            return False

        containers_running = (
            pg_container.status == "running" and mongo_container.status == "running"
        )

        if containers_running:
            nombre_pg: str | None = getattr(pg_container, "name", None)
            entorno = (
                "DESARROLLO"
                if nombre_pg and "dev" in nombre_pg
                else "PRODUCCION" if nombre_pg and "prod" in nombre_pg else ""
            )
            mensaje = f"Docker: Contenedores PostgreSQL y MongoDB están en ejecución. ({entorno})"
            print_styled(mensaje, "ok")
            return True

        print_styled("Docker: Algunos contenedores no están en ejecución.", "warn")
        logger.error(
            "❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)"
        )
        return False

    except (NotFound, Exception) as e:
        print_styled(f"Docker: Error al verificar contenedores: {str(e)}", "error")
        logger.error(
            "❌ Problema crítico. Ejecuta: docker-compose up -d (raíz del proyecto)"
        )
        return False


def _check_sql_migrations() -> tuple[bool, dict]:
    """Verifica el estado de las migraciones SQL. Retorna (is_migrated, sql_status)."""
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 2/5: Verificando migraciones SQL (PostgreSQL)...")

    sql_status = get_sql_db_status()
    code_only = sql_status.get("code_only", [])
    is_migrated = len(code_only) == 0

    if is_migrated:
        print_styled(
            "PostgreSQL: La base de datos está migrada (tablas creadas).", "ok"
        )
        return True, sql_status

    print_styled(f"PostgreSQL: Faltan {len(code_only)} tabla(s) por migrar.", "warn")

    migration_created = ask_and_execute(
        "¿Deseas crear el archivo de migración ahora? (python manage.py sql create-migration)",
        ["sql", "create-migration", "-m", "initial_project_structure"],
    )

    if not migration_created:
        logger.warning("⚠️  Sin archivo de migración no se puede continuar con SQL.")
        return False, sql_status

    migrated_now = ask_and_execute(
        "¿Deseas aplicar las migraciones ahora? (python manage.py sql migrate)",
        ["sql", "migrate"],
    )

    if not migrated_now:
        logger.warning(
            "⚠️  Sin migraciones aplicadas, los seeders SQL no se ejecutarán."
        )
        return False, sql_status

    sql_status = get_sql_db_status()
    is_migrated = len(sql_status.get("code_only", [])) == 0

    if is_migrated:
        print_styled("PostgreSQL: ¡Tablas creadas exitosamente!", "ok")

    return is_migrated, sql_status


def _check_sql_seeders(is_migrated: bool, sql_status: dict) -> None:
    """Verifica y opcionalmente ejecuta los seeders SQL."""
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 3/5: Verificando datos iniciales SQL...")

    if not is_migrated:
        logger.warning("⏭️  Saltando seeders SQL: las tablas no están migradas.")
        return

    # Tablas que NO contienen datos de negocio inicial (se generan automaticamente)
    TABLAS_AUTOGENERADAS = {
        "process_run",
        "process_run_log",
        "alembic_version",
        "access_log",
        "session_log",
        "audit_log",
    }

    # Contar cuantas tablas tienen datos en total
    total_tablas_con_datos = sum(
        1 for conteo in sql_status.get("table_counts", {}).values() if conteo > 0
    )

    # Contar solo tablas de negocio que deberian tener datos de seed
    tablas_negocio_con_datos = sum(
        1
        for nombre, conteo in sql_status.get("table_counts", {}).items()
        if nombre not in TABLAS_AUTOGENERADAS and conteo > 0
    )

    # Si NO HAY DATOS en NINGUNA tabla (o solo en tablas autogeneradas)
    if total_tablas_con_datos == 0 or tablas_negocio_con_datos == 0:
        print_styled(
            "PostgreSQL: No hay datos iniciales cargados.",
            "warn",
        )
        ask_and_execute(
            "¿Deseas ejecutar los seeders SQL ahora? (python manage.py sql seed)",
            ["sql", "seed"],
        )
        return

    # Si ya hay datos
    print_styled(
        f"PostgreSQL: Hay datos en {total_tablas_con_datos} tabla(s).",
        "ok",
    )


def _check_mongo_schema() -> tuple[bool, dict]:
    """Verifica el esquema de MongoDB. Retorna (schema_exists, mongo_status)."""
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 4/5: Verificando esquema MongoDB...")

    mongo_status = get_mongo_db_status()

    if not mongo_status.get("connected"):
        print_styled(
            f"MongoDB: No se pudo conectar. Error: {mongo_status.get('error')}", "error"
        )
        logger.info("👉 Revisa MONGO_USER / MONGO_PASSWORD en tu .env")
        return False, mongo_status

    if mongo_status.get("collections_exist"):
        collections = mongo_status.get("collections", [])
        total_documentos = 0
        conteo_por_coleccion = {}

        # Obtener conteo de documentos por coleccion
        try:
            from pymongo import MongoClient
            from core.config import settings

            client = MongoClient(str(settings.MONGO_URI), serverSelectionTimeoutMS=2000)
            db = client[settings.MONGO_DB]

            for collection_name in collections:
                conteo = db[collection_name].count_documents({})
                conteo_por_coleccion[collection_name] = conteo
                total_documentos += conteo

            client.close()
        except Exception:
            pass

        print_styled(
            f"MongoDB: Esquema inicializado. {len(collections)} colección(es) | {total_documentos} documentos totales.",
            "ok",
        )

        # Mostrar detalle de cada coleccion si hay pocas
        if len(collections) <= 10:
            for nombre, conteo in conteo_por_coleccion.items():
                logger.info(f"  📋 {nombre:<30} → {conteo:>6} documentos")

        return True, mongo_status

    print_styled(
        "MongoDB: El esquema no ha sido inicializado (sin colecciones).", "warn"
    )

    schema_created = ask_and_execute(
        "¿Deseas inicializar el esquema de MongoDB ahora? (python manage.py nosql init-schema)",
        ["nosql", "init-schema"],
    )

    if schema_created:
        mongo_status = get_mongo_db_status()

    return mongo_status.get("collections_exist", False), mongo_status


def _check_mongo_seeders(collections_exist: bool, mongo_status: dict) -> None:
    """Verifica y opcionalmente ejecuta los seeders de MongoDB."""
    typer.echo("\n" + "─" * 60)
    logger.info("📋 PASO 5/5: Verificando datos iniciales MongoDB...")

    if not collections_exist:
        logger.warning("⏭️  Saltando seeders MongoDB: el esquema no está inicializado.")
        return

    if mongo_status.get("has_data"):
        print_styled("MongoDB: La base de datos tiene datos iniciales.", "ok")
        return

    print_styled("MongoDB: Las colecciones están vacías.", "warn")
    ask_and_execute(
        "¿Deseas ejecutar los seeders de MongoDB ahora? (python manage.py nosql seed)",
        ["nosql", "seed"],
    )


def _print_final_summary() -> None:
    """Imprime el resumen final del estado del proyecto."""
    typer.echo("\n" + "═" * 60)

    final_sql = get_sql_db_status()
    final_mongo = get_mongo_db_status()

    sql_ok = (
        len(final_sql.get("code_only", [])) == 0
        and len(final_sql.get("synced", [])) > 0
    )
    mongo_ok = final_mongo.get("collections_exist", False) and final_mongo.get(
        "has_data", False
    )
    all_ok = sql_ok and mongo_ok

    if all_ok:
        logger.opt(ansi=True).success(
            "🎉 ¡El proyecto está completamente configurado y listo!"
        )
        print_styled("Inicia el servidor con `python manage.py server run`", "ok")
    else:
        logger.opt(ansi=True).warning(
            "⚠️  Aún hay pasos pendientes. Vuelve a ejecutar `python manage.py project status`"
        )

    typer.echo("═" * 60)


def _run_project_status():
    """Función principal que ejecuta la verificación completa del estado del proyecto."""
    logger.info("🚀 Verificando el estado del proyecto TipsterByte...")

    # PASO 1: Docker
    if not _check_docker():
        return

    # PASO 2: Migraciones SQL
    is_migrated, sql_status = _check_sql_migrations()

    # PASO 3: Seeders SQL
    _check_sql_seeders(is_migrated, sql_status)

    # PASO 4: Esquema MongoDB
    collections_exist, mongo_status = _check_mongo_schema()
    if not mongo_status.get("connected"):
        return

    # PASO 5: Seeders MongoDB
    _check_mongo_seeders(collections_exist, mongo_status)

    # RESUMEN FINAL
    _print_final_summary()
