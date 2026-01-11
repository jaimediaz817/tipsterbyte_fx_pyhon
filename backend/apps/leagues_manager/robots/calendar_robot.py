from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from loguru import logger
import asyncio

class CalendarRobot(BaseRobot):
    async def _execute_scraping(self):
        logger.trace(f"      -> {self.robot_id} extrayendo calendario...")
        await asyncio.sleep(2) # Simula petición y parsing de calendario