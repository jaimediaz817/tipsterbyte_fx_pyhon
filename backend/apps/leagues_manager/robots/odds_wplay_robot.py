from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from loguru import logger
import asyncio

class OddsWPlayRobot(BaseRobot):
    async def _execute_scraping(self):
        logger.trace(f"      -> {self.robot_id} extrayendo cuotas de WPlay...")
        await asyncio.sleep(1) # Simula petición y parsing de cuotas