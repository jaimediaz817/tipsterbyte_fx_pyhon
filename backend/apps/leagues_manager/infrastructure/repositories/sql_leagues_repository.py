from __future__ import annotations
from typing import cast, TYPE_CHECKING
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from apps.leagues_manager.domain.entities.fuente_extraccion import FuenteExtraccion
    from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
        DetalleFuenteExtraccion,
    )

from apps.leagues_manager.domain.entities.continente import Continente
from apps.leagues_manager.domain.entities.liga import Liga
from apps.leagues_manager.domain.entities.pais import Pais
from apps.leagues_manager.domain.entities.torneo import Torneo
from apps.leagues_manager.domain.repositories.i_leagues_repository import (
    ILeaguesRepository,
)


from apps.leagues_manager.infrastructure.models.sql.continente import (
    Continente,
)
from apps.leagues_manager.infrastructure.models.sql.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion as DetalleFuenteExtraccionModel,
)
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion as FuenteExtraccionModel,
)
from apps.leagues_manager.infrastructure.models.sql.pais import Pais as PaisModel
from apps.leagues_manager.infrastructure.models.sql.liga import Liga as LigaModel
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo as TorneoModel
from apps.leagues_manager.infrastructure.mappers import (
    map_continente_from_model,
    map_pais_from_model,
    map_liga_from_model,
    map_torneo_from_model,
    map_fuente_extraccion_from_model,
    map_detalle_fuente_extraccion_from_model,
)
from shared.utils.db.sql.sqlalchemy_utils import update_from_dict


