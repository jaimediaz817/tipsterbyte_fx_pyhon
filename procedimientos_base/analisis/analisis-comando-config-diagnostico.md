# Análisis: Comando de Diagnóstico de Configuración

## Diagnóstico Actual

### Problema Identificado
El proyecto tiene **múltiples variables de configuración** dispersas que afectan el comportamiento del sistema, pero **no existe un punto centralizado** para visualizar su estado actual.

### Variables Críticas Identificadas

#### 1. Variables de Logging (Implementadas)
| Variable                      | Ubicación | Default | Controla                                 |
| ----------------------------- | --------- | ------- | ---------------------------------------- |
| `PROCESS_RUN_LOGGING_ENABLED` | config.py | `true`  | Tablas `process_run` y `process_run_log` |
| `FILE_LOGGING_ENABLED`        | config.py | `true`  | Archivos en `backend/logs/`              |

#### 2. Variables de Entorno
| Variable    | Ubicación | Default       | Controla             |
| ----------- | --------- | ------------- | -------------------- |
| `ENV`       | config.py | `development` | Entorno de ejecución |
| `DEBUG`     | config.py | `True`        | Modo debug           |
| `LOG_LEVEL` | config.py | `DEBUG`       | Nivel de logs        |

#### 3. Variables de Base de Datos
| Variable       | Ubicación | Default            | Controla            |
| -------------- | --------- | ------------------ | ------------------- |
| `DATABASE_URL` | config.py | `postgresql://...` | Conexión PostgreSQL |
| `MONGO_URI`    | config.py | `mongodb://...`    | Conexión MongoDB    |

#### 4. Variables de Concurrencia
| Variable                 | Ubicación | Default | Controla               |
| ------------------------ | --------- | ------- | ---------------------- |
| `MAX_CONCURRENT_CLIENTS` | config.py | `5`     | Concurrencia de robots |

---

## Plan de Implementación

### Paso 1: Crear Comando `config` en `project_cli.py`

**Ubicación**: `backend/commands/project_cli.py`

```python
@app.command(name="config", help="Muestra el estado actual de la configuración.")
def project_config():
    """Muestra diagnóstico de todas las variables de configuración."""
    from core.config import settings
    
    # ... lógica de visualización
```

### Paso 2: Estructura del Comando

```
python manage.py project config
```

**Salida esperada**:
```
════════════════════════════════════════════════════════════
        CONFIGURACIÓN ACTUAL - TipsterByte FX
════════════════════════════════════════════════════════════

── ENTORNO ────────────────────────────────────────────────
  ENV                          = development
  DEBUG                        = True

── LOGGING ────────────────────────────────────────────────
  LOG_LEVEL                    = DEBUG
  PROCESS_RUN_LOGGING_ENABLED  = True    [ESCRIBE EN BD]
  FILE_LOGGING_ENABLED         = True    [ESCRIBE EN ARCHIVOS]

── BASE DE DATOS ─────────────────────────────────────────
  DATABASE_URL                 = postgresql://postgres:***
  MONGO_URI                    = mongodb://tipster_admin:***

── CONCURRENCIA ──────────────────────────────────────────
  MAX_CONCURRENT_CLIENTS       = 5

── LOGS ──────────────────────────────────────────────────
  LOG_RETENTION_DAYS           = 3
  LOG_ARCHIVE_RETENTION_DAYS   = 30
  AUTO_CLEANUP_ENABLED         = False

════════════════════════════════════════════════════════════
```

### Paso 3: Formato Visual con Colores

Usar `typer.secho()` para colores:
- **Verde**: Valores que indican comportamiento activo
- **Amarillo**: Valores por defecto o advertencias
- **Rojo**: Valores críticos o deshabilitados
- **Cyan**: Información general

```python
def print_config_value(key: str, value: any, description: str = "", status: str = "info"):
    """Imprime un valor de configuración con formato."""
    colors = {
        "ok": typer.colors.GREEN,
        "warn": typer.colors.YELLOW,
        "error": typer.colors.RED,
        "info": typer.colors.CYAN,
    }
    
    color = colors.get(status, typer.colors.WHITE)
    
    # Formatear valor
    if isinstance(value, bool):
        value_str = "True" if value else "False"
        status_icon = "[ACTIVO]" if value else "[INACTIVO]"
    elif isinstance(value, str) and len(value) > 40:
        value_str = value[:37] + "***"
    else:
        value_str = str(value)
        status_icon = ""
    
    typer.echo(f"  {key:<35} = ", nl=False)
    typer.secho(f"{value_str}", fg=color, bold=True, nl=False)
    if status_icon:
        typer.secho(f" {status_icon}", fg=color)
    else:
        typer.echo()
```

### Paso 4: Variables Sin Valor o Por Defecto

Detectar y resaltar:
```python
def is_default_value(key: str, value: any) -> bool:
    """Detecta si un valor es el default."""
    defaults = {
        "ENV": "development",
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "MAX_CONCURRENT_CLIENTS": 5,
        "PROCESS_RUN_LOGGING_ENABLED": True,
        "FILE_LOGGING_ENABLED": True,
    }
    return defaults.get(key) == value
```

### Paso 5: Registrar en `manage.py`

```python
# En manage.py, el comando ya está registrado via project_cli.app
# Solo necesitamos asegurar que el comando 'config' exista en project_cli.py
```

---

## Implicaciones

### 1. Impacto en Código Existente
- ✅ **No rompe nada**: Es un comando de solo lectura
- ✅ **No modifica configuración**: Solo muestra valores
- ✅ **No afecta tests**: No interfiere con fixtures

