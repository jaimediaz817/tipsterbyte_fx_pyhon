# DIAGNÓSTICO COMPLETO: IMPACTO EN BASE DE DATOS Y TAREAS PROGRAMADAS

**Fecha**: 2026-03-30  
**Estado**: ANÁLISIS COMPLETO  
**Objetivo**: Evaluar impacto de artefactos en estructura de BD y scheduler

---

## 1. ANÁLISIS DEL INICIO DEL SERVIDOR (main_init_web_server.py)

### 1.1 Operaciones que se ejecutan al iniciar

```python
# Secuencia de inicio:
1. load_key()                    # Validar clave Fernet
2. start_scheduler()             # Iniciar scheduler de procesos
3. create_db_and_tables()        # ⚠️ CREAR TABLAS SQL
4. _display_available_routes()   # Mostrar rutas disponibles
```

### 1.2 ⚠️ PROBLEMA CRÍTICO IDENTIFICADO

**`create_db_and_tables()` ejecuta**:
```python
Base.metadata.create_all(bind=engine)
```

**¿Qué hace esto?**
- Intenta crear **TODAS las tablas** registradas en SQLAlchemy
- Si las tablas ya existen, SQLAlchemy las ignora (no falla)
- **PERO**: No verifica si hay datos existentes
- **NO es una migración**, es un `CREATE TABLE IF NOT EXISTS`

**Riesgo**: ✅ **BAJO** - SQLAlchemy maneja bien tablas existentes

---

## 2. MODELOS SQL IDENTIFICADOS

### 2.1 Módulo Auth (4 tablas)

| Modelo     | Tabla        | Descripción              |
| ---------- | ------------ | ------------------------ |
| `User`     | `users`      | Usuarios del sistema     |
| `Role`     | `roles`      | Roles de usuario         |
| `UserRole` | `user_roles` | Relación N:M users-roles |
| `Test`     | `test`       | Tabla de prueba          |

### 2.2 Módulo Platform Config (4 tablas)

| Modelo                   | Tabla                      | Descripción                         |
| ------------------------ | -------------------------- | ----------------------------------- |
| `Process`                | `process`                  | Procesos/tareas definidos           |
| `ProcessRun`             | `process_runs`             | Ejecuciones de procesos             |
| `ProcessRunLog`          | `process_run_logs`         | Logs de ejecuciones                 |
| `ScheduledProcessConfig` | `scheduled_process_config` | Configuración de tareas programadas |

### 2.3 Módulo Leagues Manager (6 tablas)

| Modelo                    | Tabla                       | Descripción         |
| ------------------------- | --------------------------- | ------------------- |
| `Continente`              | `continente`                | Continentes         |
| `Pais`                    | `pais`                      | Países              |
| `Liga`                    | `liga`                      | Ligas deportivas    |
| `Torneo`                  | `torneo`                    | Torneos             |
| `FuenteExtraccion`        | `fuente_extraccion`         | Fuentes de datos    |
| `DetalleFuenteExtraccion` | `detalle_fuente_extraccion` | Detalles de fuentes |

**Total SQL**: 14 tablas

---

## 3. MODELOS MONGODB IDENTIFICADOS

### 3.1 Módulo Auth (2 colecciones)

| Modelo       | Colección      | Descripción             | Estado        |
| ------------ | -------------- | ----------------------- | ------------- |
| `SessionLog` | `session_logs` | Logs de sesión/acciones | ✅ ACTIVO      |
| `AccessLog`  | `access_logs`  | Logs de acceso HTTP     | ⚠️ SOLO MODELO |

**Total MongoDB**: 2 colecciones

---

## 4. ANÁLISIS DE CONFLICTOS POTENCIALES

### 4.1 SQL: create_all() vs Datos Existentes

| Escenario                | Resultado                | Riesgo  |
| ------------------------ | ------------------------ | ------- |
| Tablas no existen        | ✅ Se crean correctamente | NINGUNO |
| Tablas existen sin datos | ✅ No hace nada           | NINGUNO |
| Tablas existen con datos | ✅ No hace nada           | NINGUNO |
| Esquema cambió           | ⚠️ No actualiza tablas    | MEDIO   |

**Conclusión**: `create_all()` es **SEGURO** para tablas existentes. NO borra datos.

### 4.2 MongoDB: Inicialización de Colecciones

| Escenario              | Resultado                         | Riesgo  |
| ---------------------- | --------------------------------- | ------- |
| Colecciones no existen | ✅ Se crean al insertar primer doc | NINGUNO |
| Colecciones existen    | ✅ No hace nada                    | NINGUNO |
| Índices no existen     | ✅ Se crean automáticamente        | NINGUNO |

