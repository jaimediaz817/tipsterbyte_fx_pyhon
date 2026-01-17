# filepath: c:\Users\JaimeIvanDiazGaona\Documents\proyectos_jdiaz\tipsterByte_fx\backend\core\database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
 
from core.db.sql.init_sql_all_models import load_all_models
from core.config import settings
# Importa la Base fundamental
from core.db.sql.base_class import Base
# IMPORTANTE: Importa el archivo que registra todos los modelos.
# Aunque no se use directamente aquí, esta línea asegura que SQLAlchemy los conozca.
# import core.db.sql.init_sql_all_models

# ✅ Cargar todos los modelos SQL antes de crear engine/sesiones
load_all_models()

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def create_db_and_tables():
    """
    Crea todas las tablas en la base de datos.
    `Base.metadata` conoce todos los modelos gracias a la importación de `all_models`.
    """
    Base.metadata.create_all(bind=engine)