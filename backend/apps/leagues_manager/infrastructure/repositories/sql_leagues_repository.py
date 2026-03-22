from sqlalchemy.orm import Session

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
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.fuente_extraccion import (
    FuenteExtraccion,
)
from apps.leagues_manager.infrastructure.models.sql.pais import Pais as PaisModel
from apps.leagues_manager.infrastructure.models.sql.liga import Liga as LigaModel
from apps.leagues_manager.infrastructure.models.sql.torneo import Torneo as TorneoModel
from shared.utils.db.sql.sqlalchemy_utils import update_from_dict


class SQLLeaguesRepository(ILeaguesRepository):
    def __init__(self, db: Session):
        self.db = db

    # --- mappers ---
    def _to_continente(self, continente_model: Continente | None) -> Continente | None:
        if not continente_model:
            return None
        return Continente(
            id=getattr(continente_model, "id", 0),
            nombre=getattr(continente_model, "nombre", "") or "",
            codigo=getattr(continente_model, "codigo", None),
        )

    def _to_pais(self, pais_model: PaisModel) -> Pais:
        return Pais(
            id=(
                getattr(pais_model, "id", 0)
                if getattr(pais_model, "id", None) is not None
                else 0
            ),
            nombre=getattr(pais_model, "nombre", "") or "",
            continente_id=(
                getattr(pais_model, "continente_id", 0)
                if getattr(pais_model, "continente_id", None) is not None
                else 0
            ),
            codigo_iso=getattr(pais_model, "codigo_iso", None),
        )

    def _to_liga(self, liga_model: LigaModel) -> Liga:
        from apps.leagues_manager.domain.entities.liga import CategoriaLigaEnum

        nombre_categoria_value = getattr(liga_model, "nombre_categoria", None)
        if nombre_categoria_value is not None and nombre_categoria_value != "":
            try:
                nombre_categoria_enum = CategoriaLigaEnum(nombre_categoria_value)
            except ValueError:
                nombre_categoria_enum = None
        else:
            nombre_categoria_enum = None

        return Liga(
            id=(
                getattr(liga_model, "id", 0)
                if getattr(liga_model, "id", None) is not None
                else 0
            ),
            nombre=getattr(liga_model, "nombre", "") or "",
            pais_id=(
                getattr(liga_model, "pais_id", 0)
                if getattr(liga_model, "pais_id", None) is not None
                else 0
            ),
            nombre_categoria=nombre_categoria_enum,
        )

    def _to_torneo(self, torneo_model: TorneoModel) -> Torneo:
        return Torneo(
            id=(
                getattr(torneo_model, "id", 0)
                if getattr(torneo_model, "id", None) is not None
                else 0
            ),
            nombre=getattr(torneo_model, "nombre", "") or "",
            liga_id=(
                getattr(torneo_model, "liga_id", 0)
                if getattr(torneo_model, "liga_id", None) is not None
                else 0
            ),
            fecha_inicio=getattr(torneo_model, "fecha_inicio", None),
            fecha_fin=getattr(torneo_model, "fecha_fin", None),
        )

    # --- Mappers para FuenteExtraccion y DetalleFuenteExtraccion (¡NUEVOS!) ---
    def _to_fuente_extraccion(
        self, m: FuenteExtraccion | None
    ) -> FuenteExtraccion | None:
        if not m:
            return None
        return FuenteExtraccion(
            id=m.id,
            name=m.name,
            type=m.type,  # El Enum ya se maneja aquí gracias a SQLAlchemy
            descripcion=m.descripcion,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    def _to_detalle_fuente_extraccion(
        self, m: DetalleFuenteExtraccion | None
    ) -> DetalleFuenteExtraccion | None:
        if not m:
            return None
        return DetalleFuenteExtraccion(
            id=m.id,
            torneo_id=m.torneo_id,
            fuente_id=m.fuente_id,
            url=m.url,
            is_active=m.is_active,
            process_id=m.process_id,  # Mapeo del nuevo campo
            created_at=m.created_at,
            updated_at=m.updated_at,
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

    # --- FuenteExtraccion (¡NUEVO!) ---
    def get_fuente_extraccion_by_name(self, name: str) -> FuenteExtraccion | None:
        m = (
            self.db.query(FuenteExtraccion)
            .filter(FuenteExtraccion.name == name)
            .first()
        )
        return self._to_fuente_extraccion(m)

    def create_fuente_extraccion(
        self, name: str, type: str, descripcion: str | None, is_active: bool
    ) -> FuenteExtraccion:
        m = FuenteExtraccion(
            name=name, type=type, descripcion=descripcion, is_active=is_active
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_fuente_extraccion(m)

    def update_fuente_extraccion(self, fuente_id: int, data: dict) -> FuenteExtraccion:
        obj = (
            self.db.query(FuenteExtraccion)
            .filter(FuenteExtraccion.id == fuente_id)
            .first()
        )
        if not obj:
            raise ValueError(f"FuenteExtraccion con ID {fuente_id} no encontrada")
        update_from_dict(obj, data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_fuente_extraccion(obj)

    # --- DetalleFuenteExtraccion (¡NUEVO!) ---
    def get_detalle_fuente_extraccion_by_torneo_and_fuente(
        self, torneo_id: int, fuente_id: int
    ) -> DetalleFuenteExtraccion | None:
        m = (
            self.db.query(DetalleFuenteExtraccion)
            .filter(
                DetalleFuenteExtraccion.torneo_id == torneo_id,
                DetalleFuenteExtraccion.fuente_id == fuente_id,
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
        process_id: int,  # ¡Nuevo parámetro!
    ) -> DetalleFuenteExtraccion:
        m = DetalleFuenteExtraccion(
            torneo_id=torneo_id,
            fuente_id=fuente_id,
            url=url,
            is_active=is_active,
            process_id=process_id,  # Asignación del nuevo campo
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._to_detalle_fuente_extraccion(m)

    def update_detalle_fuente_extraccion(
        self, detalle_id: int, data: dict
    ) -> DetalleFuenteExtraccion:
        obj = (
            self.db.query(DetalleFuenteExtraccion)
            .filter(DetalleFuenteExtraccion.id == detalle_id)
            .first()
        )
        if not obj:
            raise ValueError(
                f"DetalleFuenteExtraccion con ID {detalle_id} no encontrado"
            )
        update_from_dict(obj, data)
        if "process_id" in data:  # Aseguramos que se actualice si se pasa
            obj.process_id = data["process_id"]
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return self._to_detalle_fuente_extraccion(obj)
