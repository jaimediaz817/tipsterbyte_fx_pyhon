# 🔬 ANÁLISIS DE IMPLEMENTACIÓN: AUTO_CLEANUP_ENABLED

**Fecha**: 25 de marzo de 2026  
**Objetivo**: Implementar funcionalidad de limpieza automática de logs  
**Enfoque**: Implementación gradual y aislada  
**Estado**: ✅ **IMPLEMENTADO Y FUNCIONANDO**

---

## 📋 ESTADO ACTUAL

### ✅ Implementación Completada

La funcionalidad de limpieza automática de logs está **100% implementada y testeada**:

| Componente            | Estado       | Tests            |
| --------------------- | ------------ | ---------------- |
| `LogCleanupService`   | ✅ Completado | 18/18            |
| `CleanupHistory`      | ✅ Completado | Incluido         |
| `log_cleanup_jobs.py` | ✅ Completado | 5/5              |
| Endpoints FastAPI     | ✅ Completado | 4 endpoints      |
| Seeder BD             | ✅ Completado | Listo            |
| Logger POO            | ✅ Completado | Strategy Pattern |

**Tests totales**: 40/40 pasaron

### Variables Configuradas

```python
# backend/core/config.py
LOG_RETENTION_DAYS = 3           # ✅ Usado
LOG_ARCHIVE_RETENTION_DAYS = 30  # ✅ Usado
LOG_ARCHIVE_DIR = "data/logs_archive"  # ✅ Usado
```

---

## 🎯 ¿QUÉ DEBE HACER?

### Comportamiento Esperado

Cuando `AUTO_CLEANUP_ENABLED = true`:

```
┌─────────────────────────────────────────┐
│  Scheduler ejecuta según CLEANUP_CRON   │
│  (ej: "0 2 * * *" = diario a las 2AM)  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  1. Archivar logs activos > N días      │
│     (LOG_RETENTION_DAYS)                │
│                                         │
│  2. Mover a LOG_ARCHIVE_DIR             │
│     (data/logs_archive)                 │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  3. Eliminar logs archivados > M días   │
│     (LOG_ARCHIVE_RETENTION_DAYS)        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  4. Log de actividad                    │
│  5. Actualizar métricas                 │
└─────────────────────────────────────────┘
```

---

## 🔍 ANÁLISIS DE VIABILIDAD

### ✅ Puntos a Favor

1. **Variables ya definidas**: No hay que agregar nuevas configuraciones
2. **Estructura de logs existe**: `backend/logs/` ya está organizado
3. **Scheduler disponible**: APScheduler ya está configurado
4. **Patrón similar existe**: Los procesos programados ya funcionan

### ⚠️ Riesgos Identificados

1. **Logs en uso**: No se pueden eliminar archivos que Loguru está escribiendo
2. **Windows file locks**: En Windows, archivos abiertos no se pueden mover
3. **Concurrencia**: Múltiples procesos podrían intentar limpiar simultáneamente
4. **Pérdida de datos**: Eliminar logs necesarios para debugging

### 🎯 Mitigaciones

| Riesgo           | Mitigación                                 |
| ---------------- | ------------------------------------------ |
| Logs en uso      | Cerrar sinks temporalmente o solo archivar |
| File locks       | Usar `shutil.move` con retry               |
| Concurrencia     | Usar file lock o semáforo                  |
| Pérdida de datos | Backup antes de eliminar                   |

---

## 📊 IMPACTO EN LA APLICACIÓN

### Componentes Afectados

```
backend/
├── core/
│   ├── config.py              ✅ Ya tiene variables
│   ├── logger.py              ⚠️  Modificar para cerrar/abrir sinks
│   └── scheduler/
│       └── jobs_loader.py     ⚠️  Registrar nuevo job
│
├── apps/
│   └── platform_config/
│       ├── domain/
│       │   └── entities/
│       │       └── scheduled_process_config.py  ✅ Ya existe modelo
│       └── infrastructure/
│           └── repositories/
│               └── sql_platform_config_repository.py  ✅ Ya existe repo
│
├── services/
│   └── log_cleanup_service.py  🆕 NUEVO ARCHIVO
│
└── tasks/
    └── log_cleanup_task.py     🆕 NUEVO ARCHIVO
```

