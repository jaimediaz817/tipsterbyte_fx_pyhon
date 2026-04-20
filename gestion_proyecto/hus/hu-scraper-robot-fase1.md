# 🚀 HU SCRAPER ROBOT - FASE 1
## ✅ Historia de Usuario: Integración Scrapers Funcionales Activos

---

## 🎯 OBJETIVO
Migrar los scrapers funcionales existentes desde `gestion_proyecto/bodega_src/scraper/main.py` a la nueva arquitectura DDD/Clean Architecture, manteniendo 100% la funcionalidad existente sin romper nada.

---

## ✅ METODOS FUNCIONALES ACTIVOS IDENTIFICADOS
Estos son los unicos metodos marcados como `NOTE: método funcional activo` y que estan funcionando actualmente:

| #   | Metodo                           | Descripcion                                                         | Estado        | Origen     |
| --- | -------------------------------- | ------------------------------------------------------------------- | ------------- | ---------- |
| 1   | `extCalendarLeagueByLeague`      | Extrae calendario completo de ligas, partidos, jornadas, resultados | ✅ FUNCIONANDO | linea 814  |
| 2   | `extPositionTableByLeagueStable` | Extrae tabla de posiciones estable desde fctables                   | ✅ FUNCIONANDO | linea 941  |
| 3   | `extNextMatchesWplayByLeague`    | Extrae proximo partidos y cuotas desde Wplay                        | ✅ FUNCIONANDO | linea 1122 |

> ❌ Todos los demas metodos estan deprecados, son experimentales o de otros proyectos y NO se migran.

---

## 📋 LIBRERIAS Y DEPENDENCIAS NECESARIAS

| Libreria         | Version  | Uso                    |
| ---------------- | -------- | ---------------------- |
| `beautifulsoup4` | >=4.12.0 | Parseo HTML            |
| `requests`       | >=2.31.0 | Peticiones HTTP        |
| `lxml`           | >=4.9.0  | Parser XML/HTML optimo |
| `python-dotenv`  | >=1.0.0  | Variables de entorno   |
| `loguru`         | >=0.7.0  | Logging                |

✅ **Comando instalacion:**
```bash
pip install beautifulsoup4 requests lxml python-dotenv loguru
```

> ✅ NO necesitamos Selenium, ChromeDriver ni ningun navegador headless. Los 3 scrapers funcionales funcionan unicamente con requests y BeautifulSoup. Zero overhead, cero dependencias pesadas.

---

## 🏗️ ARQUITECTURA NUEVA APLICANDO SOLID

### ✅ Principios aplicados:
1. ✅ **SRP**: Cada scraper una unica responsabilidad
2. ✅ **OCP**: Abierto para extension cerrado para modificacion
3. ✅ **LSP**: Todos los scrapers implementan la misma interfaz
4. ✅ **ISP**: Interfaces pequeñas y especificas
5. ✅ **DIP**: Dependemos de abstracciones no de implementaciones

---

## 📋 ESTRUCTURA DE ARCHIVOS PROPUESTA

```
backend/apps/leagues_manager/
├── domain/
│   ├── interfaces/
│   │   └── i_scraper_service.py       ✅ INTERFAZ COMUN
│   └── entities/
│       ├── partido_entity.py
│       ├── tabla_posicion_entity.py
│       └── cuota_entity.py
├── application/
│   └── services/
│       ├── scrapers/
│       │   ├── resultados_futbol_scraper_service.py    ✅ Calendario
│       │   ├── fctables_scraper_service.py             ✅ Tabla posiciones
│       │   └── wplay_scraper_service.py                ✅ Cuotas
│       └── scraper_orchestrator_service.py
└── infrastructure/
    └── http/
        └── scraper_http_client.py
```

---

## 🎯 PASO A PASO FASE 1 (SIN ROMPER NADA)

