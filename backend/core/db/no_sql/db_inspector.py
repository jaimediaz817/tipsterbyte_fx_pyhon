from typing import Any
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from core.config import settings


def get_mongo_db_status(expected_collections: list[str] | None = None) -> dict[str, Any]:
    status: dict[str, Any] = {
        "connected": False,
        "db_exists": False,
        "collections_exist": False,
        "has_data": False, # <-- NUEVA CLAVE
        "collections": [],
        "missing_collections": [],
        "error": None,
    }

    client = None
    try:
        client = MongoClient(str(settings.MONGO_URI), serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        status["connected"] = True

        db = client[settings.MONGO_DB]
        collections = sorted(db.list_collection_names())
        status["collections"] = collections
        status["db_exists"] = len(collections) > 0

        if expected_collections:
            missing = [c for c in expected_collections if c not in collections]
            status["missing_collections"] = missing
            status["collections_exist"] = len(missing) == 0
        else:
            status["collections_exist"] = len(collections) > 0

        # --- LÓGICA AÑADIDA PARA VERIFICAR DATOS ---
        if status["collections_exist"]:
            for collection_name in collections:
                # Si encontramos al menos un documento en cualquier colección, es suficiente.
                if db[collection_name].count_documents({}, limit=1) > 0:
                    status["has_data"] = True
                    break
        # --- FIN DE LA LÓGICA AÑADIDA ---

    except PyMongoError as e:
        status["error"] = str(e)
    finally:
        if client is not None:
            client.close()

    return status