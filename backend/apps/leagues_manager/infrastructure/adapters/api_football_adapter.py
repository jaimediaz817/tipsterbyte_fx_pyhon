from __future__ import annotations
from typing import Any, Dict, List
from loguru import logger
import httpx

from apps.leagues_manager.domain.entities.detalle_fuente_extraccion import (
    DetalleFuenteExtraccion,
)
from apps.leagues_manager.domain.interfaces.i_fuente_extraccion_adapter import (
    IFuenteExtraccionAdapter,
)


class ApiFootballAdapter(IFuenteExtraccionAdapter):
    """
    ✅ Adaptador para API Football
    Implementacion por defecto compatible con la version actual del sistema
    """

    def __init__(self, detalle_fuente: DetalleFuenteExtraccion):
        self.detalle_fuente = detalle_fuente
        self.base_url = (
            detalle_fuente.base_url or "https://api-football-v1.p.rapidapi.com/v3"
        )
        self.api_key = detalle_fuente.api_key or ""
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
        }

    async def obtener_ligas(self) -> List[Dict[str, Any]]:
        logger.debug(
            f"Obteniendo ligas desde ApiFootball para fuente {self.detalle_fuente.id}"
        )

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/leagues", headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])

    async def obtener_torneos(self, liga_externa_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"Obteniendo torneos liga {liga_externa_id}")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/leagues/seasons",
                headers=self.headers,
                params={"id": liga_externa_id},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])

    async def obtener_partidos(self, torneo_externo_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"Obteniendo partidos torneo {torneo_externo_id}")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={"league": torneo_externo_id, "season": "2025"},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])

    async def obtener_cuotas(self, partido_externo_id: str) -> List[Dict[str, Any]]:
        logger.debug(f"Obteniendo cuotas partido {partido_externo_id}")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/odds",
                headers=self.headers,
                params={"fixture": partido_externo_id},
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
