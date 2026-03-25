# Análisis: Control de Escritura de Archivos de Logs

## Resumen Ejecutivo

El sistema de logging actual usa **Loguru** con múltiples sinks (destinos) configurados en `backend/core/logger.py`. Los logs se escriben SIEMPRE en archivos, sin ningún mecanismo de control para deshabilitarlos. Este análisis propone una solución para controlar la escritura de archivos de logs de manera similar a como se implementó para `process_run`.

---

## Arquitectura Actual del Sistema de Logging

```
┌─────────────────────────────────────────────────────────────┐
│                    Loguru Logger                            │
│                    (core/logger.py)                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
   │ Consola │  │system.log│  │scheduler│  │robots.log│
   │ (stdout)│  │          │  │  .log   │  │          │
   └─────────┘  └──────────┘  └─────────┘  └──────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
   │general_ │  │ leagues_ │  │  auth   │  │platform_ │
   │ app.log │  │manager.log│  │  .log   │  │config.log│
   └─────────┘  └──────────┘  └─────────┘  └──────────┘
```

---

## Puntos de Escritura de Logs Identificados

### 1. **Consola (stdout)**
- **Ubicación**: `backend/core/logger.py` línea ~95
- **Comportamiento**: SIEMPRE activo
- **Uso**: Logs en terminal para desarrollo

### 2. **system.log**
- **Ubicación**: `backend/logs/system.log`
- **Filtro**: Logs de `core.*` (excluyendo scheduler)
- **Rotación**: 10 MB, 7 días retención

### 3. **scheduler/scheduler.log**
- **Ubicación**: `backend/logs/scheduler/scheduler.log`
- **Filtro**: Logs que contienen "scheduler" en el nombre
- **Rotación**: 5 MB, 14 días retención

### 4. **robots.log**
- **Ubicación**: `backend/logs/robots.log`
- **Filtro**: Logs de `apps.leagues_manager.robots.*`
- **Rotación**: 10 MB, 10 días retención

### 5. **Sinks dinámicos por módulo**
- **Ubicación**: `backend/logs/{module_name}.log`
- **Módulos**: leagues_manager, auth, platform_config
- **Rotación**: 10 MB, 10 días retención

### 6. **general_app.log**
- **Ubicación**: `backend/logs/general_app.log`
- **Filtro**: Logs que NO son de core, scheduler ni apps.*
- **Rotación**: 20 MB, 5 días retención

---

## Propuesta de Implementación

### Opción 1: Variable Global `FILE_LOGGING_ENABLED`

```python
# backend/core/config.py
FILE_LOGGING_ENABLED: bool = Field(
    True,
    description="Controla si se escriben logs en archivos. Consola SIEMPRE activa."
)
```

**Ventajas**:
- Simple y directo
- Similar a `PROCESS_RUN_LOGGING_ENABLED`
- Consola siempre activa (no se pierde visibilidad)

**Desventajas**:
- Control todo-o-nada (no se puede deshabilitar solo un archivo)

### Opción 2: Variables por Cada Sink

```python
FILE_LOGGING_ENABLED: bool = Field(True, description="...")
SYSTEM_LOG_ENABLED: bool = Field(True, description="...")
SCHEDULER_LOG_ENABLED: bool = Field(True, description="...")
ROBOTS_LOG_ENABLED: bool = Field(True, description="...")
```

**Ventajas**:
- Control granular por tipo de log
- Permite deshabilitar solo logs específicos

**Desventajas**:
- Más complejo de configurar
- Más variables de entorno

### Opción 3: Lista de Sinks Habilitados

```python
ENABLED_LOG_SINKS: str = Field(
    "console,system,scheduler,robots,general",
    description="Lista de sinks de logs habilitados (separados por coma)"
)
```

**Ventajas**:
- Flexible
- Una sola variable

**Desventajas**:
- Más complejo de parsear
- Menos intuitivo

---

## Impacto en Tests Unitarios

### Tests Afectados

1. **`backend/core/tests/test_logger.py`**
   - `TestConfigureLogging`: Prueba la configuración completa
   - `TestSafeAddSink`: Prueba agregar sinks
   - **Impacto**: Necesitarán mockear la nueva variable

2. **`backend/core/tests/test_robot_logging.py`**
   - Prueba funciones de logging de robots
   - **Impacto**: Bajo (usa logger directamente, no archivos)

3. **Tests de integración**
   - Pueden generar logs en archivos durante la ejecución
   - **Impacto**: Podrían necesitar deshabilitar logs de archivos

### Estrategia para Tests

