from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.db.sql.base_class import Base


# Bitácora de ejecuciones
class ProcessRun(Base):
    __tablename__ = "process_runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, nullable=False, unique=True)
    # TODO: tb-hu-auth-01-users-or-clients: pendiente definir si es user_id o client_id
    # client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    status = Column(String, default="in_progress")  # success, failed, etc.
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
