"""
Configuración de semáforos diferenciados por tipo de robot.

Este módulo permite configurar la concurrencia máxima por tipo de robot,
habilitando rate limiting y priorización diferenciada.
"""

from typing import Dict
from apps.leagues_manager.domain.enums.robot_type_enum import RobotTypeEnum


# ===================================================================
# CONFIGURACIÓN DE SEMÁFOROS POR TIPO DE ROBOT
# ===================================================================

# Configuración por defecto (puede ser sobrescrita por variables de entorno)
DEFAULT_SEMAPHORE_CONFIG: Dict[RobotTypeEnum, int] = {
    RobotTypeEnum.STANDINGS: 3,  # Rápido (1.5s) - más concurrencia
    RobotTypeEnum.ODDS_WPLAY: 1,  # Lento (10s) - rate limit
    RobotTypeEnum.CALENDAR: 2,  # Medio (2s) - concurrencia media
}

# Concurrencia global por defecto (fallback)
DEFAULT_GLOBAL_CONCURRENCY = 3


def get_semaphore_config() -> Dict[RobotTypeEnum, int]:
    """
    Retorna la configuración de semáforos por tipo de robot.

    Returns:
        Dict[RobotTypeEnum, int]: Mapeo de tipo de robot a concurrencia máxima
    """
    return DEFAULT_SEMAPHORE_CONFIG.copy()


def get_global_concurrency() -> int:
    """
    Retorna la concurrencia global por defecto.

    Returns:
        int: Número máximo de ejecuciones concurrentes globales
    """
    return DEFAULT_GLOBAL_CONCURRENCY


def get_concurrency_for_robot_type(robot_type: RobotTypeEnum) -> int:
    """
    Retorna la concurrencia máxima para un tipo de robot específico.

    Args:
        robot_type: Tipo de robot (RobotTypeEnum)

    Returns:
        int: Número máximo de ejecuciones concurrentes para este tipo
    """
    config = get_semaphore_config()
    return config.get(robot_type, get_global_concurrency())
