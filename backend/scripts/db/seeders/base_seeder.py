from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from loguru import logger

class BaseSeeder(ABC):
    """
    Clase base abstracta para todos los seeders.
    Define el contrato que cada seeder específico debe seguir.
    """
    def __init__(self, db: Session):
        if not isinstance(db, Session):
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