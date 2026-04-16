# Ejemplos de Configuración de Logging

## Variables de Control

| Variable                      | Controla                                       | Default                  |
| ----------------------------- | ---------------------------------------------- | ------------------------ |
| `PROCESS_RUN_LOGGING_ENABLED` | Tablas `process_run` y `process_run_log` en BD | `true`                   |
| `FILE_LOGGING_ENABLED`        | Archivos de logs en `backend/logs/`            | `true`                   |
| Consola (stdout)              | SIEMPRE activa                                 | No se puede deshabilitar |

---

## Escenario 1: Escribe en BD y en Archivo (Default)

**Configuración en `.env`**:
```env
PROCESS_RUN_LOGGING_ENABLED=true
FILE_LOGGING_ENABLED=true
```

**Comportamiento**:
- ✅ Consola: Muestra logs
- ✅ BD: Escribe en `process_run` y `process_run_log`
- ✅ Archivos: Escribe en `backend/logs/*.log`

**Uso**: Producción y desarrollo normal

---

## Escenario 2: NO escribe en BD, PERO SÍ en Archivo

**Configuración en `.env`**:
```env
PROCESS_RUN_LOGGING_ENABLED=false
FILE_LOGGING_ENABLED=true
```

**Comportamiento**:
- ✅ Consola: Muestra logs
- ❌ BD: NO escribe en tablas (usa NoOpProcessRunRepository)
- ✅ Archivos: Escribe en `backend/logs/*.log`

**Uso**: Desarrollo cuando no quieres contaminar BD pero necesitas trazabilidad en archivos

---

## Escenario 3: NO escribe en BD, NO escribe en Archivo

**Configuración en `.env`**:
```env
PROCESS_RUN_LOGGING_ENABLED=false
FILE_LOGGING_ENABLED=false
```

**Comportamiento**:
- ✅ Consola: Muestra logs
- ❌ BD: NO escribe en tablas (usa NoOpProcessRunRepository)
- ❌ Archivos: NO escribe en archivos

**Uso**: Tests unitarios (configuración automática via fixtures)

---

## Escenario 4: Escribe en BD, NO escribe en Archivo

**Configuración en `.env`**:
```env
PROCESS_RUN_LOGGING_ENABLED=true
FILE_LOGGING_ENABLED=false
```

**Comportamiento**:
- ✅ Consola: Muestra logs
- ✅ BD: Escribe en `process_run` y `process_run_log`
- ❌ Archivos: NO escribe en archivos

**Uso**: Producción donde solo necesitas BD y consola (ahorro de espacio en disco)

---

## Ejemplos de Uso por Entorno

### Producción (Default)
```env
# backend/.env
PROCESS_RUN_LOGGING_ENABLED=true
FILE_LOGGING_ENABLED=true
```
**Resultado**: Todo habilitado, máxima trazabilidad

### Desarrollo sin contaminar BD
```env
# backend/.env
PROCESS_RUN_LOGGING_ENABLED=false
FILE_LOGGING_ENABLED=true
```
**Resultado**: Solo consola y archivos, BD limpia

### Desarrollo mínimo (solo consola)
```env
# backend/.env
PROCESS_RUN_LOGGING_ENABLED=false
FILE_LOGGING_ENABLED=false
```
**Resultado**: Solo consola, sin persistencia

### Producción optimizada (solo BD)
```env
# backend/.env
PROCESS_RUN_LOGGING_ENABLED=true
FILE_LOGGING_ENABLED=false
```
**Resultado**: BD y consola, sin archivos (ahorro de espacio)

---

## Ejemplos de Uso Programático

### Ejemplo 1: Forzar NoOp en código
```python
from shared.repositories.scheduler_repos import ProcessRunRepositoryFactory

# Forzar que NO escriba en BD (independiente de .env)
repo = ProcessRunRepositoryFactory.get_repository(
    db=session,
    use_real_db=False  # Forzar NoOp
)
```

### Ejemplo 2: Verificar configuración actual
```python
from core.config import settings

print(f"BD Logging: {settings.PROCESS_RUN_LOGGING_ENABLED}")
print(f"File Logging: {settings.FILE_LOGGING_ENABLED}")
print(f"Log Level: {settings.LOG_LEVEL}")
```

### Ejemplo 3: Cambiar en runtime (solo para esa sesión)
```python
import os

# Temporalmente deshabilitar BD logging
os.environ["PROCESS_RUN_LOGGING_ENABLED"] = "false"

# Tu código aquí...

# Restaurar
os.environ.pop("PROCESS_RUN_LOGGING_ENABLED", None)
```

---

## Verificación de Estado

### Verificar configuración actual
```bash
cd backend
python -c "
from core.config import settings
print(f'PROCESS_RUN_LOGGING_ENABLED: {settings.PROCESS_RUN_LOGGING_ENABLED}')
print(f'FILE_LOGGING_ENABLED: {settings.FILE_LOGGING_ENABLED}')
"
```

### Verificar archivos de logs
```bash
# Ver si se están creando archivos
ls -la backend/logs/

# Ver contenido de un log
tail -f backend/logs/general_app.log
```

### Verificar registros en BD
```bash
cd backend
python scripts/check_process_run_tables.py
```

---

## Matriz de Decisión Rápida

| Quiero...               | PROCESS_RUN_LOGGING_ENABLED | FILE_LOGGING_ENABLED |
| ----------------------- | --------------------------- | -------------------- |
| Todo habilitado         | `true`                      | `true`               |
| Solo BD + consola       | `true`                      | `false`              |
| Solo archivos + consola | `false`                     | `true`               |
| Solo consola            | `false`                     | `false`              |
| Tests (automático)      | `false` (fixture)           | `false` (fixture)    |

---

## Notas Importantes

1. **Consola siempre activa**: No se puede deshabilitar la consola sin modificar el código fuente
2. **Tests automáticos**: Los fixtures `disable_process_run_logging` y `disable_file_logging` deshabilitan automáticamente ambos en tests
3. **Orden de carga**: Las variables se leen al iniciar la aplicación, cambios en `.env` requieren reinicio
4. **Variables de entorno**: Tienen prioridad sobre `.env` si están definidas en el sistema

---

*Documento generado: Ejemplos de configuración de logging*