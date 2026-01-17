from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class FuenteExtraccion(Base):
    __tablename__ = "fuente_extraccion"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # "standings", "odds_wplay", "calendar", etc.
    descripcion = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    detalles = relationship("DetalleFuenteExtraccion", back_populates="fuente")