**Conclusión**: MongoDB es **SEGURO** - No hay operaciones destructivas al iniciar.

---

## 5. TAREAS PROGRAMADAS (SCHEDULER)

### 5.1 Análisis del Scheduler

**Archivo**: `backend/core/scheduler/__init__.py`

```python
def start_scheduler():
    """Inicia el scheduler de procesos programados"""
    # Carga jobs desde la base de datos
    # Programa ejecuciones periódicas
```

**¿Qué hace al iniciar?**
1. Conecta a PostgreSQL
2. Lee configuración de `scheduled_process_config`
3. Programa tareas según cron expressions
4. **NO ejecuta tareas inmediatamente**

**Riesgo**: ✅ **BAJO** - Solo programa, no ejecuta

### 5.2 Jobs Programados

| Job         | Frecuencia | Descripción              |
| ----------- | ---------- | ------------------------ |
| Log Cleanup | Diario     | Limpia logs antiguos     |
| Otros jobs  | Variable   | Depende de configuración |

---

## 6. MIDDLEWARE DE AUDITORÍA

### 6.1 AuditMiddleware

**¿Qué hace?**
- Intercepta CADA request HTTP
- Extrae user_id del JWT
- Llama a `SessionLogService.log_api_call()`
- Registra en MongoDB `session_logs`

**Impacto en BD**:
- ✅ Escritura en MongoDB (no bloqueante)
- ✅ No afecta PostgreSQL
- ✅ No interrumpe flujo principal

**Riesgo**: ✅ **NINGUNO** - Escritura asíncrona y resiliente

---

## 7. DIAGNÓSTICO DE IMPACTO

### 7.1 Resumen de Operaciones al Iniciar

| Operación                | Base de Datos | Impacto                    | Riesgo    |
| ------------------------ | ------------- | -------------------------- | --------- |
| `create_db_and_tables()` | PostgreSQL    | Crear tablas si no existen | ✅ BAJO    |
| `start_scheduler()`      | PostgreSQL    | Leer configuración         | ✅ BAJO    |
| `AuditMiddleware`        | MongoDB       | Registrar logs             | ✅ NINGUNO |
| `SessionLogService`      | MongoDB       | Escribir logs              | ✅ NINGUNO |

### 7.2 Conflicto con Datos Existentes

**Escenario**: Usuario tiene datos en PostgreSQL y MongoDB

| Base de Datos | Operación      | ¿Borra datos? | ¿Modifica esquema?            |
| ------------- | -------------- | ------------- | ----------------------------- |
| PostgreSQL    | `create_all()` | ❌ NO          | ❌ NO (solo crea si no existe) |
| MongoDB       | Inicialización | ❌ NO          | ❌ NO                          |

**Conclusión**: ✅ **NO HAY CONFLICTO** con datos existentes

---

## 8. PROBLEMAS IDENTIFICADOS

### 8.1 ⚠️ PROBLEMA 1: AccessLog sin uso

**Situación**: El modelo `AccessLog` existe pero:
- ❌ No tiene repositorio
- ❌ No tiene servicio
- ❌ No se usa en la aplicación

**Impacto**:
- ✅ No causa errores (solo ocupa espacio en memoria)
- ⚠️ Confusión arquitectónica

**Recomendación**: Eliminar o documentar su propósito futuro

### 8.2 ⚠️ PROBLEMA 2: create_all() vs Alembic

**Situación**: El proyecto usa Alembic para migraciones, pero `main_init_web_server.py` usa `create_all()`

**Problema**:
- `create_all()` crea tablas pero NO maneja cambios de esquema
- Si agregas una columna, `create_all()` no la agregará
- Deberías usar `alembic upgrade head` en su lugar

**Impacto**:
- ✅ Funciona para desarrollo inicial
- ❌ NO funciona para actualizaciones de esquema

**Recomendación**: Usar Alembic para migraciones en producción

### 8.3 ⚠️ PROBLEMA 3: Sin verificación de conexión

**Situación**: `create_db_and_tables()` no verifica si la BD está disponible antes de intentar crear tablas

**Impacto**:
- Si PostgreSQL no está disponible, el servidor falla al iniciar
- Error fatal que detiene la aplicación

**Recomendación**: Agregar verificación de conexión antes de `create_all()`

---

## 9. RECOMENDACIONES DE ARQUITECTURA

