"""
Módulo de Logging - Sistema de Perfiles de Log
================================================

Este módulo implementa un sistema de logging basado en perfiles (Strategy Pattern)
que permite:
- Definir categorías de logs de forma declarativa
- Configurar filtrado, rotación y retención por perfil
- Facilitar la extensión sin modificar código existente
- Mejorar la mantenibilidad del sistema de logging

Uso:
    from core.logging import LOG_PROFILES, configure_logging

    # Configurar logging
    configure_logging()

    # Acceder a perfiles individuales
    system_profile = LOG_PROFILES["system"]
    print(system_profile.name)  # "system"
"""

from core.logging.log_profile import (
    LogProfile,
    SystemProfile,
    SchedulerProfile,
    RobotsProfile,
    GeneralProfile,
    LOG_PROFILES,
)

__all__ = [
    "LogProfile",
    "SystemProfile",
    "SchedulerProfile",
    "RobotsProfile",
    "GeneralProfile",
    "LOG_PROFILES",
]