```python
# backend/apps/leagues_manager/tests/conftest.py
@pytest.fixture(autouse=True)
def disable_file_logging():
    """Deshabilita escritura de archivos de logs en tests."""
    original_value = os.environ.get("FILE_LOGGING_ENABLED")
    os.environ["FILE_LOGGING_ENABLED"] = "false"
    yield
    if original_value is None:
        os.environ.pop("FILE_LOGGING_ENABLED", None)
    else:
        os.environ["FILE_LOGGING_ENABLED"] = original_value
```

---

## Implementación Recomendada

### Archivos a Modificar

1. **`backend/core/config.py`**
   - Añadir `FILE_LOGGING_ENABLED: bool = Field(True, ...)`

2. **`backend/core/logger.py`**
   - Modificar `configure_logging()` para verificar la variable
   - Solo agregar sinks de archivos si `settings.FILE_LOGGING_ENABLED`

3. **`backend/.env`**
   - Añadir `FILE_LOGGING_ENABLED=true`

4. **`backend/apps/leagues_manager/tests/conftest.py`**
   - Añadir fixture `disable_file_logging` (autouse=True)

5. **`procedimientos_base/analisis-file-logging.md`**
   - Este documento

### Código de Implementación

```python
# backend/core/logger.py - configure_logging()

def configure_logging():
    logger.remove()
    LOGS_ROOT.mkdir(exist_ok=True)

    # Redirigir logging estándar
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Formatos
    console_format = "..."
    file_format = "..."

    # Consola SIEMPRE activa
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=console_format,
        colorize=True,
    )

    # Archivos SOLO si FILE_LOGGING_ENABLED
    if settings.FILE_LOGGING_ENABLED:
        # System
        _safe_add_sink(LOGS_ROOT / "system.log", ...)
        
        # Scheduler
        _safe_add_sink(LOGS_ROOT / "scheduler" / "scheduler.log", ...)
        
        # Robots
        _safe_add_sink(LOGS_ROOT / "robots.log", ...)
        
        # Sinks dinámicos
        for module_name in module_names:
            _safe_add_sink(LOGS_ROOT / f"{module_name}.log", ...)
        
        # General
        _safe_add_sink(LOGS_ROOT / "general_app.log", ...)

    logger.info("✅ Logging configurado correctamente.")
```

---

## Comportamiento Esperado

| Escenario         | Consola | Archivos | Razón                                |
| ----------------- | ------- | -------- | ------------------------------------ |
| Producción        | ✅ SÍ    | ✅ SÍ     | Default: `FILE_LOGGING_ENABLED=true` |
| Desarrollo        | ✅ SÍ    | ✅ SÍ     | Default: `FILE_LOGGING_ENABLED=true` |
| Tests unitarios   | ✅ SÍ    | ❌ NO     | Fixture deshabilita archivos         |
| Variable `=false` | ✅ SÍ    | ❌ NO     | Configuración explícita              |
| Variable `=true`  | ✅ SÍ    | ✅ SÍ     | Configuración explícita              |

---

## Riesgos y Consideraciones

### 1. **Rendimiento**
- **Riesgo**: Bajo. Solo se evita agregar sinks, no se modifica el flujo de logging
- **Mitigación**: La consola sigue funcionando normalmente

### 2. **Debugging en Producción**
- **Riesgo**: Si se deshabilitan archivos, se pierde trazabilidad
- **Mitigación**: Documentar claramente que solo se debe deshabilitar en tests

### 3. **Compatibilidad con Tests Existentes**
- **Riesgo**: Tests que verifican archivos de logs fallarán
- **Mitigación**: Actualizar tests para usar el fixture `disable_file_logging`

### 4. **Orden de Inicialización**
- **Riesgo**: `configure_logging()` se ejecuta antes de que settings esté disponible
- **Mitigación**: Verificar que settings se carga antes de llamar a configure_logging()

---

## Estimación de Esfuerzo

| Tarea                        | Tiempo Estimado |
| ---------------------------- | --------------- |
| Modificar config.py          | 5 min           |
| Modificar logger.py          | 15 min          |
| Actualizar .env              | 2 min           |
| Crear fixture en conftest.py | 10 min          |
| Actualizar tests existentes  | 20 min          |
| Crear documentación          | 15 min          |
| **Total**                    | **~1 hora**     |

---

## Recomendación Final

**Implementar Opción 1** (variable global `FILE_LOGGING_ENABLED`) porque:
1. Es simple y consistente con `PROCESS_RUN_LOGGING_ENABLED`
2. Resuelve el problema de contaminación de archivos en tests
3. Mantiene la consola siempre activa (no se pierde visibilidad)
4. Fácil de entender y mantener

---

*Documento generado: Análisis de control de escritura de archivos de logs*