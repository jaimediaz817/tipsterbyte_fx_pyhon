from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base
from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun


class Process(Base):
    """Modelo que representa un proceso o tarea programada en el sistema."""

    __tablename__ = "process"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    # Relación inversa a DetalleFuenteExtraccion
    detalles_fuente_extraccion = relationship(
        "DetalleFuenteExtraccion", back_populates="process"
    )

    # Existing relationships:
    process_runs = relationship("ProcessRun", back_populates="process")
