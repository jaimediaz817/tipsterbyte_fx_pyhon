from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from loguru import logger
import asyncio

class StandingsRobot(BaseRobot):
    async def _execute_scraping(self):
        logger.trace(f"      -> {self.robot_id} extrayendo tablas de posiciones...")
        await asyncio.sleep(1.5) # Simula petición y parsing de tablas