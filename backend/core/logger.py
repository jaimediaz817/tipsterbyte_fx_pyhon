from loguru import logger
import sys
from core.config import settings
from pathlib import Path

# Sube dos niveles para llegar a la raíz de 'backend' y luego crea la carpeta 'logs'
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def configure_logging():
    logger.remove()
    
    print(f"DEBUG:LOGGER >>>>>>>> Configurando logging. LOG_DIR: {Path(__file__).resolve().parent.parent}")

    # Consola
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        backtrace=True,
        diagnose=True
    )

    # Archivo general
    logger.add(
        LOG_DIR / "app.log",
        level=settings.LOG_LEVEL,
        rotation="10 MB",
        retention="10 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function} - {message}",
        compression="zip",
        enqueue=True
    )
