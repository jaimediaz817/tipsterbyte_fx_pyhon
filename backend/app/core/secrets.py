from cryptography.fernet import Fernet
from pathlib import Path
from loguru import logger

# Ruta absoluta al archivo .fernet.key (raíz del backend)
FERNET_SECRET_FILE = Path(__file__).resolve().parent.parent / ".fernet.key"

_fernet_instance: Fernet | None = None

def generate_key():
    """Genera una nueva clave y la guarda en un archivo .fernet.key"""
    key = Fernet.generate_key()
    with open(FERNET_SECRET_FILE, "wb") as f:
        f.write(key)
    logger.info("🔐 Clave generada y guardada en .fernet.key")


def load_key() -> bytes:
    """Carga la clave desde el archivo .fernet.key"""
    if not FERNET_SECRET_FILE.exists():
        raise FileNotFoundError("⚠️ Archivo .fernet.key no encontrado. Ejecuta generate_key() primero.")
    with open(FERNET_SECRET_FILE, "rb") as f:
        return f.read()

# Crear instancia única de Fernet
def get_fernet() -> Fernet:
    global _fernet_instance
    if _fernet_instance is None:
        _fernet_instance = Fernet(load_key())
    return _fernet_instance


def encrypt(value: str) -> str:
    """Cifra un valor usando Fernet"""
    return get_fernet().encrypt(value.encode()).decode()


def decrypt(token: str) -> str:
    """Descifra un valor usando Fernet"""
    return get_fernet().decrypt(token.encode()).decode()
