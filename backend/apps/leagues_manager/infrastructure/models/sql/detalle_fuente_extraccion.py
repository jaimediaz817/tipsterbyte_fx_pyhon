from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base
from .torneo import Torneo


class DetalleFuenteExtraccion(Base):
    __tablename__ = "detalle_fuente_extraccion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    torneo_id = Column(
        Integer, ForeignKey("torneo.id", ondelete="CASCADE"), nullable=False
    )
    fuente_id = Column(
        Integer, ForeignKey("fuente_extraccion.id", ondelete="RESTRICT"), nullable=False
    )
    url = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    torneo = relationship("Torneo", back_populates="detalles_fuente")
    fuente = relationship("FuenteExtraccion", back_populates="detalles")

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("torneo_id", "fuente_id", name="uq_detalle_torneo_fuente"),
    )