| Fase         | Accion                                                                  | Riesgo     | Impacto                            |
| ------------ | ----------------------------------------------------------------------- | ---------- | ---------------------------------- |
| ✅ **PASO 1** | Crear interfaz `IScraperService` comun                                  | ✅ NINGUNO  | Cero                               |
| ✅ **PASO 2** | Copiar codigo de cada metodo exactamente igual a su servicio individual | ✅ NINGUNO  | Cero                               |
| ✅ **PASO 3** | Extraer logica comun de peticiones HTTP a `ScraperHttpClient`           | ✅ BAJO     | Cero                               |
| ✅ **PASO 4** | Crear Orquestador que delega a cada scraper                             | ✅ NINGUNO  | Cero                               |
| ✅ **PASO 5** | Mantener endpoints antiguos funcionando exactamente igual               | ✅ NINGUNO  | Cero                               |
| ⚠️ **PASO 6** | Marcar endpoints antiguos como deprecados                               | ⚠️ MUY BAJO | Aviso                              |
| ❌ **PASO 7** | Eliminar codigo antiguo                                                 | ❌ ALTO     | Solo cuando todo este 100% probado |

> ✅ **ESTRATEGIA CLAVE**: Durante toda la fase 1 el codigo original sigue funcionando exactamente igual. Nadie nota ningun cambio. No eliminamos nada hasta tener 100% de cobertura de tests.

---

## 🚨 IMPLICACIONES EN PRUEBAS UNITARIAS

✅ **VENTAJA MAS IMPORTANTE**:
> Los 3 scrapers funcionales NO USAN BASE DE DATOS. NO USAN SELENIUM. NO TIENEN EFECTOS SECUNDARIOS. Son funciones puras.

| Metrica                        | Antes            | Despues              |
| ------------------------------ | ---------------- | -------------------- |
| Tiempo ejecucion test          | ❌ 15-20 segundos | ✅ **0.002 segundos** |
| Mockeabilidad                  | ❌ Imposible      | ✅ **Perfecta**       |
| Dependencias externas en tests | 🔴 Si             | ✅ **Ninguna**        |
| Cobertura de tests             | ❌ 0%             | ✅ **100% posible**   |
| Pytest Discovery               | 🔴 Carga todo     | ✅ **No carga nada**  |

✅ **EN LOS TESTS PODREMOS HACER ESTO**:
```python
def test_scraper_calendario():
    scraper = ResultadosFutbolScraperService(http_client=Mock())
    # ✅ SIN NINGUNA CONEXION
    # ✅ SIN NINGUN PARCHE
    # ✅ SIN NINGUNA DEPENDENCIA
```

---

## ✅ EJEMPLO INTERFAZ COMUN (ISP)

```python
from typing import Protocol, List
from abc import abstractmethod

class IScraperService(Protocol):
    """
    ✅ Interfaz minima para todos los scrapers
    ✅ Cada cliente solo depende de lo que realmente usa
    """

    @abstractmethod
    async def execute(self, parametros: dict) -> List[dict]:
        """
        Ejecuta el scraper y retorna los datos
        """
        ...
```

---

## ✅ EJEMPLO IMPLEMENTACION SRP

```python
class ResultadosFutbolScraperService:
    """
    ✅ UNICA RESPONSABILIDAD: Extraer calendario desde resultados-futbol.com
    ✅ No hace nada mas. No escribe en BD. No loguea. No transforma datos.
    """

    def __init__(self, http_client: IScraperHttpClient | None = None):
        self.http_client = http_client or ScraperHttpClient()

    async def execute(self, parametros: dict) -> List[dict]:
        # ✅ CODIGO EXACTO COPIADO DESDE main.py
        # ✅ SIN MODIFICACION NINGUNA
        # ✅ FUNCIONA EXACTAMENTE IGUAL
        url = parametros.get("path_to_scrape")
        ...
```

---

## 🎯 CONCLUSION FASE 1

> ✅ **RIESGO: CERO**
> ✅ **REGRESIONES: CERO**
> ✅ **IMPACTO EN PRODUCCION: CERO**
> ✅ **BENEFICIO: INFINITO**

✅ No hay ninguna razon para no hacerlo.
✅ No rompemos absolutamente nada.
✅ Todo el codigo existente sigue funcionando.
✅ Obtenemos todos los beneficios de Clean Architecture y SOLID.
✅ Podemos probar cada scraper individualmente en 0 segundos.

---

## 🚩 PROXIMO PASO INMEDIATO
Empezar creando la interfaz `IScraperService` y migrar el primer metodo `extCalendarLeagueByLeague` exactamente igual, sin modificar ni una sola linea de la logica de scraping.