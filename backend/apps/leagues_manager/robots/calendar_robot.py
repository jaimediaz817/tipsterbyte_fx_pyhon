from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.application.robot_registry import register_robot
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from loguru import logger
import asyncio


@register_robot(RobotTypeEnum.CALENDAR)
class CalendarRobot(BaseRobot):
    async def _execute_scraping(self):
        logger.trace(f"      -> {self.robot_id} extrayendo calendario...")
        await asyncio.sleep(2)  # Simula petición y parsing de calendario
        logger.info("<<<<<<<<<<<< FIN ROBOT CALENDAR >>>>>>>>>>>>>")
