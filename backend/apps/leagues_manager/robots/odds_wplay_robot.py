from apps.leagues_manager.domain.robots.base_robot import BaseRobot
from apps.leagues_manager.application.robot_registry import register_robot
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from loguru import logger
import asyncio


@register_robot(RobotTypeEnum.ODDS_WPLAY)
class OddsWPlayRobot(BaseRobot):
    async def _execute_scraping(self):
        logger.trace(f"      -> {self.robot_id} extrayendo cuotas de WPlay...")
        await asyncio.sleep(1)  # Simula petición y parsing de cuotas
        logger.debug(
            f"      -> {self.robot_id} Cuotas extraídas: {{'TeamA': 1.8, 'TeamB': 2.0, 'Draw': 3.5}}"
        )
        logger.info("<<<<<<<<<<<< FIN ROBOTODDEWPLAY >>>>>>>>>>>>>")
