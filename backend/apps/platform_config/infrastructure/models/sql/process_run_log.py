
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from core.db.sql.base_class import Base
from sqlalchemy.orm import relationship

# Log detallado por paso del proceso
class ProcessRunLog(Base):
    __tablename__ = "process_run_logs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, ForeignKey("process_runs.run_id"), nullable=False)
    # TODO: refactor aplicado: tb-hu-auth-01-users-or-clients-or-source
    detalle_fuente_extraccion_id = Column(Integer)
    step = Column(String)
    level = Column(String)  # info, error, warning, debug
    message = Column(String)
    input = Column(Text, nullable=True)   # ← o usar JSON si se usa PostgreSQL
    output = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())

    # --- RELACIÓN NUEVA ---
    # Un 'ProcessRunLog' pertenece a un único 'ProcessRun'.
    # 'back_populates' le dice a SQLAlchemy que esta relación es el otro lado de 'logs' en el modelo ProcessRun.
    process_run = relationship("ProcessRun", back_populates="logs")