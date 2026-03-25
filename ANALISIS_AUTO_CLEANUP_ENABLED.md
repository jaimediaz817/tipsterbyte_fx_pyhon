# 🔍 ANÁLISIS: Variable AUTO_CLEANUP_ENABLED

**Fecha**: 25 de marzo de 2026  
**Variable**: `AUTO_CLEANUP_ENABLED`  
**Tipo**: `bool`  
**Default**: `False`

---

## 📋 DEFINICIÓN

```python
AUTO_CLEANUP_ENABLED: bool = Field(
    False, description="Habilitar limpieza automática de logs"
)
```

**Ubicación**: `backend/core/config.py`

---

## 🎯 ¿QUÉ HACE?

Esta variable controla si el sistema ejecuta **limpieza automática de logs antiguos** de manera programada.

### Comportamiento:

| Valor   | Comportamiento                              |
| ------- | ------------------------------------------- |
| `False` | ❌ NO limpia logs automáticamente            |
| `True`  | ✅ SÍ limpia logs automáticamente según cron |

---

## 📊 VARIABLES RELACIONADAS

```python
LOG_RETENTION_DAYS: int = 3
# Días que se mantienen logs activos antes de archivar

LOG_ARCHIVE_RETENTION_DAYS: int = 30  
# Días que se mantienen logs archivados antes de eliminar

LOG_ARCHIVE_DIR: str = "data/logs_archive"
# Directorio donde se guardan logs archivados

AUTO_CLEANUP_ENABLED: bool = False
# Habilita la limpieza automática

CLEANUP_CRON: str = "0 2 * * *"  # Solo en .env.prod
# Expresión cron para programar limpieza (diario a las 2 AM)
```

---

## 🔍 CONFIGURACIÓN POR ENTORNO

### Desarrollo (`.env`)
```env
AUTO_CLEANUP_ENABLED=false
LOG_RETENTION_DAYS=3
LOG_ARCHIVE_RETENTION_DAYS=30
```
**Comportamiento**: Logs se acumulan, NO se limpian automáticamente

### Desarrollo (`.env.dev`)
```env
AUTO_CLEANUP_ENABLED=false
LOG_ARCHIVE_DIR=/var/log/tipsterbyte/archive
```
**Comportamiento**: Similar a desarrollo, sin limpieza

### Producción (`.env.prod`)
```env
AUTO_CLEANUP_ENABLED=true
CLEANUP_CRON="0 2 * * *"
```
**Comportamiento**: Limpieza automática diaria a las 2:00 AM

---

## ⚙️ FLUJO DE LIMPIEZA

```
┌─────────────────────────────────────────┐
│   AUTO_CLEANUP_ENABLED = true           │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Cron job ejecuta diario a las 2 AM    │
│   (CLEANUP_CRON = "0 2 * * *")         │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   1. Archivar logs activos > 3 días     │
│      (LOG_RETENTION_DAYS)               │
│                                         │
│   2. Mover a LOG_ARCHIVE_DIR            │
│      (data/logs_archive)                │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   3. Eliminar logs archivados > 30 días │
│      (LOG_ARCHIVE_RETENTION_DAYS)       │
└─────────────────────────────────────────┘
```

---

## ⚠️ ESTADO ACTUAL

Según el comando `project config`:

```
── LOGS ────────────────────────────────────────
  LOG_RETENTION_DAYS                  = 3
  LOG_ARCHIVE_RETENTION_DAYS          = 30
  LOG_ARCHIVE_DIR                     = data/logs_archive
  AUTO_CLEANUP_ENABLED                = False [INACTIVO]
```

**Estado**: 🟡 **INACTIVO** en desarrollo

---

## 💡 RECOMENDACIONES

### Para Desarrollo:
```
AUTO_CLEANUP_ENABLED=false  ✅ CORRECTO
```
**Razón**: 
- Desarrollo genera muchos logs de debug
- Útil mantenerlos para troubleshooting
- No hay riesgo de llenar disco en local

### Para Producción:
```
AUTO_CLEANUP_ENABLED=true   ✅ CORRECTO
CLEANUP_CRON="0 2 * * *"   ✅ CORRECTO
```
**Razón**:
- Producción genera logs continuamente
- Sin limpieza → disco se llena
- Limpieza diaria a las 2 AM (bajo tráfico)

---

## 🎯 CONCLUSIÓN

| Aspecto    | Estado      | Recomendación    |
| ---------- | ----------- | ---------------- |
| Desarrollo | `False`     | ✅ Mantener así   |
| Producción | `True`      | ✅ Correcto       |
| Cron job   | "0 2 * * *" | ✅ Horario óptimo |
| Retención  | 3/30 días   | ✅ Balanceado     |

**Veredicto**: La configuración actual es **CORRECTA** para cada entorno.

---

## 📚 REFERENCIAS

- Archivo: `backend/core/config.py`
- Comando diagnóstico: `python manage.py project config`
- Documentación: `procedimientos_base/ejemplos-configuracion-logging.md`

---

*Análisis generado por arquitecto de software*