### Dependencias

| Componente | Estado                  | Acción                             |
| ---------- | ----------------------- | ---------------------------------- |
| Config     | ✅ Listo                 | Ninguna                            |
| Logger     | ⚠️ Necesita modificación | Agregar método para cerrar/reabrir |
| Scheduler  | ✅ Listo                 | Registrar job                      |
| Modelo DB  | ✅ Listo                 | Usar existente                     |

---

## 🏗️ ARQUITECTURA PROPUESTA

### Opción A: Servicio Independiente (Recomendada)

```
┌─────────────────────────────────────────┐
│         LogCleanupService               │
├─────────────────────────────────────────┤
│  + archive_old_logs(days: int)          │
│  + delete_archived_logs(days: int)      │
│  + get_disk_usage() → dict              │
│  + run_cleanup() → CleanupResult        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│            Logger (core)                │
├─────────────────────────────────────────┤
│  + close_all_sinks()                    │
│  + reopen_all_sinks()                   │
└─────────────────────────────────────────┘
```

**Ventajas**:
- ✅ Código aislado y testeable
- ✅ No modifica logger.py directamente
- ✅ Fácil de deshabilitar
- ✅ Reutilizable

### Opción B: Integración Directa

Modificar `logger.py` directamente.

**Desventajas**:
- ❌ Acoplamiento alto
- ❌ Difícil de testear
- ❌ Riesgo de romper logging existente

---

## 📝 PLAN DE IMPLEMENTACIÓN GRADUAL

### FASE 1: Preparación (30 min)

1. **Crear servicio aislado** `backend/services/log_cleanup_service.py`
2. **Implementar métodos básicos**:
   - `archive_old_logs()`
   - `delete_archived_logs()`
   - `get_disk_usage()`
3. **Crear tests unitarios**

### FASE 2: Integración con Logger (20 min)

1. **Agregar métodos a `logger.py`**:
   - `close_all_sinks()`
   - `reopen_all_sinks()`
2. **Testear que no rompe logging existente**

### FASE 3: Conexión con Scheduler (20 min)

1. **Registrar job en `jobs_loader.py`**
2. **Usar `scheduled_process_config` de la BD**
3. **Configurar cron por defecto** (`0 2 * * *`)

### FASE 4: Testing (30 min)

1. **Test unitario del servicio**
2. **Test de integración con scheduler**
3. **Test manual con cron modificado** (`* * * * *` para prueba inmediata)

### FASE 5: Activación (10 min)

1. **Habilitar en `.env`**: `AUTO_CLEANUP_ENABLED=true`
2. **Verificar logs de actividad**
3. **Monitorear por 24 horas**

---

## 🧪 PRUEBA PROPUESTA

### Para Test Inmediato

1. **Crear script de prueba**:
```python
# backend/test_cleanup_manual.py
from services.log_cleanup_service import LogCleanupService

service = LogCleanupService()
result = service.run_cleanup()
print(result)
```

2. **Modificar cron temporalmente**:
```env
CLEANUP_CRON="* * * * *"  # Ejecuta cada minuto
```

3. **Ejecutar y verificar**:
```bash
cd backend
python test_cleanup_manual.py
```

---

## 📊 ESTIMACIÓN DE ESFUERZO

| Fase               | Tiempo      | Dificultad     |
| ------------------ | ----------- | -------------- |
| Fase 1: Servicio   | 30 min      | Baja           |
| Fase 2: Logger     | 20 min      | Media          |
| Fase 3: Scheduler  | 20 min      | Baja           |
| Fase 4: Testing    | 30 min      | Baja           |
| Fase 5: Activación | 10 min      | Baja           |
| **Total**          | **110 min** | **Baja-Media** |

---

## ✅ CRITERIOS DE ÉXITO

1. ✅ Servicio aislado funciona independientemente
2. ✅ Logs se archivan correctamente
3. ✅ Logs antiguos se eliminan según configuración
4. ✅ Logging existente no se rompe
5. ✅ Scheduler ejecuta según cron configurado
6. ✅ Variables de entorno se usan correctamente

---

## 🎯 SIGUIENTE PASO

