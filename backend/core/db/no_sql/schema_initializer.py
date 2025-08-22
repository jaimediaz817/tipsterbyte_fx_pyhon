import importlib
import inspect
from pathlib import Path
from typing import List, Type

from beanie import Document
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, OperationFailure
from beanie import init_beanie

from core.config import settings
from core.paths import BACKEND_ROOT

# --- 1. FUNCIÓN PARA VALIDAR LA CONEXIÓN ---
async def check_mongo_connection() -> bool:
    """
    Valida la conexión y autenticación con MongoDB usando las credenciales de settings.
    Además, muestra los modelos encontrados y el conteo de documentos en cada colección.
    """
    logger.info(f"Intentando conectar a MongoDB en: {settings.MONGO_HOST}:{settings.MONGO_PORT}")
    try:
        # Creamos un cliente temporal solo para la validación
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # El comando 'ping' es la forma canónica de probar una conexión.
        await client.admin.command('ping')
        logger.success("✅ Conexión y autenticación con MongoDB exitosa.")

        # --- Buscar modelos y mostrar conteo de documentos ---
        logger.info("🔍 Buscando modelos de Beanie y mostrando conteo de documentos...")
        document_models = _find_beanie_models()

        if not document_models:
            logger.warning("No se encontraron modelos de Beanie.")
        else:
            for model in document_models:
                try:
                    collection_name = model.Settings.name if hasattr(model.Settings, "name") else model.__name__.lower()
                    document_count = await model.count()
                    logger.info(f"  -> Colección '{collection_name}' ({model.__name__}): {document_count} documentos.")
                except Exception as e:
                    logger.warning(f"No se pudo obtener el conteo para el modelo {model.__name__}: {e}")

        return True
    except OperationFailure as e:
        logger.error(f"❌ Fallo de autenticación en MongoDB: {e.details.get('errmsg', e)}")
        logger.error("Verifica que MONGO_USER, MONGO_PASSWORD y authSource en MONGO_URI sean correctos.")
        return False
    except ConnectionFailure as e:
        logger.error(f"❌ No se pudo conectar al servidor de MongoDB: {e}")
        logger.error("Asegúrate de que el contenedor Docker de MongoDB esté corriendo y sea accesible.")
        return False
    except Exception as e:
        logger.error(f"❌ Ocurrió un error inesperado al conectar con MongoDB: {e}")
        return False

# --- 2. FUNCIONES PARA INICIALIZAR EL ESQUEMA ---

def _find_beanie_models() -> List[Type[Document]]:
    """
    Busca dinámicamente todas las clases que heredan de beanie.Document en la carpeta 'apps'.
    """
    models = []
    apps_dir = BACKEND_ROOT / "apps"
    logger.info(f"Buscando modelos de Beanie en el directorio: {apps_dir}")

    # --- CAMBIO: Añadir un contador para saber cuántos archivos se procesan ---
    file_count = 0
    for path in apps_dir.rglob("*.py"):
        file_count += 1
        # Ignorar archivos de inicialización o tests
        if path.name.startswith(("_", "test_")):
            continue

        # Convertir la ruta del archivo a un nombre de módulo importable (e.g., apps.auth.infrastructure.models.mongo.access_log_model)
        module_path = ".".join(path.relative_to(BACKEND_ROOT).with_suffix("").parts)
        
        try:
            # --- CAMBIO: Log para ver qué módulo se está intentando importar ---
            logger.trace(f"Intentando importar módulo: {module_path}")
            module = importlib.import_module(module_path)
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Document) and obj is not Document and obj not in models:
                    logger.debug(f"  -> Modelo encontrado: {obj.__name__} en {module_path}")
                    models.append(obj)
        except Exception as e:
            logger.warning(f"No se pudo importar o inspeccionar el módulo {module_path}: {e}")
    
    # --- CAMBIO: Log final para resumir la búsqueda ---
    logger.info(f"Búsqueda completada. Se procesaron {file_count} archivos y se encontraron {len(models)} modelos.")
    return models

async def initialize_mongo_schema():
    """
    Inicializa la base de datos MongoDB, creando colecciones e índices
    basados en todos los modelos de Beanie encontrados en el proyecto.
    """
    logger.info("🚀 Iniciando la inicialización del esquema de MongoDB...")
    
    # Primero, validamos que podamos conectar
    if not await check_mongo_connection():
        logger.error("La inicialización del esquema no puede continuar sin una conexión válida.")
        return

    # Encontrar todos los modelos
    document_models = _find_beanie_models()

    if not document_models:
        logger.warning("No se encontraron modelos de Beanie. No hay nada que inicializar.")
        return

    logger.info(f"Modelos a inicializar: {[model.__name__ for model in document_models]}")

    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB]
        
        # Inicializa Beanie con los modelos encontrados
        await init_beanie(
            database=db,
            document_models=document_models
        )
        logger.success("✅ Esquema de Beanie inicializado. Los índices han sido creados o verificados.")

        # --- Crear colecciones vacías manualmente ---
        logger.info("🔍 Verificando y creando colecciones vacías si no existen...")
        for model in document_models:
            try:
                collection_name = model.Settings.name if hasattr(model.Settings, "name") else model.__name__.lower()
                existing_collections = await db.list_collection_names()
                
                if collection_name not in existing_collections:
                    await db.create_collection(collection_name)
                    logger.info(f"  -> Colección '{collection_name}' creada exitosamente (vacía).")
                else:
                    logger.info(f"  -> Colección '{collection_name}' ya existe.")
            except Exception as e:
                logger.warning(f"No se pudo crear la colección para el modelo {model.__name__}: {e}")

    except Exception as e:
        logger.error(f"❌ Ocurrió un error durante la inicialización de Beanie: {e}")