### 9.1 PRIORIDAD ALTA

#### 1. Usar Alembic en lugar de create_all()

**Archivo**: `backend/main_init_web_server.py`

```python
# ANTES (create_all)
create_db_and_tables()

# DESPUÉS (Alembic)
from alembic.config import Config
from alembic import command

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

**Beneficio**: Maneja cambios de esquema correctamente

#### 2. Verificar conexión antes de migraciones

```python
def verify_database_connection():
    """Verifica que la BD esté disponible"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ BD no disponible: {e}")
        return False
```

#### 3. Eliminar o documentar AccessLog

**Opción A**: Eliminar completamente
```python
# Eliminar archivo
backend/apps/auth/infrastructure/models/mongo/access_log_model.py
```

**Opción B**: Documentar propósito futuro
```python
class AccessLog(Document):
    """
    NOTA: Este modelo se reserva para uso futuro.
    Actualmente NO se usa en la aplicación.
    """
```

### 9.2 PRIORIDAD MEDIA

#### 4. Agregar health check de BD

```python
@app.get("/health/db")
async def health_check_db():
    """Verifica estado de las bases de datos"""
    postgres_ok = verify_postgres_connection()
    mongo_ok = verify_mongo_connection()
    
    return {
        "postgres": "ok" if postgres_ok else "error",
        "mongodb": "ok" if mongo_ok else "error"
    }
```

#### 5. Logging de operaciones de BD

```python
def create_db_and_tables():
    """Crea tablas con logging detallado"""
    logger.info("🔍 Verificando tablas existentes...")
    
    # Verificar qué tablas existen
    existing_tables = engine.table_names()
    logger.info(f"📋 Tablas existentes: {existing_tables}")
    
    # Crear solo las que faltan
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ Verificación de tablas completada")
```

### 9.3 PRIORIDAD BAJA

#### 6. Implementar retry logic para conexiones

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def connect_to_database():
    """Conecta a la BD con reintentos"""
    return engine.connect()
```

#### 7. Métricas de operaciones de BD

```python
from prometheus_client import Counter

db_operations = Counter(
    'db_operations_total',
    'Total de operaciones de BD',
    ['database', 'operation']
)
```

---

## 10. PLAN DE ACCIÓN

### FASE 1: Inmediata (Hoy)

| Tarea                                              | Prioridad | Impacto   |
| -------------------------------------------------- | --------- | --------- |
| ✅ Verificar que `create_all()` no causa conflictos | ALTA      | Ninguno   |
| ✅ Documentar AccessLog como "reservado"            | MEDIA     | Claridad  |
| ✅ Agregar health check de BD                       | MEDIA     | Monitoreo |

### FASE 2: Corto plazo (Esta semana)

| Tarea                                   | Prioridad | Impacto               |
| --------------------------------------- | --------- | --------------------- |
| 🔄 Reemplazar `create_all()` con Alembic | ALTA      | Migraciones correctas |
| 🔄 Agregar verificación de conexión      | ALTA      | Robustez              |
| 🔄 Logging detallado de operaciones BD   | MEDIA     | Debugging             |

### FASE 3: Medio plazo (Este mes)

| Tarea                           | Prioridad | Impacto        |
| ------------------------------- | --------- | -------------- |
| 📊 Implementar métricas de BD    | BAJA      | Monitoreo      |
| 🔄 Retry logic para conexiones   | BAJA      | Resiliencia    |
| 📚 Documentar arquitectura de BD | BAJA      | Mantenibilidad |

---

## 11. CONCLUSIÓN

### ✅ ESTADO ACTUAL: ESTABLE

**No hay conflictos críticos** con datos existentes:
- ✅ `create_all()` es seguro para tablas existentes
- ✅ MongoDB no tiene operaciones destructivas
- ✅ Scheduler no ejecuta tareas al iniciar
- ✅ Middleware de auditoría es resiliente

### ⚠️ MEJORAS RECOMENDADAS

1. **Usar Alembic** para migraciones (no `create_all()`)
2. **Verificar conexión** antes de operaciones de BD
3. **Documentar AccessLog** como reservado para futuro
4. **Agregar health checks** para monitoreo

### 🎯 PRÓXIMOS PASOS

1. Ejecutar servidor y verificar que inicia correctamente
2. Verificar logs de operaciones de BD
3. Implementar mejoras de arquitectura según prioridad

---

**Elaborado por**: Arquitecto de Software Senior  
**Fecha**: 2026-03-30  
**Estado**: ✅ DIAGNÓSTICO COMPLETO