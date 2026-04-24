from pathlib import Path
from loguru import logger


def safe_add_sink(sink_path: Path, **kwargs):
    """
    Agrega un sink de Loguru de manera segura, deshabilitando rotación si hay errores.
    """
    # ✅ SOLUCION BUG LOGURU: Crear directorio padre ANTES de agregar el sink
    # Loguru NO crea directorios anidados automaticamente
    sink_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Intentar agregar con rotación
        logger.add(sink=sink_path, **kwargs)
    except Exception as e:
        # Si hay error, intentar sin rotación
        logger.warning(f"⚠️ Error al configurar rotación para {sink_path.name}: {e}")
        logger.info(f"🔄 Deshabilitando rotación para {sink_path.name}")

        # Remover parámetros de rotación
        safe_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["rotation", "retention", "compression"]
        }

        try:
            logger.add(sink=sink_path, **safe_kwargs)
            logger.info(f"✅ Sink {sink_path.name} configurado sin rotación")
        except Exception as e2:
            logger.error(f"❌ Error crítico al configurar sink {sink_path.name}: {e2}")
