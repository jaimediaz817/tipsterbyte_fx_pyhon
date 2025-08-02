# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\core\db\database_nosql.py
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from apps.auth.infrastructure.models.mongo.access_log_model import AccessLog
from core.config import settings
# --- CAMBIO CLAVE: Importamos el nuevo modelo ---


async def init_db_nosql():
    """
    Inicializa la conexión a la base de datos NoSQL (MongoDB) y registra los modelos de Beanie.
    """
    logger.info("🔌 Conectando a la base de datos NoSQL (MongoDB)...")
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        
        # --- CAMBIO CLAVE: Añadimos el modelo a la lista de documentos ---
        await init_beanie(
            database=client[settings.MONGO_DB],
            document_models=[
                AccessLog,
                # ... aquí irán tus futuros modelos de Beanie
            ]
        )
        logger.success("✅ Conexión a MongoDB y registro de modelos Beanie exitosos.")
    except Exception as e:
        logger.error(f"❌ Falló la inicialización de la base de datos NoSQL: {e}")
        raise