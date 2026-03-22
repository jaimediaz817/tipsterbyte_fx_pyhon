"""
Registro automático de robots usando decoradores.

Este módulo permite registrar robots automáticamente sin necesidad
de modificar el factory manualmente cada vez que se agrega un nuevo robot.

Uso:
    from apps.leagues_manager.application.robot_registry import register_robot
    from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum

    @register_robot(RobotTypeEnum.STANDINGS)
    class StandingsRobot(BaseRobot):
        ...
"""

from typing import Dict, Type
from loguru import logger
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum
from apps.leagues_manager.domain.robots.base_robot import BaseRobot

# Registro global de robots: {RobotTypeEnum: RobotClass}
_robot_registry: Dict[RobotTypeEnum, Type[BaseRobot]] = {}


def register_robot(robot_type: RobotTypeEnum):
    """
    Decorador para registrar robots automáticamente.

    Uso:
        @register_robot(RobotTypeEnum.STANDINGS)
        class StandingsRobot(BaseRobot):
            ...

    El robot se registra automáticamente al importar el módulo.
    """

    def decorator(robot_class: Type[BaseRobot]) -> Type[BaseRobot]:
        if robot_type in _robot_registry:
            logger.warning(
                f"⚠️ Robot '{robot_type.value}' ya registrado. Sobreescribiendo..."
            )
        _robot_registry[robot_type] = robot_class
        logger.trace(
            f"✅ Robot '{robot_type.value}' registrado: {robot_class.__name__}"
        )
        return robot_class

    return decorator


def get_registered_robots() -> Dict[RobotTypeEnum, Type[BaseRobot]]:
    """Retorna todos los robots registrados."""
    return _robot_registry.copy()