### 2. Dependencias
- `typer` (ya instalado)
- `core.config.settings` (ya existe)
- `loguru` (ya instalado)

### 3. Archivos a Modificar
| Archivo                           | Acción                  | Impacto |
| --------------------------------- | ----------------------- | ------- |
| `backend/commands/project_cli.py` | Añadir comando `config` | Bajo    |
| `backend/manage.py`               | No requiere cambios     | Ninguno |

### 4. Tests
- No se requieren tests nuevos (comando de solo lectura)
- Se puede verificar manualmente con `python manage.py project config`

---

## Variables Adicionales a Incluir

### Variables de Scheduler
| Variable                                            | Default | Controla                     |
| --------------------------------------------------- | ------- | ---------------------------- |
| `SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS` | N/A     | Código del proceso principal |

### Variables de Selenium
| Variable           | Default                        | Controla        |
| ------------------ | ------------------------------ | --------------- |
| `SELENIUM_HUB_URL` | `http://localhost:4444/wd/hub` | Hub de Selenium |

### Variables de Logs Adicionales
| Variable          | Default             | Controla               |
| ----------------- | ------------------- | ---------------------- |
| `LOG_ARCHIVE_DIR` | `data/logs_archive` | Directorio de archivos |

---

## Ejemplo de Implementación

```python
@app.command(name="config", help="Muestra el estado actual de la configuración.")
def project_config():
    """Muestra diagnóstico completo de la configuración."""
    from core.config import settings
    
    typer.echo("\n" + "═" * 60)
    typer.secho("        CONFIGURACIÓN ACTUAL - TipsterByte FX", fg=typer.colors.CYAN, bold=True)
    typer.echo("═" * 60)
    
    # ── ENTORNO ──
    typer.echo("\n── ENTORNO " + "─" * 49)
    _print_setting("ENV", settings.ENV, "info")
    _print_setting("DEBUG", settings.DEBUG, "ok" if settings.DEBUG else "warn")
    
    # ── LOGGING ──
    typer.echo("\n── LOGGING " + "─" * 50)
    _print_setting("LOG_LEVEL", settings.LOG_LEVEL, "info")
    _print_setting(
        "PROCESS_RUN_LOGGING_ENABLED", 
        settings.PROCESS_RUN_LOGGING_ENABLED,
        "ok" if settings.PROCESS_RUN_LOGGING_ENABLED else "error"
    )
    _print_setting(
        "FILE_LOGGING_ENABLED",
        settings.FILE_LOGGING_ENABLED,
        "ok" if settings.FILE_LOGGING_ENABLED else "error"
    )
    
    # ── BASE DE DATOS ──
    typer.echo("\n── BASE DE DATOS " + "─" * 44)
    _print_setting("DATABASE_URL", settings.DATABASE_URL, "info", mask=True)
    _print_setting("MONGO_URI", settings.MONGO_URI, "info", mask=True)
    
    # ── CONCURRENCIA ──
    typer.echo("\n── CONCURRENCIA " + "─" * 45)
    _print_setting("MAX_CONCURRENT_CLIENTS", settings.MAX_CONCURRENT_CLIENTS, "info")
    
    # ── LOGS ──
    typer.echo("\n── LOGS " + "─" * 53)
    _print_setting("LOG_RETENTION_DAYS", settings.LOG_RETENTION_DAYS, "info")
    _print_setting("LOG_ARCHIVE_RETENTION_DAYS", settings.LOG_ARCHIVE_RETENTION_DAYS, "info")
    _print_setting("AUTO_CLEANUP_ENABLED", settings.AUTO_CLEANUP_ENABLED, "warn")
    
    typer.echo("\n" + "═" * 60)


def _print_setting(key: str, value: any, status: str = "info", mask: bool = False):
    """Imprime una configuración con formato."""
    colors = {
        "ok": typer.colors.GREEN,
        "warn": typer.colors.YELLOW,
        "error": typer.colors.RED,
        "info": typer.colors.CYAN,
    }
    
    color = colors.get(status, typer.colors.WHITE)
    
    # Formatear valor
    if mask and isinstance(value, str):
        if "://" in value:
            # Enmascarar credenciales
            parts = value.split("://")
            if len(parts) > 1:
                value_str = f"{parts[0]}://***"
        else:
            value_str = value[:20] + "***" if len(value) > 20 else value
    elif isinstance(value, bool):
        value_str = "True" if value else "False"
    else:
        value_str = str(value)
    
    # Indicador de estado
    status_indicator = ""
    if isinstance(value, bool):
        status_indicator = " [ACTIVO]" if value else " [INACTIVO]"
    
    typer.echo(f"  {key:<35} = ", nl=False)
    typer.secho(f"{value_str}", fg=color, bold=True, nl=False)
    if status_indicator:
        typer.secho(status_indicator, fg=color)
    else:
        typer.echo()
```

---

## Resumen de Implementación

### Archivo a Modificar
- `backend/commands/project_cli.py` → Añadir comando `config`

### Tiempo Estimado
- **Implementación**: 30 minutos
- **Testing manual**: 10 minutos
- **Total**: 40 minutos

### Riesgos
- **Ninguno**: Comando de solo lectura, no modifica nada

### Beneficios
- ✅ Punto centralizado de diagnóstico
- ✅ Visualización clara del estado
- ✅ Detección rápida de configuraciones incorrectas
- ✅ Facilita debugging
- ✅ Documentación viva del sistema

---

*Documento generado: Análisis de comando de diagnóstico de configuración*