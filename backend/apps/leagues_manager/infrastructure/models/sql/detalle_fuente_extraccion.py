from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base
from .torneo import Torneo

class DetalleFuenteExtraccion(Base):
    __tablename__ = "detalle_fuente_extraccion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    torneo_id = Column(Integer, ForeignKey("torneo.id", ondelete="CASCADE"), nullable=False)
    fuente_id = Column(Integer, ForeignKey("fuente_extraccion.id", ondelete="RESTRICT"), nullable=False)
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    torneo = relationship("Torneo", back_populates="detalles_fuente")
    fuente = relationship("FuenteExtraccion", back_populates="detalles")

    # --- RELACIÓN NUEVA ---
    # Un detalle de fuente puede estar en varias tablas de procesos
    fuente_processes = relationship("DetalleFuenteExtraccionProcess", back_populates="detalle_fuente")

    __table_args__ = (
        UniqueConstraint("torneo_id", "fuente_id", name="uq_detalle_torneo_fuente"),
    )