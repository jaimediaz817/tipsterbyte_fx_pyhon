from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class Torneo(Base):
    __tablename__ = "torneo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    liga_id = Column(Integer, ForeignKey("liga.id", ondelete="RESTRICT"), nullable=False)
    nombre = Column(String(150), nullable=False)  # Apertura 2026, Clausura 2026, etc.
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    liga = relationship("Liga", back_populates="torneos")
    detalles_fuente = relationship("DetalleFuenteExtraccion", back_populates="torneo", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("liga_id", "nombre", name="uq_torneo_liga_nombre"),
    )