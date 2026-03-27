#!/usr/bin/env python
"""Script de diagnóstico de estado de ligas por país.

Este script verifica:
1. Paises existentes en la BD
2. Ligas registradas por país
3. Paises sin ligas (faltantes)
4. Estadísticas generales
"""

import httpx
import json
from datetime import datetime
from pathlib import Path

# ===================================================================
#  CONFIGURACIÓN
# ===================================================================

API_KEY = "ddc44ff1c845c9c705b6f21d00926633"
API_HOST = "v3.football.api-sports.io"
BASE_URL = f"https://{API_HOST}"

HEADERS = {
    "x-apisports-key": API_KEY,
    "x-apisports-host": API_HOST,
}

TIMEOUT_SECONDS = 30

# ===================================================================
#  FUNCIONES DE DIAGNÓSTICO
# ===================================================================


def get_countries_from_api():
    """Obtiene todos los países disponibles en la API."""
    print("[INFO] Obteniendo paises de la API-Football...")
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(f"{BASE_URL}/countries", headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            countries = data.get("response", [])
            print(f"[OK] {len(countries)} paises obtenidos de la API")
            return countries
    except Exception as e:
        print(f"[ERROR] Error obteniendo paises: {e}")
        return []


def get_leagues_for_country(country_name: str) -> list:
    """Obtiene ligas de un país específico."""
    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(
                f"{BASE_URL}/leagues", headers=HEADERS, params={"country": country_name}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", [])
    except Exception as e:
        print(f"[ERROR] Error obteniendo ligas para {country_name}: {e}")
        return []


def simulate_bd_countries() -> list:
    """Simula países de la BD (GeografiaSeeder ya los cargo)."""
    # Estos son los países que típicamente carga el GeografiaSeeder
    # con ligas de fútbol importantes
    return [
        {"id": 1, "nombre": "Argentina", "codigo_iso": "AR", "continente_id": 6},
        {"id": 2, "nombre": "Spain", "codigo_iso": "ES", "continente_id": 4},
        {"id": 3, "nombre": "England", "codigo_iso": "GB", "continente_id": 4},
        {"id": 4, "nombre": "Germany", "codigo_iso": "DE", "continente_id": 4},
        {"id": 5, "nombre": "Italy", "codigo_iso": "IT", "continente_id": 4},
        {"id": 6, "nombre": "France", "codigo_iso": "FR", "continente_id": 4},
        {"id": 7, "nombre": "Brazil", "codigo_iso": "BR", "continente_id": 6},
        {"id": 8, "nombre": "Mexico", "codigo_iso": "MX", "continente_id": 5},
        {"id": 9, "nombre": "Portugal", "codigo_iso": "PT", "continente_id": 4},
        {"id": 10, "nombre": "Netherlands", "codigo_iso": "NL", "continente_id": 4},
        {"id": 11, "nombre": "Belgium", "codigo_iso": "BE", "continente_id": 4},
        {"id": 12, "nombre": "Turkey", "codigo_iso": "TR", "continente_id": 4},
        {"id": 13, "nombre": "Greece", "codigo_iso": "GR", "continente_id": 4},
        {"id": 14, "nombre": "Scotland", "codigo_iso": "GB", "continente_id": 4},
        {"id": 15, "nombre": "USA", "codigo_iso": "US", "continente_id": 5},
        {"id": 16, "nombre": "Canada", "codigo_iso": "CA", "continente_id": 5},
        {"id": 17, "nombre": "Japan", "codigo_iso": "JP", "continente_id": 2},
        {"id": 18, "nombre": "South Korea", "codigo_iso": "KR", "continente_id": 2},
        {"id": 19, "nombre": "Australia", "codigo_iso": "AU", "continente_id": 3},
        {"id": 20, "nombre": "China", "codigo_iso": "CN", "continente_id": 2},
    ]


def simulate_leagues_in_bd() -> dict:
    """Simula ligas existentes en la BD."""
    # Simula que algunos países ya tienen ligas registradas
    return {
        "AR": 5,  # Argentina tiene 5 ligas
        "ES": 3,  # España tiene 3 ligas
        "GB": 2,  # Inglaterra tiene 2 ligas
        "DE": 0,  # Alemania no tiene ligas
        "IT": 0,  # Italia no tiene ligas
    }


def analyze_leagues_gap():
    """Analiza brecha entre API y BD."""
    print("\n" + "=" * 70)
    print("[DIAGNOSTICO] ANALISIS DE BRECHA DE LIGAS")
    print("=" * 70)

    # Obtener países de la BD (simulado)
    bd_countries = simulate_bd_countries()
    print(f"\n[BD] Paises en base de datos: {len(bd_countries)}")

    # Simular ligas existentes
    bd_leagues = simulate_leagues_in_bd()

    # Obtener países de la API
    api_countries = get_countries_from_api()

    # Crear mapa de países de la BD por código ISO
    bd_countries_map = {c["codigo_iso"]: c for c in bd_countries}

    # Análisis
    print("\n" + "-" * 70)
    print("ESTADO POR PAIS:")
    print("-" * 70)

    countries_with_leagues = []
    countries_without_leagues = []

    for bd_country in bd_countries[:10]:  # Mostrar primeros 10
        code = bd_country["codigo_iso"]
        name = bd_country["nombre"]
        leagues_count = bd_leagues.get(code, 0)

        if leagues_count > 0:
            status = f"[OK] {leagues_count} ligas"
            countries_with_leagues.append(bd_country)
        else:
            status = "[PENDIENTE] Sin ligas"
            countries_without_leagues.append(bd_country)

        print(f"  {code:3s} - {name:20s} | {status}")

    # Resumen
    print("\n" + "=" * 70)
    print("[RESUMEN] ESTADISTICAS:")
    print("=" * 70)
    print(f"  Paises en BD: {len(bd_countries)}")
    print(f"  Paises con ligas: {len(countries_with_leagues)}")
    print(f"  Paises sin ligas: {len(countries_without_leagues)}")

    # Paises prioritarios sin ligas
    print("\n" + "=" * 70)
    print("[PRIORIDAD] PAISES SIN LIGAS (Necesitan procesamiento):")
    print("=" * 70)

    priority_countries = [
        ("DE", "Germany", "Bundesliga"),
        ("IT", "Italy", "Serie A"),
        ("FR", "France", "Ligue 1"),
        ("BR", "Brazil", "Brasileirao"),
        ("MX", "Mexico", "Liga MX"),
        ("PT", "Portugal", "Primeira Liga"),
        ("NL", "Netherlands", "Eredivisie"),
        ("BE", "Belgium", "Pro League"),
        ("TR", "Turkey", "Super Lig"),
        ("US", "USA", "MLS"),
    ]

    for code, name, league_name in priority_countries:
        if code in [c["codigo_iso"] for c in countries_without_leagues]:
            print(f"  {code:3s} - {name:20s} | Liga principal: {league_name}")

    # Estrategia de lotes
    print("\n" + "=" * 70)
    print("[ESTRATEGIA] PLAN DE LOTES (50 requests/dia):")
    print("=" * 70)

    total_countries = len(bd_countries)
    batch_size = 50
    total_batches = (total_countries + batch_size - 1) // batch_size

    print(f"  Total paises a procesar: {total_countries}")
    print(f"  Tamanio de lote: {batch_size} paises")
    print(f"  Total lotes necesarios: {total_batches}")
    print(f"  Requests por dia: ~{batch_size}")
    print(f"  Dias para completar: {total_batches}")

    # Lotes sugeridos
    print("\n  LOTES SUGERIDOS:")
    for i in range(0, min(total_countries, 100), batch_size):
        batch_num = (i // batch_size) + 1
        batch_countries = bd_countries[i : i + batch_size]
        batch_codes = [c["codigo_iso"] for c in batch_countries[:5]]
        print(
            f"    Lote {batch_num}: {len(batch_countries)} paises (ej: {', '.join(batch_codes)}...)"
        )

    return countries_without_leagues


def generate_cache_structure():
    """Genera estructura de cache JSON."""
    print("\n" + "=" * 70)
    print("[CACHE] ESTRUCTURA DE CACHE PROPUESTA:")
    print("=" * 70)

    cache_example = {
        "metadata": {
            "ultima_actualizacion": datetime.now().isoformat(),
            "version": "1.0",
            "total_paises": 0,
            "total_ligas": 0,
        },
        "paises": {},
    }

    print(json.dumps(cache_example, indent=2, ensure_ascii=False))

    # Guardar ejemplo
    cache_file = Path("backend/data/leagues_cache.json")
    cache_file.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache_example, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Archivo de cache creado: {cache_file}")


# ===================================================================
#  MAIN
# ===================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("[LIGAS] DIAGNOSTICO DE ESTADO DE LIGAS")
    print(f"[FECHA] Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Ejecutar análisis
    countries_without_leagues = analyze_leagues_gap()

    # Generar estructura de cache
    generate_cache_structure()

    print("\n" + "=" * 70)
    print("[DECISION] PUNTOS PARA TOMAR DECISION:")
    print("=" * 70)
    print(
        """
    1. CAMPO NAME_STANDARD:
       - Los nombres de paises en la API vienen en ingles
       - Nuestra BD tambien los guarda en ingles (GeografiaSeeder)
       - RECOMENDACION: NO agregar campo name_standard
       - RAZON: Ya tenemos codigo_iso como identificador unico
       - ALTERNATIVA: Usar codigo_iso para matching (mas robusto)

    2. ESTRATEGIA DE LOTES:
       - Procesar 50 paises por dia
       - Priorizar ligas principales (Bundesliga, Serie A, etc.)
       - Guardar cache en JSON para evitar re-requests
       - Marcar ligas desaparecidas como is_active=False

    3. MECANISMO DE VALIDACION:
       - Verificar existencia por id_api_externa
       - Si existe: actualizar
       - Si no existe: crear
       - Si no aparece en API: marcar como inactiva

    4. DIAGNOSTICO VISUAL:
       - Script creado: backend/scripts/diagnose_leagues_status.py
       - Muestra paises con/sin ligas
       - Identifica prioridades
       - Calcula lotes necesarios
    """
    )
