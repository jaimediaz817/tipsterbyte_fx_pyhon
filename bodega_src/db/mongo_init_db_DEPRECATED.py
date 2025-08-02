import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from backend.core.config import Settings
# from core.config import settings
# Importa aquí tus futuros modelos de Beanie. Ejemplo:
# from app.db.models.mongo.user_log import UserActivityLog
# from app.db.models.mongo.ml_experiment import MLExperiment

async def init_mongo_db():
    """
    Initializes the MongoDB connection and Beanie ODM.
    """
    mongo_uri = Settings.MONGO_URI  # Asegúrate de tener MONGO_URI en tu config.py y .env
    mongo_db_name = Settings.MONGO_DB  # Asegúrate de tener MONGO_DB en tu config.py y .env

    if not mongo_uri:
        raise ValueError("MONGO_URI no está configurada en las variables de entorno.")
    if not mongo_db_name:
        raise ValueError("MONGO_DB no está configurada en las variables de entorno.")

    client = AsyncIOMotorClient(mongo_uri)
    database = client[mongo_db_name]

    # Lista de todos tus modelos de Beanie que quieres inicializar
    # Por ahora, la dejaremos vacía hasta que crees tus modelos.
    # Ejemplo: document_models = [UserActivityLog, MLExperiment]
    document_models = [
        # Añade tus modelos de Beanie aquí a medida que los crees
        # Ejemplo: UserActivityLog,
        #          MLExperiment,
    ]

    await init_beanie(
        database=database,
        document_models=document_models
    )
    print(f"MongoDB (Beanie) inicializado y conectado a la base de datos: {mongo_db_name}")

    # Opcional: Puedes devolver el cliente o la base de datos si necesitas usarlos directamente en otro lugar
    # return client, database
