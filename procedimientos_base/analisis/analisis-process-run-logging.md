# Análisis: Cuándo se escribe en process_run / process_run_log

## Resumen Ejecutivo

El sistema utiliza un **Factory Pattern** (`ProcessRunRepositoryFactory`) que decide si escribir o no en las tablas de base de datos `process_run` y `process_run_log` basándose en la variable de entorno `PROCESS_RUN_LOGGING_ENABLED`.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    IProcessRunRepository                    │
│                      (Interface)                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────────┐     ┌───────────────────────┐
│ ProcessRunRepository│     │ NoOpProcessRunRepository│
│  (ESCRIBE EN BD)  │     │   (NO ESCRIBE EN BD)   │
└───────────────────┘     └───────────────────────┘
        ▲                           ▲
        │                           │
        └───────────┬───────────────┘
                    │
    ┌───────────────┴───────────────┐
    │  ProcessRunRepositoryFactory  │
    │  (Decide cuál usar)           │
    └───────────────────────────────┘
```

---

## Variable de Entorno: `PROCESS_RUN_LOGGING_ENABLED`

| Valor              | Comportamiento                                   |
| ------------------ | ------------------------------------------------ |
| `"true"` (default) | **ESCRIBE** en `process_run` y `process_run_log` |
| `"1"`              | **ESCRIBE** en `process_run` y `process_run_log` |
| `"yes"`            | **ESCRIBE** en `process_run` y `process_run_log` |
| `"false"`          | **NO ESCRIBE** (usa NoOpProcessRunRepository)    |
| `"0"`              | **NO ESCRIBE** (usa NoOpProcessRunRepository)    |
| No definida        | **ESCRIBE** (default es `"true"`)                |

---

## Casos en los que SÍ se escribe en BD

### 1. Ejecución normal del scheduler (producción/desarrollo)
- **Archivo**: `backend/apps/leagues_manager/tasks/process_rastreo_data_fuentes_deportivas_task.py`
- **Línea**: `repo = ProcessRunRepositoryFactory.get_repository(db=session)`
- **Condición**: Variable `PROCESS_RUN_LOGGING_ENABLED` no está definida o es `"true"` (default)
- **Flujo**:
  1. Se crea `ProcessRun` con `repo.create_run(run_id, process_code)`
  2. Durante la ejecución se escriben logs con `repo.write_log()`
  3. Al finalizar exitosamente: `repo.complete_run(run_id)`
  4. Si falla: `repo.fail_run(run_id)`

### 2. Ejecución manual o via API
- Mismo flujo que producción si no se modifica la variable de entorno

---

## Casos en los que NO se escribe en BD

### 1. Ejecución de tests unitarios (automático)
- **Archivo**: `backend/apps/leagues_manager/tests/conftest.py`
- **Fixture**: `disable_process_run_logging` (autouse=True)
- **Comportamiento**: Establece automáticamente `PROCESS_RUN_LOGGING_ENABLED=false` para TODOS los tests
- **Resultado**: Usa `NoOpProcessRunRepository` que solo almacena en memoria

### 2. Configuración manual para debugging/desarrollo
- Establecer `PROCESS_RUN_LOGGING_ENABLED=false` en `.env` o variable de entorno
- Útil para reducir ruido en BD durante desarrollo

### 3. Ejecución con flag explícito
```python
repo = ProcessRunRepositoryFactory.get_repository(
    db=session,
    use_real_db=False  # Forzar NoOp
)
```

---

## Flujo de Decisión del Factory

```python
# process_run_repository_factory.py

if use_real_db is None:
    # Leer de configuración centralizada (default: True para producción)
    use_real_db = settings.PROCESS_RUN_LOGGING_ENABLED

if use_real_db:
    if db is None:
        raise ValueError("db session is required...")
    logger.info("📊 Usando ProcessRunRepository (ESCRIBE en BD)")
    return ProcessRunRepository(db=db)  # ESCRIBE EN BD

