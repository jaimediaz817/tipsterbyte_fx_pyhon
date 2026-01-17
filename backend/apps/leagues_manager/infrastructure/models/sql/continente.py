from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base

class Continente(Base):
    __tablename__ = "continente"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True)
    codigo = Column(String(10), nullable=True, unique=True)
    paises = relationship("Pais", back_populates="continente", cascade="all, delete-orphan")