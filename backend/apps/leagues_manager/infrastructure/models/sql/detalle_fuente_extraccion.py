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
from apps.platform_config.infrastructure.models.sql.process import Process


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

    # Campo para la relación con Process
    process_id = Column(
        Integer, ForeignKey("process.id", ondelete="RESTRICT"), nullable=False
    )

    # ✅ NUEVOS CAMPOS: Aislamiento Fuente de Extraccion
    provider_code = Column(String(100), nullable=True)
    base_url = Column(String(500), nullable=True)
    api_key = Column(String(255), nullable=True)
    rate_limit_per_minute = Column(Integer, nullable=True, default=60)
    priority = Column(Integer, nullable=True, default=1)
    adapter_class = Column(String(255), nullable=True)

    torneo = relationship("Torneo", back_populates="detalles_fuente")
    fuente = relationship("FuenteExtraccion", back_populates="detalles")
    process = relationship(
        "Process", back_populates="detalles_fuente_extraccion"
    )  # Relación ORM

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
