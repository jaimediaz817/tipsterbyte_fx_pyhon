from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.db.sql.base_class import Base


# Bitácora de ejecuciones
class ProcessRun(Base):
    __tablename__ = "process_runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, nullable=False, unique=True)
    # TODO: tb-hu-auth-01-users-or-clients-or-source: pendiente definir si es user_id o client_id u otra fuente: detalle_fuente_extraccion_id
    # detalle_fuente_extraccion_id = Column(Integer, ForeignKey("detalle_fuente_extraccion.id"), nullable=False)
    
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    status = Column(String, default="in_progress")  # success, failed, etc.

    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    
    # --- RELACIÓN NUEVA ---
    process = relationship("Process", back_populates="runs")    
    # --- RELACIÓN NUEVA ---
    # Un 'ProcessRun' tiene muchos 'ProcessRunLog'.
    # 'back_populates' le dice a SQLAlchemy que esta relación es el otro lado de 'process_run' en el modelo ProcessRunLog.
    # 'cascade' asegura que si borras un ProcessRun, todos sus logs asociados se borren también.
    logs = relationship("ProcessRunLog", back_populates="process_run", cascade="all, delete-orphan")