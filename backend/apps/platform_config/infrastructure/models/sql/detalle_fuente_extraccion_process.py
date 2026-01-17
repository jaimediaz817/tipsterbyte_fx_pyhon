from sqlalchemy import Column, ForeignKey, Integer, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class DetalleFuenteExtraccionProcess(Base):
    """ Modelo de base de datos para los procesos asociados a las fuentes de extracción. """
    __tablename__ = "detalle_fuente_extraccion_processes"

    id = Column(Integer, primary_key=True)
    # La FK debe apuntar a 'detalle_fuente_extraccion.id'.
    detalle_fuente_id = Column(Integer, ForeignKey("detalle_fuente_extraccion.id"), nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- RELACIONES NUEVAS ---
    detalle_fuente = relationship("DetalleFuenteExtraccion", back_populates="fuente_processes")
    process = relationship("Process", back_populates="fuente_processes")