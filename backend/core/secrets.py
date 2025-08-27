from cryptography.fernet import Fernet
from pathlib import Path
from loguru import logger
import os
from core.paths import CORE_ROOT

# La ruta donde se guarda la clave. Si decides moverla a la raíz, cambia esta línea.
# FERNET_SECRET_FILE = Path(__file__).resolve().parent / ".fernet.key"
FERNET_SECRET_FILE = CORE_ROOT / ".fernet.key"

# Priorizamos la variable de entorno si existe, ideal para producción.
FERNET_ENV_KEY = os.getenv("FERNET_KEY")

print(f"DEBUG: >>>>>>>> FERNET_ENV_KEY = {FERNET_ENV_KEY}")


_fernet_instance: Fernet | None = None

def generate_key(force: bool = False):
    """
    Genera una nueva clave Fernet.
    - Si force=False y la clave ya existe, no hace nada.
    - Si force=True, sobrescribe la clave existente (rotación).
    """
    if FERNET_ENV_KEY:
        logger.warning("⚠️  Variable de entorno FERNET_KEY detectada. Se ignora la escritura de archivo.")
        return

    if FERNET_SECRET_FILE.exists() and not force:
        logger.info(f"🔐 Clave ya existe en {FERNET_SECRET_FILE}. Usa --force para rotarla.")
        return

    key = Fernet.generate_key()
    FERNET_SECRET_FILE.write_bytes(key)
    action = "rotada" if force else "generada"
    logger.success(f"✅ Clave {action} y guardada exitosamente en: {FERNET_SECRET_FILE}")

def load_key() -> bytes:
    """Carga la clave desde la variable de entorno o desde el archivo .fernet.key."""
    if FERNET_ENV_KEY:
        return FERNET_ENV_KEY.encode()
    
    if not FERNET_SECRET_FILE.exists():
        raise FileNotFoundError("⚠️ Archivo .fernet.key no encontrado. Ejecuta: python manage.py secrets generate")
    return FERNET_SECRET_FILE.read_bytes()

def key_exists() -> bool:
    """Verifica si la clave existe, ya sea en el entorno o en un archivo."""
    return bool(FERNET_ENV_KEY) or FERNET_SECRET_FILE.exists()

def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(load_key())
    return _fernet_instance

def encrypt(value: str) -> str:
    """Cifra un valor usando Fernet."""
    return get_fernet().encrypt(value.encode()).decode()

def decrypt(token: str) -> str:
    """Descifra un valor usando Fernet."""
    return get_fernet().decrypt(token.encode()).decode()