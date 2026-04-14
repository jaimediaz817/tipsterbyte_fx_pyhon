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
from core.exceptions.database_exceptions import MongoCollectionNotInitializedException


# --- 1. FUNCIÓN PARA VALIDAR LA CONEXIÓN ---
async def check_mongo_connection() -> bool:
    """
    Valida la conexión y autenticación con MongoDB usando las credenciales de settings.
    Además, muestra los modelos encontrados y el conteo de documentos en cada colección.
    """
    logger.info(
        f"Intentando conectar a MongoDB en: {settings.MONGO_HOST}:{settings.MONGO_PORT}"
    )
    try:
        # Creamos un cliente temporal solo para la validación
        client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)

        # El comando 'ping' es la forma canónica de probar una conexión.
        await client.admin.command("ping")
        logger.success("✅ Conexión y autenticación con MongoDB exitosa.")

        # --- Buscar modelos y mostrar conteo de documentos ---
        logger.info("🔍 Buscando modelos de Beanie y mostrando conteo de documentos...")
        document_models = _find_beanie_models()

        if not document_models:
            logger.warning("No se encontraron modelos de Beanie.")
        else:
            for model in document_models:
                try:
                    model_settings = getattr(model, "Settings", None)
                    collection_name = (
                        model_settings.name
                        if model_settings and hasattr(model_settings, "name")
                        else model.__name__.lower()
                    )
                    document_count = await model.count()
                    logger.info(
                        f"  -> Colección '{collection_name}' ({model.__name__}): {document_count} documentos."
                    )
                except Exception as e:
                    logger.warning(
                        f"No se pudo obtener el conteo para el modelo {model.__name__}: {e}"
                    )
                    logger.info(
                        f"     (Esto es normal si aún no has ejecutado 'init-schema')"
                    )

        # --- GUÍA DE PRÓXIMOS PASOS ---
        print("\n" + "=" * 80)
        print("📋 PRÓXIMOS PASOS PARA CONFIGURAR MONGODB")
        print("=" * 80)

        print("\n🔹 PASO 1: Inicializar esquema (crear colecciones e índices)")
        print("   Comando: python manage.py nosql init-schema")
        print("   Descripción: Crea las colecciones vacías y los índices necesarios")

        print("\n🔹 PASO 2: Ejecutar migraciones de datos")
        print("   Comando: python manage.py nosql-migrate run")
        print(
            "   Descripción: Aplica migraciones como agregar campos a documentos existentes"
        )

        print("\n🔹 PASO 3: (OPCIONAL) Ejecutar seeders")
        print("   Comando: python manage.py nosql seed")
        print("   Descripción: Puebla la base de datos con datos de ejemplo")

        print("\n🔹 PASO 4: (OPCIONAL) Crear backup")
        print("   Comando: python manage.py nosql state backup")
        print("   Descripción: Crea un backup de la base de datos MongoDB")

        print("\n" + "-" * 80)
        print("💡 CONSEJO: Ejecuta los comandos en orden (1, 2, 3, 4)")
        print("   Si solo necesitas la estructura, ejecuta solo los pasos 1 y 2")
        print("=" * 80 + "\n")

        return True
    except OperationFailure as e:
        error_msg = e.details.get("errmsg", str(e)) if e.details else str(e)
        logger.error(f"❌ Fallo de autenticación en MongoDB: {error_msg}")
        logger.error(
            "Verifica que MONGO_USER, MONGO_PASSWORD y authSource en MONGO_URI sean correctos."
        )
        return False
    except ConnectionFailure as e:
        logger.error(f"❌ No se pudo conectar al servidor de MongoDB: {e}")
        logger.error(
            "Asegúrate de que el contenedor Docker de MongoDB esté corriendo y sea accesible."
        )
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
                if (
                    issubclass(obj, Document)
                    and obj is not Document
                    and obj not in models
                ):
                    logger.debug(
                        f"  -> Modelo encontrado: {obj.__name__} en {module_path}"
                    )
                    models.append(obj)
        except Exception as e:
            logger.warning(
                f"No se pudo importar o inspeccionar el módulo {module_path}: {e}"
            )

    # --- CAMBIO: Log final para resumir la búsqueda ---
    logger.info(
        f"Búsqueda completada. Se procesaron {file_count} archivos y se encontraron {len(models)} modelos."
    )
    return models


def _get_collection_name(model: Type[Document]) -> str:
    """
    ✅ SRP: Funcion única responsabilidad: Obtener nombre de coleccion desde un modelo Beanie
    """
    model_settings = getattr(model, "Settings", None)
    return (
        model_settings.name
        if model_settings and hasattr(model_settings, "name")
        else model.__name__.lower()
    )


