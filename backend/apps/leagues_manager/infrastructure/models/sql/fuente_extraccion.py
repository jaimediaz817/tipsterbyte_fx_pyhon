from sqlalchemy import Column, DateTime, Enum, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from core.db.sql.base_class import Base


class FuenteExtraccion(Base):
    __tablename__ = "fuente_extraccion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    type = Column(
        Enum(
            RobotTypeEnum, name="robot_type_enum", create_type=True
        ),  # <--- ¡CAMBIO CLAVE AQUÍ!
        nullable=False,
    )
    # "standings", "odds_wplay", "calendar", etc.
    descripcion = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
        nullable=False,
    )

    detalles = relationship("DetalleFuenteExtraccion", back_populates="fuente")
