"""
Utilidades para logging mejorado de robots.

Proporciona helpers para logs más visuales y trazables en terminal,
sin complejidades innecesarias de JSON estructurado.
"""

from loguru import logger
from typing import Optional


# ===================================================================
# EMOJIS Y SÍMBOLOS PARA MEJORAR VISUALIZACIÓN EN TERMINAL
# ===================================================================


class LogSymbols:
    """Símbolos y emojis para logs más visuales en terminal."""

    # Estados
    START = "🚀"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    WAITING = "⏳"
    INFO = "ℹ️"

    # Tipos de robot
    ROBOT = "🤖"
    STANDINGS = "📊"
    ODDS = "🎲"
    CALENDAR = "📅"

    # Acciones
    SCRAPING = "🔍"
    SAVE = "💾"
    NETWORK = "🌐"
    PARSER = "📝"
    SEMAPHORE = "🚦"

    # Contexto
    RUN_ID = "🆔"
    TORNEO = "🏆"
    FUENTE = "📄"
    TIME = "⏱️"


def get_robot_emoji(robot_type: str) -> str:
    """
    Retorna el emoji apropiado según el tipo de robot.

    Args:
        robot_type: Tipo de robot (standings, odds_wplay, calendar, etc.)

    Returns:
        str: Emoji correspondiente al tipo de robot
    """
    robot_type_lower = robot_type.lower()

    if "standings" in robot_type_lower:
        return LogSymbols.STANDINGS
    elif "odds" in robot_type_lower:
        return LogSymbols.ODDS
    elif "calendar" in robot_type_lower:
        return LogSymbols.CALENDAR
    else:
        return LogSymbols.ROBOT


def format_run_context(run_id: str, robot_type: str, torneo_nombre: str) -> str:
    """
    Formatea el contexto de ejecución de manera visual y compacta.

    Args:
        run_id: ID único de la ejecución
        robot_type: Tipo de robot
        torneo_nombre: Nombre del torneo

    Returns:
        str: Contexto formateado para logs
    """
    emoji = get_robot_emoji(robot_type)
    # run_id corto (primeros 8 caracteres) para mejor legibilidad
    short_run_id = run_id[:8] if len(run_id) > 8 else run_id
    return f"{emoji} [{short_run_id}] {torneo_nombre}"


def log_robot_start(
    run_id: str,
    robot_type: str,
    robot_class_name: str,
    torneo_nombre: str,
    fuente_name: str,
    detalle_id: int,
    url: str,
):
    """
    Log estructurado de inicio de ejecución de robot.

    Args:
        run_id: ID único de la ejecución
        robot_type: Tipo de robot
        robot_class_name: Nombre de la clase del robot
        torneo_nombre: Nombre del torneo
        fuente_name: Nombre de la fuente
        detalle_id: ID del detalle de fuente
        url: URL a scrapear
    """
    emoji = get_robot_emoji(robot_type)
    short_run_id = run_id[:8]

    logger.info(
        f"\n"
        f"{'='*60}\n"
        f"{LogSymbols.START} INICIANDO ROBOT\n"
        f"{'='*60}\n"
        f"  {emoji} Robot: {robot_class_name}\n"
        f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
        f"  {LogSymbols.TORNEO} Torneo: {torneo_nombre}\n"
        f"  {LogSymbols.FUENTE} Fuente: {fuente_name}\n"
        f"  📋 Detalle ID: {detalle_id}\n"
        f"  {LogSymbols.NETWORK} URL: {url}\n"
        f"{'='*60}"
    )


def log_robot_end(
    run_id: str,
    robot_type: str,
    robot_class_name: str,
    torneo_nombre: str,
    success: bool = True,
    error: Optional[Exception] = None,
):
    """
    Log estructurado de fin de ejecución de robot.

    Args:
        run_id: ID único de la ejecución
        robot_type: Tipo de robot
        robot_class_name: Nombre de la clase del robot
        torneo_nombre: Nombre del torneo
        success: Si la ejecución fue exitosa
        error: Excepción si hubo error (opcional)
    """
    emoji = get_robot_emoji(robot_type)
    short_run_id = run_id[:8]
    status_emoji = LogSymbols.SUCCESS if success else LogSymbols.ERROR
    status_text = "COMPLETADO" if success else "FALLÓ"

    if success:
        logger.info(
            f"\n"
            f"{'='*60}\n"
            f"{status_emoji} ROBOT {status_text}\n"
            f"{'='*60}\n"
            f"  {emoji} Robot: {robot_class_name}\n"
            f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
            f"  {LogSymbols.TORNEO} Torneo: {torneo_nombre}\n"
            f"{'='*60}\n"
        )
    else:
        logger.error(
            f"\n"
            f"{'='*60}\n"
            f"{status_emoji} ROBOT {status_text}\n"
            f"{'='*60}\n"
            f"  {emoji} Robot: {robot_class_name}\n"
            f"  {LogSymbols.RUN_ID} Run ID: {short_run_id}...\n"
            f"  {LogSymbols.TORNEO} Torneo: {torneo_nombre}\n"
            f"  {LogSymbols.ERROR} Error: {error}\n"
            f"{'='*60}\n"
        )


def log_step(
    robot_id: str,
    run_id: str,
    step: str,
    message: str,
    level: str = "info",
):
    """
    Log de paso intermedio con contexto visual.

    Args:
        robot_id: Identificador del robot
        run_id: ID de ejecución
        step: Nombre del paso
        message: Mensaje descriptivo
        level: Nivel de log (info, warning, error, debug)
    """
    short_run_id = run_id[:8]
    log_message = f"  [{robot_id}] [{short_run_id}] [{step}] {message}"

    if level == "info":
        logger.info(log_message)
    elif level == "warning":
        logger.warning(log_message)
    elif level == "error":
        logger.error(log_message)
    else:
        logger.debug(log_message)


def log_semaphore_status(
    robot_type: str,
    concurrency: int,
    waiting: bool = False,
):
    """
    Log del estado del semáforo.

    Args:
        robot_type: Tipo de robot
        concurrency: Concurrencia máxima
        waiting: Si está esperando cupo
    """
    emoji = get_robot_emoji(robot_type)

    if waiting:
        logger.info(
            f"  {LogSymbols.WAITING} {emoji} Tipo '{robot_type}' esperando cupo "
            f"(concurrencia: {concurrency})"
        )
    else:
        logger.info(
            f"  {LogSymbols.SEMAPHORE} {emoji} Semáforo configurado para '{robot_type}': "
            f"{concurrency} concurrencia máxima"
        )
