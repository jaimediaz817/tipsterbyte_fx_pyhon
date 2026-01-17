from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class Liga(Base):
    __tablename__ = "liga"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    nombre_categoria = Column(String(10), nullable=True)  # A/B/C...
    pais_id = Column(Integer, ForeignKey("pais.id", ondelete="RESTRICT"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    pais = relationship("Pais", back_populates="ligas")
    torneos = relationship("Torneo", back_populates="liga", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("pais_id", "nombre", "nombre_categoria", name="uq_liga_nombre_categoria_pais"),
    )