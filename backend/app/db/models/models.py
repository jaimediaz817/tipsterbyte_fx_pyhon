from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey, Table, Boolean
)
from sqlalchemy.orm import relationship, declarative_base
from app.db.init_db import Base

# Base = declarative_base()

# Tabla intermedia para la relación muchos a muchos entre usuarios y roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    accesses = relationship("AccessLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    users = relationship("User", secondary=user_roles, back_populates="roles")

class AccessLog(Base):
    __tablename__ = "access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    accessed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accesses")