class SQLLeaguesRepository(ILeaguesRepository):
    def __init__(self, db: Session):
        self.db = db

    # --- [DEPRECADO] Mappers movidos a /mappers/ - mantener por retrocompatibilidad ---
    def _to_continente(self, continente_model: Continente | None) -> Continente | None:
        return map_continente_from_model(continente_model)

    def _to_pais(self, pais_model: PaisModel) -> Pais:
        return map_pais_from_model(pais_model)

    def _to_liga(self, liga_model: LigaModel) -> Liga:
        return map_liga_from_model(liga_model)

    def _to_torneo(self, torneo_model: TorneoModel) -> Torneo:
        return map_torneo_from_model(torneo_model)

    def _to_fuente_extraccion(
        self, fuente_model: FuenteExtraccionModel | None
    ) -> "FuenteExtraccion | None":
        return cast(FuenteExtraccion, map_fuente_extraccion_from_model(fuente_model))

    def _to_detalle_fuente_extraccion(
        self, detalle_model: DetalleFuenteExtraccionModel | None
    ) -> "DetalleFuenteExtraccion | None":
        return cast(
            DetalleFuenteExtraccion,
            map_detalle_fuente_extraccion_from_model(detalle_model),
        )

    # --- Continente ---
    def get_all_continentes(self) -> list[Continente]:
        ms = self.db.query(Continente).all()
        return [self._to_continente(m) for m in ms]

    def get_continente_by_nombre(self, nombre: str) -> Continente:
        m = self.db.query(Continente).filter(Continente.nombre == nombre).first()
        return self._to_continente(m) if m else None

    def create_continente(self, nombre: str, codigo: str | None) -> Continente:
        m = Continente(nombre=nombre, codigo=codigo)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_continente(m)

    def update_continente(self, continente_id: int, data: dict) -> Continente:
        obj = self.db.query(Continente).filter(Continente.id == continente_id).first()
        if not obj:
            raise ValueError("Continente no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        continente = self._to_continente(obj)
        if continente is None:
            raise ValueError("Error al convertir el continente")
        return continente

    # --- País ---
    def get_pais_by_nombre_and_continente(
        self, nombre: str, continente_id: int
    ) -> Pais | None:
        m = (
            self.db.query(PaisModel)
            .filter(
                PaisModel.nombre == nombre, PaisModel.continente_id == continente_id
            )
            .first()
        )
        return self._to_pais(m) if m else None

    def get_pais_by_nombre(self, nombre: str):
        m = self.db.query(PaisModel).filter(PaisModel.nombre == nombre).first()
        return self._to_pais(m) if m else None

    def create_pais(self, nombre: str, codigo_iso: str | None, continente_id: int):
        m = PaisModel(nombre=nombre, codigo_iso=codigo_iso, continente_id=continente_id)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_pais(m)

    def update_pais(self, pais_id: int, data: dict) -> Pais:
        obj = self.db.query(PaisModel).filter(PaisModel.id == pais_id).first()
        if not obj:
            raise ValueError("País no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_pais(obj)

    # --- Liga ---
    def get_liga_by_nombre_and_pais(self, nombre: str, pais_id: int) -> Liga | None:
        m = (
            self.db.query(LigaModel)
            .filter(LigaModel.nombre == nombre, LigaModel.pais_id == pais_id)
            .first()
        )
        return self._to_liga(m) if m else None

    def get_liga_by_nombre(self, nombre: str):
        m = self.db.query(LigaModel).filter(LigaModel.nombre == nombre).first()
        return self._to_liga(m) if m else None

    def create_liga(self, nombre: str, nombre_categoria: str | None, pais_id: int):
        m = LigaModel(nombre=nombre, nombre_categoria=nombre_categoria, pais_id=pais_id)
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_liga(m)

    def update_liga(self, liga_id: int, data: dict) -> Liga:
        obj = self.db.query(LigaModel).filter(LigaModel.id == liga_id).first()
        if not obj:
            raise ValueError("Liga no encontrada")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_liga(obj)

    # --- Torneo ---
    def get_torneo_by_nombre_and_liga(self, nombre: str, liga_id: int):
        m = (
            self.db.query(TorneoModel)
            .filter(TorneoModel.nombre == nombre, TorneoModel.liga_id == liga_id)
            .first()
        )
        return self._to_torneo(m) if m else None

    def create_torneo(
        self, nombre: str, liga_id: int, fecha_inicio=None, fecha_fin=None
    ):
        m = TorneoModel(
            nombre=nombre,
            liga_id=liga_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_torneo(m)

    def update_torneo(self, torneo_id: int, data: dict) -> Torneo:
        obj = self.db.query(TorneoModel).filter(TorneoModel.id == torneo_id).first()
        if not obj:
            raise ValueError("Torneo no encontrado")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_torneo(obj)

    # --- FuenteExtraccion ---
    def get_fuente_extraccion_by_name(self, name: str) -> "FuenteExtraccion | None":
        m = (
            self.db.query(FuenteExtraccionModel)
            .filter(FuenteExtraccionModel.name == name)
            .first()
        )
        return self._to_fuente_extraccion(m)

    def create_fuente_extraccion(
        self, name: str, type: str, descripcion: str | None, is_active: bool
    ) -> "FuenteExtraccion":
        m = FuenteExtraccionModel(
            name=name, type=type, descripcion=descripcion, is_active=is_active
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return cast(FuenteExtraccion, self._to_fuente_extraccion(m))

    def update_fuente_extraccion(
        self, fuente_id: int, data: dict
    ) -> "FuenteExtraccion":
        obj = (
            self.db.query(FuenteExtraccionModel)
            .filter(FuenteExtraccionModel.id == fuente_id)
            .first()
        )
        if not obj:
            raise ValueError(f"FuenteExtraccion con ID {fuente_id} no encontrada")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return cast(FuenteExtraccion, self._to_fuente_extraccion(obj))

    # --- DetalleFuenteExtraccion ---
    def get_detalle_fuente_extraccion_by_torneo_and_fuente(
        self, torneo_id: int, fuente_id: int
    ) -> "DetalleFuenteExtraccion | None":
        m = (
            self.db.query(DetalleFuenteExtraccionModel)
            .filter(
                DetalleFuenteExtraccionModel.torneo_id == torneo_id,
                DetalleFuenteExtraccionModel.fuente_id == fuente_id,
            )
            .first()
        )
        return self._to_detalle_fuente_extraccion(m)

    def create_detalle_fuente_extraccion(
        self,
        torneo_id: int,
        fuente_id: int,
        url: str,
        is_active: bool,
        process_id: int,
    ) -> "DetalleFuenteExtraccion":
        m = DetalleFuenteExtraccionModel(
            torneo_id=torneo_id,
            fuente_id=fuente_id,
            url=url,
            is_active=is_active,
            process_id=process_id,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return cast(DetalleFuenteExtraccion, self._to_detalle_fuente_extraccion(m))

    def update_detalle_fuente_extraccion(
        self, detalle_id: int, data: dict
    ) -> "DetalleFuenteExtraccion":
        obj = (
            self.db.query(DetalleFuenteExtraccionModel)
            .filter(DetalleFuenteExtraccionModel.id == detalle_id)
            .first()
        )
        if not obj:
            raise ValueError(
                f"DetalleFuenteExtraccion con ID {detalle_id} no encontrado"
            )
        update_from_dict(obj, data)
        if "process_id" in data:
            obj.process_id = data["process_id"]
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return cast(DetalleFuenteExtraccion, self._to_detalle_fuente_extraccion(obj))

    # --- Métodos para LigasSeeder ---

    def get_all_paises(self) -> list[Pais]:
        """Obtiene todos los países."""
        ms = self.db.query(PaisModel).all()
        return [self._to_pais(m) for m in ms]

    def get_all_ligas(self) -> list[Liga]:
        """Obtiene todas las ligas."""
        ms = self.db.query(LigaModel).all()
        return [self._to_liga(m) for m in ms]

    def update_liga_api_fields(
        self,
        liga_id: int,
        id_api_externa: int | None,
        logo_url: str | None,
        tipo_liga: str | None,
    ) -> Liga:
        """Actualiza los campos de API-Football de una liga."""
        obj = self.db.query(LigaModel).filter(LigaModel.id == liga_id).first()
        if not obj:
            raise ValueError(f"Liga con ID {liga_id} no encontrada")

        # Pylance confunde LigaModel con Liga (entidad de dominio)
        # Usamos setattr para evitar el error de tipos
        setattr(obj, "id_api_externa", id_api_externa)
        setattr(obj, "logo_url", logo_url)
        setattr(obj, "tipo_liga", tipo_liga)

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_liga(obj)
