from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.db.models.models import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def create(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role
