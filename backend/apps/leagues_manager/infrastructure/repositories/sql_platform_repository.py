from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.liga import Liga
from sqlalchemy.orm import Session, joinedload

from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo


class SqlPlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_leagues_with_full_details(self):
        """
        Obtiene todas las ligas activas, con sus torneos activos,
        detalles de fuente de extracción activos y fuentes de extracción asociadas.
        La filtración por process_id se realizará en la lógica de la tarea.
        """
        query = (
            self.db.query(Liga)
            .filter(Liga.is_active == True)
            .options(
                joinedload(Liga.torneos)
                .joinedload(Torneo.detalles_fuente)
                .joinedload(DetalleFuenteExtraccion.fuente),
                joinedload(Liga.torneos)
                .joinedload(Torneo.detalles_fuente)
                .joinedload(DetalleFuenteExtraccion.process),
            )
        )
        # Usar distinct para evitar duplicados si hay múltiples detalles por un mismo torneo/liga
        return query.distinct(Liga.id).all()
