"""
Script de monitoreo de logs de limpieza.
Monitorea en tiempo real cuando se ejecuta el job PROCESS_LOG_CLEANUP.
"""

import time
import re
from pathlib import Path
from datetime import datetime
from loguru import logger
import sys

# Agregar directorio backend al path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core.paths import LOGS_ROOT

# Configurar logger para este script
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
)

# Patrones a monitorear
PATTERNS = [
    r"Iniciando limpieza programada de logs",
    r"LIMPIEZA COMPLETADA",
    r"Limpieza completada:",
    r"Archivados: \d+",
    r"Eliminados: \d+",
    r"Espacio liberado: [\d.]+ MB",
    r"🧹",
    r"✅",
    r"ERROR.*limpieza",
]

# Colores para output
COLORS = {
    "INFO": "\033[94m",  # Azul
    "SUCCESS": "\033[92m",  # Verde
    "WARNING": "\033[93m",  # Amarillo
    "ERROR": "\033[91m",  # Rojo
    "RESET": "\033[0m",  # Reset
    "BOLD": "\033[1m",  # Bold
}


def print_banner():
    """Imprime banner de inicio."""
    print(f"\n{COLORS['BOLD']}{'='*80}")
    print(f"{COLORS['INFO']}🔍 MONITOR DE LOGS DE LIMPIEZA - PROCESS_LOG_CLEANUP")
    print(f"{COLORS['BOLD']}{'='*80}{COLORS['RESET']}")
    print(f"\n{COLORS['INFO']}Monitoreando logs en: {LOGS_ROOT}")
    print(f"{COLORS['INFO']}Buscando patrones de ejecución de limpieza...")
    print(f"{COLORS['INFO']}Presiona Ctrl+C para detener{COLORS['RESET']}\n")


def get_log_files():
    """Obtiene archivos de log relevantes."""
    log_files = []

    # Archivos de log principales
    main_logs = [
        LOGS_ROOT / "general_app.log",
        LOGS_ROOT / "system.log",
        LOGS_ROOT / "scheduler" / "scheduler.log",
    ]

    for log_file in main_logs:
        if log_file.exists():
            log_files.append(log_file)

    return log_files


def tail_file(file_path, last_position=0):
    """Lee nuevas líneas de un archivo desde la última posición."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            f.seek(last_position)
            lines = f.readlines()
            new_position = f.tell()
            return lines, new_position
    except Exception as e:
        logger.error(f"Error leyendo {file_path}: {e}")
        return [], last_position


def check_patterns(line):
    """Verifica si la línea contiene alguno de los patrones buscados."""
    matches = []
    for pattern in PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            matches.append(pattern)
    return matches


def format_notification(line, pattern):
    """Formatea la notificación según el patrón encontrado."""
    timestamp = datetime.now().strftime("%H:%M:%S")

    if "Iniciando limpieza" in pattern:
        return f"{COLORS['BOLD']}[{timestamp}] 🚀 INICIO DE LIMPIEZA DETECTADO{COLORS['RESET']}\n{line}"
    elif "LIMPIEZA COMPLETADA" in pattern or "Limpieza completada" in pattern:
        return f"{COLORS['SUCCESS']}[{timestamp}] ✅ LIMPIEZA COMPLETADA{COLORS['RESET']}\n{line}"
    elif "Archivados:" in pattern:
        return f"{COLORS['INFO']}[{timestamp}] 📦 {line.strip()}{COLORS['RESET']}"
    elif "Eliminados:" in pattern:
        return f"{COLORS['INFO']}[{timestamp}] 🗑️ {line.strip()}{COLORS['RESET']}"
    elif "Espacio liberado:" in pattern:
        return f"{COLORS['SUCCESS']}[{timestamp}] 💾 {line.strip()}{COLORS['RESET']}"
    elif "ERROR" in pattern:
        return f"{COLORS['ERROR']}[{timestamp}] ❌ ERROR DETECTADO{COLORS['RESET']}\n{line}"
    else:
        return f"{COLORS['INFO']}[{timestamp}] 📝 {line.strip()}{COLORS['RESET']}"


def monitor_logs():
    """Monitorea los logs en tiempo real."""
    print_banner()

    # Obtener archivos de log
    log_files = get_log_files()

    if not log_files:
        logger.warning("No se encontraron archivos de log para monitorear")
        logger.info(f"Directorio de logs: {LOGS_ROOT}")
        return

    logger.info(f"Monitoreando {len(log_files)} archivos de log:")
    for log_file in log_files:
        logger.info(f"  - {log_file.name}")

    print(f"\n{COLORS['BOLD']}{'='*80}{COLORS['RESET']}\n")

    # Posiciones actuales en cada archivo
    positions = {str(f): f.stat().st_size if f.exists() else 0 for f in log_files}

    # Contador de notificaciones
    notifications_count = 0
    last_cleanup_time = None

    try:
        while True:
            new_notifications = []

            for log_file in log_files:
                file_path = str(log_file)

                # Leer nuevas líneas
                new_lines, new_position = tail_file(log_file, positions[file_path])
                positions[file_path] = new_position

                # Verificar patrones en nuevas líneas
                for line in new_lines:
                    matches = check_patterns(line)
                    if matches:
                        for pattern in matches:
                            notification = format_notification(line, pattern)
                            new_notifications.append(notification)

                            # Actualizar tiempo de última limpieza
                            if (
                                "LIMPIEZA COMPLETADA" in pattern
                                or "Limpieza completada" in pattern
                            ):
                                last_cleanup_time = datetime.now()

            # Mostrar nuevas notificaciones
            for notification in new_notifications:
                print(notification)
                notifications_count += 1

            # Mostrar estado cada 30 segundos
            if int(time.time()) % 30 == 0:
                elapsed = ""
                if last_cleanup_time:
                    elapsed = f" (última limpieza hace {(datetime.now() - last_cleanup_time).seconds}s)"
                logger.info(
                    f"📊 Monitoreando... {notifications_count} notificaciones{elapsed}"
                )

            # Esperar un poco antes de la siguiente verificación
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{COLORS['BOLD']}{'='*80}")
        print(f"{COLORS['WARNING']}🛑 Monitoreo detenido por el usuario")
        print(f"{COLORS['INFO']}Total de notificaciones: {notifications_count}")
        if last_cleanup_time:
            print(
                f"{COLORS['INFO']}Última limpieza: {last_cleanup_time.strftime('%H:%M:%S')}"
            )
        print(f"{COLORS['BOLD']}{'='*80}{COLORS['RESET']}\n")


if __name__ == "__main__":
    monitor_logs()
