from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class Process(Base):
    """ Modelo de base de datos para los procesos programados. """
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # --- RELACIONES NUEVAS ---
    # Un proceso tiene muchas ejecuciones (runs)
    runs = relationship("ProcessRun", back_populates="process", cascade="all, delete-orphan")
    # Un proceso está vinculado a muchos detalles de fuente a través de la tabla pivote
    fuente_processes = relationship("DetalleFuenteExtraccionProcess", back_populates="process")