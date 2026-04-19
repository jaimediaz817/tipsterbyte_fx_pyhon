
## Información del Proyecto
- **Nombre**: TipsterByte FX
- **Tipo**: Backend Python con FastAPI
- **Base de Datos**: PostgreSQL + MongoDB
- **Arquitectura**: DDD (Domain-Driven Design) + Clean Architecture

## Convenciones de Código
1. **Lenguaje**: Python 3.11+
2. **Framework**: FastAPI
3. **ORM**: SQLAlchemy (SQL) + MongoEngine (NoSQL)
4. **Logging**: Loguru
5. **Testing**: Pytest

## Estructura del Proyecto
- `backend/apps/` - Aplicaciones por dominio (leagues_manager, platform_config)
- `backend/core/` - Núcleo compartido (db, scheduler, monitoring, exceptions)
- `backend/shared/` - Código compartido (repositorios, constantes)
- `backend/scripts/` - Scripts de utilidad y diagnóstico
- `backend/commands/` - Comandos CLI

## Reglas de Comunicación
1. **Idioma**: Español (es)
2. **Formato de respuestas**: Directo y técnico
3. **Prefijo de herramientas**: Usar formato XML para herramientas
4. **Task Progress**: Incluir siempre checklist de progreso

## Reglas de Desarrollo
1. **SOLID**: Aplicar principios SOLID siempre
2. **Type Hints**: Usar type hints en todas las funciones
3. **Docstrings**: Documentar funciones públicas
4. **Tests**: Crear tests para nueva funcionalidad
5. **Migrations**: Usar Alembic para cambios en DB

## ✅ REGLA OBLIGATORIA PRUEBAS UNITARIAS
> APLICAR SIEMPRE SIN EXCEPCIONES EN TODOS LOS ARCHIVOS TEST
> Todas las pruebas unitarias DEBEN ser ejecutables:
> ✅ Desde Testing Explorer de VS Code
> ✅ Ejecutando manualmente `python nombre_archivo.py`
> ✅ Ejecutando pytest desde cualquier ubicacion

### Patron estandar a usar en CABECERA de TODO test:
```python
import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[4]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv
load_dotenv(ROOT_PROYECTO / "backend" / ".env")
2. **Métodos Create/Update**: Usar `cast()` para indicar que el valor de retorno NO es None
3. **Repositorios**: Siempre retornar entidades de dominio, NUNCA modelos de SQL
4. **Forward References**: Usar comillas dobles para tipos en declaraciones de métodos

## ✅ ✅ ✅  REGLA NUEVA ERROR DE AWAIT NONE
Cuando encuentres el error:
```
TypeError: 'NoneType' object can't be awaited
"None" is not awaitable
```

✅ SOLUCION OBLIGATORIA STANDARD:
```python
from typing import cast, Awaitable
await cast(Awaitable[None], metodo_async())
```

❌ NUNCA quitar el await (rompe el codigo real)
❌ NUNCA ignorar el error
✅ Siempre usar cast() para solucionar el falso positivo

---

## ✅ ✅ ✅  REGLA NUCLEAR INQUEBRANTABLE VELOCIDAD TESTS
> 👉 ESTA ES LA REGLA MAS IMPORTANTE DE TODO EL PROYECTO

### ❌ EL ERROR QUE NUNCA MAS SE DEBE REPETIR:
Nunca, jamas, bajo ningun concepto poner la proteccion contra BD en tests DESPUES de importar dependencias.

### ✅ PATRON OBLIGATORIO PARA TODOS LOS ARCHIVOS DE INFRAESTRUCTURA:
```python
# ✅ PRIMERO: PROTECCION ANTES DE TODO LO DEMAS
import os
if os.environ.get("PYTEST_VERSION") is not None:
    raise RuntimeError("⛔ NO USAR INFRAESTRUCTURA REAL EN TESTS UNITARIOS")

# ✅ SEGUNDO: AHORA SI, IMPORTAR EL RESTO
from sqlalchemy import create_engine
...
```

✅ ESTA ES LA UNICA FORMA DE QUE LOS TESTS SEAN RAPIDOS.
✅ Cualquier otra posicion de la proteccion es INUTIL.
✅ Esto asegura que NUNCA se carga SQLAlchemy, modelos, conexiones ni nada de infraestructura durante el discovery de pytest.

❌ NO PONGAS LA PROTECCION EN MEDIO DEL ARCHIVO
❌ NO PONGAS LA PROTECCION DESPUES DE IMPORTAR COSAS
❌ NO HAGAS NADA ANTES DE LA PROTECCION
