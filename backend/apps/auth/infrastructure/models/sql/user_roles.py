from sqlalchemy import Column, Integer, ForeignKey
from core.db.base_class import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
    # Puedes agregar más columnas aquí si lo necesitas


# from sqlalchemy import Table, Column, Integer, ForeignKey
# from backend.db.sql_init_db import Base

# user_roles = Table(
#     "user_roles",
#     Base.metadata,
#     Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
#     Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True)
# )