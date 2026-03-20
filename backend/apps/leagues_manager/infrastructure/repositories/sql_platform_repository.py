from apps.leagues_manager.infrastructure.models.sql.liga import Liga
from sqlalchemy.orm import Session, joinedload


class SqlPlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_leagues_with_full_details(self):
        # Carga ligas, torneos y detalles de fuente con join
        return (
            self.db.query(Liga)
            .filter(Liga.is_active == True)
            .options(
                # Eager load torneos y detalles_fuente
                # (ajusta los nombres según tus relaciones)
                joinedload(Liga.torneos)
                .joinedload(Liga.torneos.property.mapper.class_.detalles_fuente)
                .joinedload(
                    Liga.torneos.property.mapper.class_.detalles_fuente.property.mapper.class_.fuente
                )
            )
            .all()
        )
