import asyncio
from loguru import logger
from apps.auth.infrastructure.models.mongo.access_log_model import AccessLog
# --- CAMBIO CLAVE: Importamos el inicializador de la BD NoSQL ---
from core.db.no_sql.database_no_sql import init_db_nosql

async def run_migration():
    """
    Añade el campo 'process_name' a los documentos de AccessLog que no lo tengan.
    """
    # --- CAMBIO CLAVE: Inicializamos la conexión ANTES de hacer nada más ---
    await init_db_nosql()
    
    logger.info("🚀 Iniciando migración: Añadir 'process_name' a AccessLog...")
    
    # Buscamos todos los documentos donde el campo 'process_name' no exista
    query = {"process_name": {"$exists": False}}
    
    # Definimos la actualización: añadir el nuevo campo con un valor por defecto
    update_operation = {"$set": {"process_name": "legacy_log"}}
    
    # Ejecutamos la actualización para todos los documentos que coincidan
    result = await AccessLog.get_motor_collection().update_many(query, update_operation)
    
    if result.modified_count > 0:
        logger.success(f"✅ Migración completada. Se actualizaron {result.modified_count} documentos.")
    else:
        logger.info("✅ No se encontraron documentos que necesiten ser migrados.")