logger.info("🔇 Usando NoOpProcessRunRepository (NO escribe en BD)")
return NoOpProcessRunRepository()  # NO ESCRIBE
```

---

## Estructura de las Tablas

### Tabla `process_run`
- **Registro**: Se crea UN registro por ejecución del scheduler
- **Campos clave**: `run_id`, `process_id`, `status`, `started_at`, `ended_at`
- **Estados**: `in_progress` → `success` | `failed`

### Tabla `process_run_log`
- **Registro**: Múltiples registros por cada paso/acción dentro de una ejecución
- **Campos clave**: `run_id` (FK), `step`, `level`, `message`, `input`, `output`
- **Relación**: Cada log pertenece a un `process_run`

---

## Verificación del Estado Actual

### Para producción/desarrollo normal:
```bash
# Verificar si está habilitado (por defecto SÍ)
echo $PROCESS_RUN_LOGGING_ENABLED

# Para DESHABILITAR temporalmente
export PROCESS_RUN_LOGGING_ENABLED=false

# Para HABILITAR explícitamente
export PROCESS_RUN_LOGGING_ENABLED=true
```

### En archivos .env:
```env
# Añadir esta línea para deshabilitar en desarrollo
PROCESS_RUN_LOGGING_ENABLED=false
```

---

## Puntos de Atención y Mejoras Implementadas

### 1. ✅ **Variable definida en .env** (IMPLEMENTADO)
- La variable `PROCESS_RUN_LOGGING_ENABLED` **YA está definida** en `backend/.env`
- Valor actual: `PROCESS_RUN_LOGGING_ENABLED=true`
- Comportamiento: Escribe en BD por defecto
- **Estado**: ✅ Implementado correctamente

### 2. ✅ **Variable definida en Settings** (IMPLEMENTADO)
- La variable `PROCESS_RUN_LOGGING_ENABLED` **YA está definida** en `backend/core/config.py`
- Tipo: `bool` con default `True`
- Pydantic la carga automáticamente desde `.env`
- **Estado**: ✅ Implementado correctamente

### 3. ✅ **Tests**: Comportamiento correcto (VERIFICADO)
- El fixture `disable_process_run_logging` establece automáticamente `false` en tests
- Esto evita contaminar la BD con datos de tests
- **Estado**: ✅ Correctamente implementado

### 4. ✅ **Logging sobre la decisión** (IMPLEMENTADO)
- Se añadió logging en el factory para indicar qué implementación se está usando
- Logs implementados:
  - `📊 Usando ProcessRunRepository (ESCRIBE en BD)` cuando escribe
  - `🔇 Usando NoOpProcessRunRepository (NO escribe en BD)` cuando no escribe
- **Estado**: ✅ Implementado correctamente

### 5. ✅ **Factory usa settings centralizado** (IMPLEMENTADO)
- El factory ahora usa `settings.PROCESS_RUN_LOGGING_ENABLED` en lugar de `os.getenv`
- Esto es consistente con el resto de la configuración del proyecto
- Pydantic valida el tipo de dato automáticamente
- **Estado**: ✅ Implementado correctamente

---

## Resumen de Comportamiento Actual

| Escenario              | Escribe en BD? | Razón                                 |
| ---------------------- | -------------- | ------------------------------------- |
| Producción (scheduler) | ✅ SÍ           | Default de factory                    |
| Desarrollo local       | ✅ SÍ           | Default de factory                    |
| Tests unitarios        | ❌ NO           | Fixture `disable_process_run_logging` |
| Variable `=false`      | ❌ NO           | Configuración explícita               |
| Variable `=true`       | ✅ SÍ           | Configuración explícita               |
| Variable no definida   | ✅ SÍ           | Default del factory                   |

---

## Archivos Relacionados

1. `backend/shared/repositories/scheduler_repos/process_run_repository_factory.py` - Factory
2. `backend/shared/repositories/scheduler_repos/process_run_repository.py` - Implementación real
3. `backend/shared/repositories/scheduler_repos/noop_process_run_repository.py` - Implementación NoOp
4. `backend/apps/leagues_manager/tasks/process_rastreo_data_fuentes_deportivas_task.py` - Uso principal
5. `backend/apps/leagues_manager/tests/conftest.py` - Configuración de tests

---

## Sistemas Relacionados

### Control de Archivos de Logs
Se implementó un sistema similar para controlar la escritura de archivos de logs:
- **Variable**: `FILE_LOGGING_ENABLED`
- **Comportamiento**: Consola SIEMPRE activa, archivos controlados por variable
- **Documento**: `procedimientos_base/analisis-file-logging.md`

---

*Documento generado: Análisis de estabilidad del sistema de logging de process_run*