**Crear Fase 1**: Implementar `LogCleanupService` aislado con tests

---

## 🏗️ ANÁLISIS: ¿MOVER AL CORE?

### ❌ Recomendación: **NO mover al core**

| Criterio      | Core    | Services (Actual) | Veredicto  |
| ------------- | ------- | ----------------- | ---------- |
| Acoplamiento  | Alto    | Bajo              | ✅ Services |
| Testeabilidad | Difícil | Fácil             | ✅ Services |
| Mantenimiento | Difícil | Fácil             | ✅ Services |
| Reutilización | Baja    | Alta              | ✅ Services |
| Principio SRP | Violado | Cumplido          | ✅ Services |

**Conclusión**: Mantener en `backend/services/` es la decisión correcta.

---

## 📊 ARQUITECTURA ACTUAL (Implementada)

```
backend/services/
├── log_cleanup_service.py          # Servicio principal
├── models/
│   ├── __init__.py
│   └── cleanup_history.py          # Historial de auditoría
├── tests/
│   ├── test_log_cleanup_service.py     # 18 tests unitarios
│   └── test_log_cleanup_integration.py # 1 test integración
├── README_LOG_CLEANUP.md
└── PLAN_PRUEBA_SCHEDULER.md

backend/core/scheduler/
├── log_cleanup_jobs.py             # Job para scheduler
├── jobs_loader.py                  # Registro de jobs
└── tests/
    ├── test_log_cleanup_scheduler.py           # 5 tests
    └── test_log_cleanup_scheduler_integration.py # 3 tests

backend/core/services/
└── scheduler_service.py            # Control del job

backend/core/routes/
└── scheduler_routes.py             # Endpoints FastAPI
```

---

## 🔄 FLUJO DE EJECUCIÓN

```
┌─────────────────────────────────────────────────────────┐
│           scheduled_process_config (BD)                 │
│  process_name: PROCESS_LOG_CLEANUP                      │
│  cron_expression: 0 3 * * *                            │
│  enabled: true                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│            jobs_loader.py                               │
│  Lee configuración desde BD                             │
│  Registra job en APScheduler                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         log_cleanup_jobs.py                             │
│  create_log_cleanup_job()                               │
│  └── job_function()                                     │
│      ├── LogCleanupService().run_cleanup()              │
│      └── CleanupHistory.add_entry()                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│       LogCleanupService                                 │
│  1. Analiza logs_dir                                    │
│  2. Archiva logs > retention_days                       │
│  3. Elimina archivados > archive_retention_days         │
│  4. Retorna CleanupResult                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         CleanupHistory (JSON)                           │
│  Registra timestamp, archivos, espacio, errores         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 COMANDOS PARA PROBAR

### Ejecutar tests
```bash
cd backend && python -m pytest backend/services/tests/ backend/core/scheduler/tests/ -v
```

### Ejecutar limpieza manual
```python
from services.log_cleanup_service import LogCleanupService
service = LogCleanupService()
result = service.run_cleanup()
print(f"Archivados: {result.archived_files}, Liberado: {result.freed_space_mb:.2f} MB")
```

### Ejecutar seeder
```bash
python backend/manage.py sql seed PlatformConfigSeeder
```

### Probar endpoints (con servidor)
```bash
# Ver estado
curl http://localhost:8000/scheduler/log-cleanup/status

# Ejecutar inmediatamente
curl -X POST http://localhost:8000/scheduler/log-cleanup/run-now

# Pausar
curl -X POST http://localhost:8000/scheduler/log-cleanup/pause

# Reanudar
curl -X POST http://localhost:8000/scheduler/log-cleanup/resume
```

---

## 📈 PRÓXIMAS MEJORAS PROPUESTAS

| Mejora            | Prioridad | Descripción                       |
| ----------------- | --------- | --------------------------------- |
| Limpieza por peso | Alta      | Ejecutar solo si logs > X MB      |
| Dashboard         | Media     | Panel de control de limpiezas     |
| Alertas           | Media     | Notificar cuando se libere > X MB |
| Backup automático | Baja      | Backup antes de eliminar          |

---

*Documento actualizado: 25 de marzo de 2026*


