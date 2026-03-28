from sqlalchemy import (
    Column,
    Enum,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from apps.leagues_manager.domain.enums.categoria_liga_enum import CategoriaLigaEnum
from core.db.sql.base_class import Base


class Liga(Base):
    __tablename__ = "liga"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    nombre_categoria = Column(
        Enum(CategoriaLigaEnum, name="categoria_liga_enum", create_type=True),
        nullable=True,
    )
    pais_id = Column(
        Integer, ForeignKey("pais.id", ondelete="RESTRICT"), nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)

    # Campos nuevos para API-Football
    id_api_externa = Column(
        Integer, nullable=True, unique=True, comment="ID de la liga en API-Football"
    )
    logo_url = Column(String(500), nullable=True, comment="URL del logo de la liga")
    tipo_liga = Column(
        String(50), nullable=True, comment="Tipo de liga: 'League' o 'Cup'"
    )

    pais = relationship("Pais", back_populates="ligas")
    torneos = relationship(
        "Torneo", back_populates="liga", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "pais_id",
            "nombre",
            "nombre_categoria",
            name="uq_liga_nombre_categoria_pais",
        ),
    )
