#!/usr/bin/env python
"""Script de diagnóstico para API-Football v3.

Este script verifica:
1. Conexión a la API
2. Endpoints disponibles
3. Estructura de respuesta
4. Viabilidad para obtener ligas por país
"""

import httpx
import json
from datetime import datetime

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


def test_connection():
    """Prueba la conexión básica a la API."""
    print("=" * 70)
    print("TEST 1: Conexión a la API")
    print("=" * 70)

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(f"{BASE_URL}/status", headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            print("[OK] Conexion exitosa!")
            print(f"   Status Code: {response.status_code}")
            print("   Respuesta:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
    except Exception as e:
        print(f"[ERROR] Error de conexión: {e}")
        return False


def test_leagues_endpoint():
    """Prueba el endpoint de ligas."""
    print("\n" + "=" * 70)
    print("TEST 2: Endpoint de Ligas")
    print("=" * 70)

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            # Obtener ligas de Argentina como ejemplo
            response = client.get(
                f"{BASE_URL}/leagues", headers=HEADERS, params={"country": "Argentina"}
            )
            response.raise_for_status()
            data = response.json()

            print("[OK] Endpoint /leagues accesible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Total de ligas encontradas: {len(data.get('response', []))}")

            # Mostrar las primeras 3 ligas como ejemplo
            leagues = data.get("response", [])[:3]
            for i, league_data in enumerate(leagues, 1):
                league = league_data.get("league", {})
                country = league_data.get("country", {})
                print(f"\n   Liga {i}:")
                print(f"      ID: {league.get('id')}")
                print(f"      Nombre: {league.get('name')}")
                print(f"      Tipo: {league.get('type')}")
                print(f"      Pais: {country.get('name')} ({country.get('code')})")

            # Mostrar estructura completa de la primera liga
            if data.get("response"):
                print("\n   [ESTRUCTURA] Estructura completa de la primera liga:")
                first_league = data["response"][0]
                print(json.dumps(first_league, indent=6, ensure_ascii=False))

            return True
    except Exception as e:
        print(f"[ERROR] Error en endpoint de ligas: {e}")
        return False


def test_countries_endpoint():
    """Prueba el endpoint de países."""
    print("\n" + "=" * 70)
    print("TEST 3: Endpoint de Paises")
    print("=" * 70)

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(f"{BASE_URL}/countries", headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            print("[OK] Endpoint /countries accesible!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Total de paises: {len(data.get('response', []))}")

            # Mostrar los primeros 5 países
            countries = data.get("response", [])[:5]
            for i, country in enumerate(countries, 1):
                print(f"   {i}. {country.get('name')} ({country.get('code')})")

            return True
    except Exception as e:
        print(f"[ERROR] Error en endpoint de países: {e}")
        return False


def test_rate_limit():
    """Verifica información sobre límites de rate limiting."""
    print("\n" + "=" * 70)
    print("TEST 4: Informacion de Rate Limiting")
    print("=" * 70)

    try:
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            response = client.get(f"{BASE_URL}/status", headers=HEADERS)
            response.raise_for_status()
            data = response.json()

            # Extraer información de rate limiting
            subscription = data.get("response", {}).get("subscription", {})
            requests = data.get("response", {}).get("requests", {})

            print("   [INFO] Informacion de suscripcion:")
            print(f"      Plan: {subscription.get('plan', 'N/A')}")
            print(f"      Estado: {subscription.get('active', 'N/A')}")
            print(f"      Expira: {subscription.get('expire', 'N/A')}")

            print("\n   [ESTADISTICAS] Informacion de requests:")
            print(f"      Requests actuales: {requests.get('current', 'N/A')}")
            print(f"      Limite diario: {requests.get('limit_day', 'N/A')}")

            if requests.get("limit_day"):
                remaining = requests["limit_day"] - requests.get("current", 0)
                print(f"      Requests restantes hoy: {remaining}")

            return True
    except Exception as e:
        print(f"[ERROR] Error obteniendo información de rate limiting: {e}")
        return False


def analyze_feasibility():
    """Analiza la viabilidad de usar la API para poblar ligas."""
    print("\n" + "=" * 70)
    print("ANALISIS DE VIABILIDAD")
    print("=" * 70)

    print(
        """
    [OK] VENTAJAS:
    1. API RESTful estandar con documentacion clara
    2. Endpoint /leagues permite filtrar por pais
    3. Estructura de datos bien definida
    4. Incluye informacion de temporadas, logos, etc.
    
    [ADVERTENCIA] LIMITACIONES:
    1. Limite de 100 requests diarios (plan gratuito)
    2. Necesitariamos ~200 paises x 1 request = 200 requests
    3. Esto excede el limite diario
    
    [IDEA] ESTRATEGIA RECOMENDADA:
    1. Obtener TODOS los paises del GeografiaSeeder (ya tenemos ~250)
    2. Para cada pais, hacer 1 request a /leagues?country={nombre}
    3. Procesar en lotes de 50 paises por dia (dentro del limite)
    4. Cachear resultados en archivo JSON para evitar re-requests
    5. Usar el campo "code" del pais (ISO 3166-1 alpha-2) para matching
    
    [ENDPOINTS] ENDPOINTS NECESARIOS:
    - GET /leagues?country={country_name} -> Obtiene ligas de un pais
    - GET /countries -> Lista de paises disponibles en la API
    
    [MATCH] MATCHING CON NUESTRO SISTEMA:
    - Usar campo "code" del pais (ej: "AR" para Argentina)
    - Buscar en nuestra tabla "pais" por "codigo_iso"
    - Crear registros en tabla "liga" con los datos de la API
    """
    )


# ===================================================================
#  MAIN
# ===================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("[FOOTBALL] DIAGNOSTICO DE API-FOOTBALL v3")
    print(f"[FECHA] Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Ejecutar tests
    test1 = test_connection()
    test2 = test_leagues_endpoint()
    test3 = test_countries_endpoint()
    test4 = test_rate_limit()

    # Análisis de viabilidad
    analyze_feasibility()

    # Resumen
    print("\n" + "=" * 70)
    print("[RESUMEN] RESUMEN")
    print("=" * 70)
    print(f"   [OK] Conexion API: {'OK' if test1 else 'FALLO'}")
    print(f"   [OK] Endpoint Ligas: {'OK' if test2 else 'FALLO'}")
    print(f"   [OK] Endpoint Paises: {'OK' if test3 else 'FALLO'}")
    print(f"   [OK] Rate Limiting: {'OK' if test4 else 'FALLO'}")

    if all([test1, test2, test3, test4]):
        print("\n[EXITO] API completamente funcional y viable para uso!")
    else:
        print("\n[ADVERTENCIA] Algunos tests fallaron. Revisar errores arriba.")

    print("=" * 70)
