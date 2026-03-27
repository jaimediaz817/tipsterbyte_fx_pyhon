# Plan de Prueba del Scheduler para Log Cleanup

## 📋 Resumen

El job de limpieza de logs está completamente integrado con el scheduler. Aquí está el plan para probarlo.

---

## 🏗️ Arquitectura Implementada

```
┌─────────────────────────────────────────────────────────┐
│                    APScheduler                          │
│                 (AsyncIOScheduler)                      │
├─────────────────────────────────────────────────────────┤
│ jobs_loader.py                                          │
│   └── ALL_PROCESS_MAPS = {                              │
│         **PROCESS_MAP_LEAGUES_MANAGER,                  │
│         **LOG_CLEANUP_PROCESS_MAP,  ← NUEVO            │
│       }                                                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│          log_cleanup_jobs.py                            │
│   └── create_log_cleanup_job()                          │
│       └── LogCleanupService().run_cleanup()             │
│       └── CleanupHistory.add_entry()                    │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Tests Completados (24/24)

### Tests Unitarios (18)
- `test_default_values`
- `test_to_dict`
- `test_str_success`
- `test_str_error`
- `test_initialization`
- `test_get_disk_usage_empty`
- `test_get_disk_usage_with_files`
- `test_get_files_older_than_empty`
- `test_get_files_older_than_with_files`
- `test_get_files_older_than_nonexistent_dir`
- `test_archive_old_logs_empty`
- `test_archive_old_logs_with_files`
- `test_archive_old_logs_skips_recent`
- `test_delete_archived_logs_empty`
- `test_delete_archived_logs_with_files`
- `test_delete_archived_logs_skips_recent`
- `test_run_cleanup_full_workflow`
- `test_handles_file_disappearing`

### Test de Integración (1)
- `test_simulate_years_of_logs` (50 archivos, 2 años, auditoría)

### Tests de Scheduler (5)
- `test_log_cleanup_job_exists_in_process_map`
- `test_log_cleanup_job_is_callable`
- `test_log_cleanup_job_executes_successfully`
- `test_log_cleanup_job_handles_errors_gracefully`
- `test_cron_expression_is_correct`

---

## 🧪 Cómo Probar el Scheduler

### Opción 1: Ejecutar tests automáticamente

```bash
# Todos los tests
cd backend && python -m pytest backend/services/tests/ backend/core/scheduler/tests/test_log_cleanup_scheduler.py -v

# Solo tests de scheduler
python -m pytest backend/core/scheduler/tests/test_log_cleanup_scheduler.py -v
```

### Opción 2: Ejecutar limpieza manual (sin scheduler)

```python
# En un script de Python
from services.log_cleanup_service import LogCleanupService

service = LogCleanupService()
result = service.run_cleanup()

print(f"Archivados: {result.archived_files}")
print(f"Eliminados: {result.deleted_files}")
print(f"Espacio liberado: {result.freed_space_mb:.2f} MB")
```

### Opción 3: Probar el job directamente

```python
# En un script de Python
from core.scheduler.log_cleanup_jobs import LOG_CLEANUP_PROCESS_MAP

# Obtener el job
job = LOG_CLEANUP_PROCESS_MAP["PROCESS_LOG_CLEANUP"]

# Ejecutar el job
job()

# Verificar historial
from services.models.cleanup_history import get_cleanup_history
history = get_cleanup_history()
print(history.get_stats())
```

### Opción 4: Probar con scheduler real (requiere BD)

```bash
# 1. Ejecutar seeder para crear el job en BD
cd backend && python manage.py sql seed PlatformConfigSeeder

# 2. O para forzar actualización si ya existe
cd backend && python manage.py sql seed PlatformConfigSeeder --update

# 3. Iniciar el scheduler
python manage.py runserver

# 4. Verificar en logs que el job se registra
# Deberías ver: "✅ Trabajo 'PROCESS_LOG_CLEANUP' programado con cron '0 3 * * *'"

# 5. Esperar a las 3:00 AM (o modificar cron temporalmente para pruebas)
# 6. Verificar que se ejecuta la limpieza
```

---

## 📊 Configuración del Job

| Parámetro         | Valor                            | Descripción                  |
| ----------------- | -------------------------------- | ---------------------------- |
| `process_name`    | `PROCESS_LOG_CLEANUP`            | Nombre del proceso           |
| `cron_expression` | `0 3 * * *`                      | Todos los días a las 3:00 AM |
| `enabled`         | `True`                           | Habilitado por defecto       |
| `description`     | "Limpieza automática de logs..." | Descripción del job          |

---

## 📁 Estructura de Archivos

```
backend/
├── services/
│   ├── log_cleanup_service.py              # Servicio principal
│   ├── models/
│   │   ├── __init__.py
│   │   └── cleanup_history.py              # Modelo de historial
│   ├── tests/
│   │   ├── test_log_cleanup_service.py     # 18 tests unitarios
│   │   └── test_log_cleanup_integration.py # 1 test de integración
│   └── README_LOG_CLEANUP.md               # Manual de uso
├── core/
│   ├── scheduler/
│   │   ├── log_cleanup_jobs.py             # Job para scheduler
│   │   ├── jobs_loader.py                  # Registro de jobs
│   │   └── tests/
│   │       └── test_log_cleanup_scheduler.py # 5 tests de scheduler
│   └── logging/
│       ├── __init__.py
│       └── log_profile.py                  # Perfiles de logging (POO)
└── scripts/
    └── db/
        └── seeders/
            └── sql/
                └── platform_config_seeder.py # Seeder actualizado
```

---

## 🔍 Verificar que Todo Funciona

### Comando completo

```bash
cd backend && python -m pytest backend/services/tests/ backend/core/scheduler/tests/test_log_cleanup_scheduler.py -v --tb=short
```

### Resultado esperado

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2
collected 24 items

backend/services/tests/test_log_cleanup_integration.py::TestLogCleanupIntegration::test_simulate_years_of_logs PASSED
backend/services/tests/test_log_cleanup_service.py::TestCleanupResult::test_default_values PASSED
backend/services/tests/test_log_cleanup_service.py::TestCleanupResult::test_to_dict PASSED
...
backend/core/scheduler/tests/test_log_cleanup_scheduler.py::TestLogCleanupScheduler::test_cron_expression_is_correct PASSED

============================= 24 passed in 0.80s ==============================
```

---

## 🚀 Próximos Pasos (Fase 5)

1. **Monitoreo**: Agregar métricas de rendimiento
2. **Alertas**: Notificar cuando se libere más de X MB
3. **Dashboard**: Crear panel de control de limpiezas
4. **Optimización**: Mejorar rendimiento con archivos grandes

---

## 📞 Soporte

Si algo falla:
1. Revisar logs en `backend/logs/`
2. Verificar historial en `backend/logs/cleanup_history.json`
3. Ejecutar tests unitarios: `python -m pytest backend/services/tests/test_log_cleanup_service.py -v`
4. Ejecutar tests de scheduler: `python -m pytest backend/core/scheduler/tests/test_log_cleanup_scheduler.py -v`