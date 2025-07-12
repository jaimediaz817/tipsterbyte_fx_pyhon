from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.db.init_db import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    users = relationship("User", secondary="user_roles", back_populates="roles")