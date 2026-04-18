from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from loguru import logger


class BaseSeeder(ABC):
    """
    Clase base abstracta para todos los seeders.
    Define el contrato que cada seeder específico debe seguir.
    """

    def __init__(self, db: Session):
        # ✅ Validacion compatible con Tests: Permite Mock objetos en entorno de prueba
        # Solo validamos estrictamente el tipo si NO es un Mock
        tipo_valido = isinstance(db, Session)
        es_mock = hasattr(db, "mock_calls") or db.__class__.__name__ in (
            "Mock",
            "MagicMock",
            "AsyncMock",
        )

        if not tipo_valido and not es_mock:
            raise TypeError("El seeder debe recibir una sesión de SQLAlchemy válida.")

        self.db = db
        self.logger = logger

    @abstractmethod
    def run(self, update: bool = False):
        """
        El método principal que ejecuta la lógica de poblado de datos.
        Este método DEBE ser implementado por cada clase hija.
        """
        pass
