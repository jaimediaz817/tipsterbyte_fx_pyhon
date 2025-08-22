
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from core.db.sql.base_class import Base


# Log detallado por paso del proceso
class ProcessRunLog(Base):
    __tablename__ = "process_run_logs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, ForeignKey("process_runs.run_id"), nullable=False)
    client_id = Column(Integer)
    step = Column(String)
    level = Column(String)  # info, error, warning, debug
    message = Column(String)
    input = Column(Text, nullable=True)   # ← o usar JSON si se usa PostgreSQL
    output = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())
