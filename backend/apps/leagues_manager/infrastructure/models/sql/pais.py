from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class Pais(Base):
    __tablename__ = "pais"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    codigo_iso = Column(String(3), nullable=True, unique=True)
    continente_id = Column(Integer, ForeignKey("continente.id", ondelete="RESTRICT"), nullable=False)

    continente = relationship("Continente", back_populates="paises")
    ligas = relationship("Liga", back_populates="pais", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("nombre", "continente_id", name="uq_pais_nombre_continente"),
    )