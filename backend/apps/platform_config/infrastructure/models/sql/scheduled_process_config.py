from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from core.db.sql.base_class import Base


class ScheduledProcessConfig(Base):
    __tablename__ = "scheduled_process_config"

    process_name = Column(String, primary_key=True)  # ejemplo: "cruce_cartera"
    cron_expression = Column(String, nullable=False)  # ejemplo: "0 1 * * *"
    enabled = Column(Boolean, default=False, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
