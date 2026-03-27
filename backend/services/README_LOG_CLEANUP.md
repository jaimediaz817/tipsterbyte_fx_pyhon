# Log Cleanup Service - Manual Rápido

## 📁 Estructura del Servicio

```
backend/services/
├── log_cleanup_service.py          # Servicio principal
├── models/
│   ├── __init__.py
│   └── cleanup_history.py          # Modelo de historial (auditoría)
└── tests/
    ├── test_log_cleanup_service.py      # Tests unitarios (18)
    └── test_log_cleanup_integration.py  # Test de integración (1)
```

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
cd backend && python -m pytest backend/services/tests/ -v

# Solo tests unitarios
python -m pytest backend/services/tests/test_log_cleanup_service.py -v

# Test de integración (simula 2 años de logs)
python -m pytest backend/services/tests/test_log_cleanup_integration.py -v -s
```

---

## 🚀 Uso Manual

### Ejecutar limpieza completa

```python
from services.log_cleanup_service import LogCleanupService

service = LogCleanupService()
result = service.run_cleanup()

print(f"Archivados: {result.archived_files}")
print(f"Eliminados: {result.deleted_files}")
print(f"Espacio liberado: {result.freed_space_mb:.2f} MB")
```

### Solo archivar logs antiguos

```python
from services.log_cleanup_service import LogCleanupService

service = LogCleanupService(retention_days=3)
result = service.archive_old_logs()

print(f"Archivados: {result.archived_files} archivos")
```

### Ver historial de auditoría

```python
from services.models.cleanup_history import get_cleanup_history

history = get_cleanup_history()
stats = history.get_stats()

print(f"Total limpiezas: {stats['total_cleanups']}")
print(f"Total archivos: {stats['total_files_processed']}")
print(f"Total liberado: {stats['total_freed_mb']} MB")
```

---

## ⚙️ Configuración

### Variables del servicio

| Variable                 | Default                               | Descripción                |
| ------------------------ | ------------------------------------- | -------------------------- |
| `logs_dir`               | `LOGS_ROOT`                           | Directorio de logs activos |
| `archive_dir`            | `settings.LOG_ARCHIVE_DIR`            | Directorio de archivo      |
| `retention_days`         | `settings.LOG_RETENTION_DAYS`         | Días para archivar         |
| `archive_retention_days` | `settings.LOG_ARCHIVE_RETENTION_DAYS` | Días para eliminar         |

### Ejemplo con configuración personalizada

```python
from pathlib import Path
from services.log_cleanup_service import LogCleanupService

service = LogCleanupService(
    logs_dir=Path("/custom/logs"),
    archive_dir=Path("/custom/archive"),
    retention_days=7,
    archive_retention_days=60,
)
```

---

## 📊 Historial de Auditoría

El historial se guarda en `backend/logs/cleanup_history.json` y contiene:

```json
{
  "last_updated": "2026-03-25T16:31:36.627698",
  "total_entries": 1,
  "entries": [
    {
      "timestamp": "2026-03-25T16:31:36.627698",
      "profile_name": "integration_test",
      "action": "archive",
      "files_count": 50,
      "freed_space_mb": 11.35,
      "files_processed": ["app_0000.log", "app_0001.log", "..."],
      "errors": [],
      "duration_seconds": 0.012
    }
  ]
}
```

---

## 🔧 Integración con Scheduler (Fase 4)

### 1. Crear job de limpieza

```python
# backend/core/scheduler/log_cleanup_jobs.py
from services.log_cleanup_service import LogCleanupService
from loguru import logger

def create_log_cleanup_job():
    def job_function():
        try:
            logger.info("Iniciando limpieza programada de logs...")
            service = LogCleanupService()
            result = service.run_cleanup()
            
            if result.success:
                logger.success(
                    f"Limpieza completada: "
                    f"{result.archived_files} archivados, "
                    f"{result.deleted_files} eliminados, "
                    f"{result.freed_space_mb:.2f} MB liberados"
                )
            else:
                logger.warning(f"Limpieza completada con errores: {result.errors}")
        except Exception as e:
            logger.exception(f"Error en limpieza de logs: {e}")
    
    return job_function

LOG_CLEANUP_PROCESS_MAP = {
    "PROCESS_LOG_CLEANUP": create_log_cleanup_job(),
}
```

### 2. Agregar código de proceso

```python
# backend/shared/constants/process/process_codes.py
PROCESS_LOG_CLEANUP = "PROCESS_LOG_CLEANUP"
```

### 3. Registrar en scheduler

```python
# backend/core/scheduler/jobs_loader.py
from core.scheduler.log_cleanup_jobs import LOG_CLEANUP_PROCESS_MAP

ALL_PROCESS_MAPS = {
    **PROCESS_MAP_LEAGUES_MANAGER,
    **LOG_CLEANUP_PROCESS_MAP,
}
```

### 4. Crear seeder en BD

```bash
# Ejecutar seeder para crear el job en BD
cd backend && python manage.py sql seed PlatformConfigSeeder

# O para forzar actualización si ya existe
cd backend && python manage.py sql seed PlatformConfigSeeder --update
```

---

## 📝 Migración (si se necesita tabla SQL)

Si se quiere migrar el historial de JSON a SQL:

```bash
# Crear migración
cd backend && python manage.py migrate --app services

# Aplicar migración
python manage.py migrate
```

---

## 🎯 Resumen de Comandos

```bash
# Ejecutar tests
python -m pytest backend/services/tests/ -v

# Ejecutar limpieza manual
python -c "from services.log_cleanup_service import LogCleanupService; LogCleanupService().run_cleanup()"

# Ver historial
python -c "from services.models.cleanup_history import get_cleanup_history; print(get_cleanup_history().get_stats())"