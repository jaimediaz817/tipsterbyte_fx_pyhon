# app/core/db.py
import os
# from dotenv import load_dotenv
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
# from motor.motor_asyncio import AsyncIOMotorClient
# from beanie import init_beanie
# import app.models.mongo_models as mongo_models

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.config import settings

# ORM base class
Base = declarative_base()

# Motor de base de datos (PostgreSQL en este caso)
# engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# TODO: deprecado en este archivo
# MongoDB - Beanie
MONGO_URI = os.getenv("MONGO_URI")
# mongo_client = AsyncIOMotorClient(MONGO_URI)

# async def init_mongo():
#     await init_beanie(database=mongo_client[os.getenv("MONGO_DB")], document_models=[mongo_models.SomeModel])
