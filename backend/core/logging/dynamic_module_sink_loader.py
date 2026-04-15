from pathlib import Path
from core.paths import BACKEND_ROOT, LOGS_ROOT
from core.logging.format_provider import file_format
from core.logging.sink_manager import safe_add_sink


def create_module_filter(name: str):
    def _f(record):
        n = record["name"]
        return (
            n.startswith(f"apps.{name}")
            and ".robots." not in n
            and not n.endswith(".robots")
        )

    return _f


def scan_and_load():
    """Escanea directorio apps y crea sinks dinamicos por modulo."""
    apps_dir = BACKEND_ROOT / "apps"
    if apps_dir.exists():
        for module_path in apps_dir.iterdir():
            if module_path.is_dir() and (module_path / "__init__.py").exists():
                module_name = module_path.name

                safe_add_sink(
                    sink_path=LOGS_ROOT / f"{module_name}.log",
                    level="INFO",
                    format=file_format,
                    filter=create_module_filter(module_name),
                    rotation="10 MB",
                    retention="10 days",
                    compression="zip",
                    enqueue=True,
                    backtrace=True,
                    diagnose=True,
                    delay=True,
                    mode="a",
                    catch=True,
                )