async def validate_collections_existence() -> None:
    """
    ✅ SRP: Valida que TODOS los modelos tengan su coleccion creada fisicamente en MongoDB
    Lanza MongoCollectionNotInitializedException si alguna coleccion falta
    Muestra tabla ASCII con estado completo
    """
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_database(settings.MONGO_DB)

    document_models = _find_beanie_models()
    existing_collections = await db.list_collection_names()

    missing_collections = []
    status_table = []

    logger.info("\n" + "=" * 80)
    logger.info("📊 ESTADO DE COLECCIONES MONGODB")
    logger.info("=" * 80)

    print(f"\n{'N°':<3} {'MODELO':<30} {'COLECCION':<30} {'ESTADO':<10}")
    print(f"{'-'*3} {'-'*30} {'-'*30} {'-'*10}")

    for idx, model in enumerate(document_models, 1):
        collection_name = _get_collection_name(model)
        exists = collection_name in existing_collections

        status = "✅ OK" if exists else "❌ FALTANTE"
        print(f"{idx:<3} {model.__name__:<30} {collection_name:<30} {status:<10}")

        if not exists:
            missing_collections.append(
                {"model": model.__name__, "collection": collection_name}
            )

    print("\n" + "-" * 80)

    if missing_collections:
        total_missing = len(missing_collections)
        logger.error(
            f"\n❌ SE ENCONTRARON {total_missing} COLECCIONES NO INICIALIZADAS"
        )
        logger.error("=============================================================")
        logger.error("⚠️  CAUSA: NUNCA SE EJECUTO COMANDO DE INICIALIZACION")
        logger.error("")
        logger.error("💡 SOLUCION: Ejecuta este comando:")
        logger.error("")
        logger.error("   python backend/manage.py nosql init-schema")
        logger.error("")
        logger.error("📌 Este comando crea automaticamente todas las colecciones")
        logger.error("=============================================================\n")

        # Lanzar excepcion personalizada con la primera coleccion faltante
        first_missing = missing_collections[0]
        raise MongoCollectionNotInitializedException(
            collection=first_missing["collection"],
            model_name=first_missing["model"],
            details=f"Faltan {total_missing} colecciones en total",
        )
    else:
        logger.success("\n✅ TODAS LAS COLECCIONES ESTAN INICIALIZADAS CORRECTAMENTE")
        logger.success(f"Total modelos validados: {len(document_models)}")


async def initialize_mongo_schema():
    """
    Inicializa la base de datos MongoDB, creando colecciones e índices
    basados en todos los modelos de Beanie encontrados en el proyecto.
    """
    logger.info("🚀 Iniciando la inicialización del esquema de MongoDB...")

    # Primero, validamos que podamos conectar
    if not await check_mongo_connection():
        logger.error(
            "La inicialización del esquema no puede continuar sin una conexión válida."
        )
        return

    # Encontrar todos los modelos
    document_models = _find_beanie_models()

    if not document_models:
        logger.warning(
            "No se encontraron modelos de Beanie. No hay nada que inicializar."
        )
        return

    logger.info(
        f"Modelos a inicializar: {[model.__name__ for model in document_models]}"
    )

    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client.get_database(settings.MONGO_DB)

        # Inicializa Beanie con los modelos encontrados
        await init_beanie(database=db, document_models=document_models)  # type: ignore[arg-type]
        logger.success(
            "✅ Esquema de Beanie inicializado. Los índices han sido creados o verificados."
        )

        # --- Crear colecciones vacías manualmente ---
        logger.info("🔍 Verificando y creando colecciones vacías si no existen...")
        for model in document_models:
            try:
                model_settings = getattr(model, "Settings", None)
                collection_name = (
                    model_settings.name
                    if model_settings and hasattr(model_settings, "name")
                    else model.__name__.lower()
                )
                existing_collections = await db.list_collection_names()
                if collection_name not in existing_collections:
                    await db.create_collection(collection_name)
                    logger.info(
                        f"  -> Colección '{collection_name}' creada exitosamente (vacía)."
                    )
                else:
                    logger.info(f"  -> Colección '{collection_name}' ya existe.")
            except Exception as e:
                logger.warning(
                    f"No se pudo crear la colección para el modelo {model.__name__}: {e}"
                )

    except Exception as e:
        logger.error(f"❌ Ocurrió un error durante la inicialización de Beanie: {e}")
