from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.models import AccessLog

class AccessLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: AccessLog) -> AccessLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log
