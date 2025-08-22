# # Creamos la "sub-app" de Typer para los comandos SQL
# import subprocess
# from loguru import logger
# import typer
# from core.db.sql.admin.db_inspector import get_sql_db_status
# from core.logger import configure_logging


# sql_app = typer.Typer(name="sql", help="Gestiona la base de datos relacional (PostgreSQL).")

# @sql_app.command("status")
# def db_status():
#     """Muestra el estado de sincronización de los modelos y las migraciones."""
#     configure_logging()
#     logger.info("🔍 Verificando estado de la base de datos SQL...")

#     # Parte 1: Compara modelos vs. tablas
#     logger.info("--- Estado de Modelos vs. Tablas en la Base de Datos ---")
#     status = get_sql_db_status()

#     if status["synced"]:
#         logger.success("✅ Modelos Sincronizados:")
#         for table in status["synced"]: print(f"  - {table}")
    
#     if status["code_only"]:
#         logger.warning("⚠️  Modelos en código que FALTAN en la Base de Datos (necesitan migración):")
#         for table in status["code_only"]: print(f"  - {table}")

#     db_only_filtered = [t for t in status["db_only"] if t != 'alembic_version']
#     if db_only_filtered:
#         logger.info("ℹ️ Tablas en la Base de Datos que NO están en el código (posiblemente obsoletas):")
#         for table in db_only_filtered: print(f"  - {table}")

#     # Parte 2: Verifica el estado de Alembic
#     logger.info("\n--- Estado de Migraciones (Alembic) ---")
#     try:
#         logger.info("Revisión actual en la base de datos:")
#         subprocess.run(["alembic", "current"], check=True)
#         logger.info("\nComprobando si se necesita una nueva migración...")
#         check_result = subprocess.run(["alembic", "check"], capture_output=True, text=True)
#         if check_result.returncode == 0:
#             logger.success("✅ Los modelos y las migraciones están sincronizados.")
#         else:
#             logger.error("❌ ¡Se detectaron cambios en los modelos que no están en un archivo de migración!")
#             logger.warning("Ejecuta 'python manage.py sql create-migration \"tu mensaje\"' para crear la migración.")
#     except Exception as e:
#         logger.error(f"❌ Ocurrió un error al ejecutar Alembic: {e}")