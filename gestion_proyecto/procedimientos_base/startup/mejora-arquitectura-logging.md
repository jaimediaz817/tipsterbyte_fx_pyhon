# 🎯 **MEJORA DE ARQUITECTURA DE LOGGING - PROPUESTA PROFESIONAL**

## 📋 **PROBLEMAS IDENTIFICADOS EN LA ARQUITECTURA ACTUAL**

### **1. Fragmentación de Logs (PROBLEMA CRÍTICO)**
```
backend/logs/
├── auth.log
├── general_app.log
├── platform_config.log
├── robots.log
├── system.log
└── scheduler/
    └── scheduler.log
```

**Problemas:**
- ❌ **Dificulta correlación de eventos**: Un error en el scheduler que afecta a un robot no se puede seguir
- ❌ **Duplicación de logs**: Un mismo evento puede aparecer en múltiples archivos
- ❌ **Búsqueda ineficiente**: Para encontrar un error hay que revisar 6+ archivos
- ❌ **Gestión compleja**: 6 diferentes políticas de rotación/retención

### **2. Filtros Lambda Complejos**
```python
filter=lambda r: r["name"].startswith("core") and "scheduler" not in r["name"]
```

**Problemas:**
- ❌ **Difícil de mantener**: Cambios en la estructura de módulos rompen filtros
- ❌ **Propenso a errores**: Filtros pueden excluir logs importantes
- ❌ **No escalable**: Agregar nuevo módulo requiere modificar filtros

### **3. Falta de Contexto para Producción**
- ❌ **No hay trace ID**: No se puede seguir una request completa
- ❌ **No hay correlación**: No se puede saber qué logs pertenecen a qué ejecución
- ❌ **No hay estructura para excepciones**: No hay base para excepciones personalizadas

---

## ✅ **PROPUESTA DE MEJORA - ARQUITECTURA PROFESIONAL**

### **Principios de Diseño:**
1. **Un solo archivo de logs** para toda la aplicación
2. **Estructura JSON** para facilitar parsing y búsqueda
3. **Trace ID único** por request/ejecución
4. **Contexto enriquecido** en cada log
5. **Preparado para excepciones personalizadas**

---

## 🔧 **IMPLEMENTACIÓN PROPUESTA**

### **1. Archivo Único de Logs con Estructura JSON**

**Archivo:** `backend/logs/application.log`

**Formato:**
```json
{
  "timestamp": "2026-03-20T20:30:15.123456-05:00",
  "level": "ERROR",
  "logger": "apps.leagues_manager.tasks.process_rastreo_data_fuentes_deportivas_task",
  "module": "process_rastreo_data_fuentes_deportivas_task",
  "function": "launch_process_rastreo_data_fuentes_deportivas_task",
  "line": 107,
  "message": "Proceso 'PROCESS_STANDINGS_EXTRACTION' está INACTIVO",
  "trace_id": "req_abc123def456",
  "process_code": "PROCESS_STANDINGS_EXTRACTION",
  "run_id": "run_xyz789",
  "extra": {
    "is_active": false,
    "process_id": 2,
    "suggestion": "Marca is_active=True en la tabla 'process'"
  }
}
```

### **2. Configuración de Logging Mejorada**

```python
# backend/core/logger.py - NUEVA VERSIÓN

import sys
import json
from loguru import logger
from core.config import settings
from core.paths import LOGS_ROOT
from datetime import datetime

class JSONFormatter:
    """Formateador JSON para logs estructurados."""
    
    def __init__(self):
        self.extra_fields = {}
    
    def format(self, record):
        """Convierte el record de Loguru a JSON estructurado."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record["time"].timestamp()).isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
        }
        
        # Agregar trace_id si existe
        if "trace_id" in record["extra"]:
            log_entry["trace_id"] = record["extra"]["trace_id"]
        
        # Agregar campos extra del contexto
        for key, value in record["extra"].items():
            if key != "trace_id":
                log_entry[key] = value
        
        # Agregar exception info si existe
        if record["exception"]:
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback,
            }
        
        return json.dumps(log_entry, ensure_ascii=False, default=str) + "\n"

def configure_logging():
    """
    Configura logging profesional para producción:
    - Un solo archivo de logs con estructura JSON
    - Trace ID único por request
    - Contexto enriquecido
    - Preparado para excepciones personalizadas
    """
    logger.remove()
    LOGS_ROOT.mkdir(exist_ok=True)
    
    # Formato JSON para archivo
    json_formatter = JSONFormatter()
    
    # Formato colorido para consola (desarrollo)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> | "
        "<yellow>trace:{extra[trace_id]}</yellow> - "
        "<level>{message}</level>"
    )
    
    # 1. Consola (solo para desarrollo)
    logger.add(
        sink=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
        format=console_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # 2. Archivo único de logs (JSON estructurado)
    logger.add(
        sink=LOGS_ROOT / "application.log",
        level="INFO",
        format=json_formatter.format,
        rotation="50 MB",  # Rotar cada 50MB
        retention="30 days",  # Retener 30 días
        compression="zip",
        enqueue=True,  # Asíncrono
        backtrace=True,
        diagnose=True,
        serialize=False,  # Ya serializamos nosotros
    )
    
    # 3. Archivo de errores (solo ERROR y CRITICAL)
    logger.add(
        sink=LOGS_ROOT / "errors.log",
        level="ERROR",
        format=json_formatter.format,
        rotation="20 MB",
        retention="90 days",  # Errores se retienen más tiempo
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
    
    logger.info("✅ Logging profesional configurado (JSON + Trace ID)")

# --- UTILIDADES PARA TRACE ID ---

import uuid
from contextvars import ContextVar

# Context variable para trace_id
trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')

def generate_trace_id() -> str:
    """Genera un trace ID único para una request."""
    return f"req_{uuid.uuid4().hex[:12]}"

def get_trace_id() -> str:
    """Obtiene el trace ID actual del contexto."""
    return trace_id_var.get()

def set_trace_id(trace_id: str):
    """Establece el trace ID en el contexto."""
    trace_id_var.set(trace_id)

def log_with_context(level: str, message: str, **kwargs):
    """
    Log con contexto enriquecido.
    
    Ejemplo:
        log_with_context(
            "error",
            "Proceso falló",
            process_code="PROCESS_STANDINGS_EXTRACTION",
            run_id="run_xyz789",
            is_active=False
        )
    """
    trace_id = get_trace_id()
    extra = {"trace_id": trace_id, **kwargs}
    
    log_func = getattr(logger, level.lower())
    log_func(message, **extra)
```

### **3. Middleware para Trace ID Automático**

```python
# backend/core/middleware.py - AGREGAR TRACE ID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from core.logger import generate_trace_id, set_trace_id

class TraceIDMiddleware(BaseHTTPMiddleware):
    """Middleware que agrega trace ID único a cada request."""
    
    async def dispatch(self, request: Request, call_next):
        # Generar trace ID único
        trace_id = generate_trace_id()
        set_trace_id(trace_id)
        
        # Agregar trace ID al request state
        request.state.trace_id = trace_id
        
        # Procesar request
        response = await call_next(request)
        
        # Agregar trace ID al header de respuesta
        response.headers["X-Trace-ID"] = trace_id
        
        return response
```

### **4. Excepciones Personalizadas (Preparación)**

```python
# backend/core/exceptions.py - NUEVO ARCHIVO

from typing import Optional, Dict, Any

class TipsterByteException(Exception):
    """Excepción base para TipsterByte FX."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        context: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.context = context or {}
        self.suggestion = suggestion
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la excepción a diccionario para logging."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "context": self.context,
            "suggestion": self.suggestion,
        }

class ProcessInactiveException(TipsterByteException):
    """Excepción cuando un proceso está inactivo."""
    
    def __init__(self, process_code: str, process_id: int):
        super().__init__(
            message=f"Proceso '{process_code}' está INACTIVO",
            error_code="PROCESS_INACTIVE",
            status_code=400,
            context={"process_code": process_code, "process_id": process_id, "is_active": False},
            suggestion=f"Marca is_active=True en la tabla 'process' para el código '{process_code}'",
        )

class FuenteInactiveException(TipsterByteException):
    """Excepción cuando una fuente está inactiva."""
    
    def __init__(self, fuente_id: int, fuente_name: str):
        super().__init__(
            message=f"Fuente '{fuente_name}' (ID: {fuente_id}) está INACTIVA",
            error_code="FUENTE_INACTIVE",
            status_code=400,
            context={"fuente_id": fuente_id, "fuente_name": fuente_name, "is_active": False},
            suggestion=f"Activa la fuente '{fuente_name}' usando el endpoint /api/v1/leagues/fuentes/{fuente_id}/resume",
        )

class DetalleInactiveException(TipsterByteException):
    """Excepción cuando un detalle está inactivo."""
    
    def __init__(self, detalle_id: int, torneo_nombre: str, fuente_name: str):
        super().__init__(
            message=f"Detalle '{torneo_nombre}' + '{fuente_name}' (ID: {detalle_id}) está INACTIVO",
            error_code="DETALLE_INACTIVE",
            status_code=400,
            context={
                "detalle_id": detalle_id,
                "torneo_nombre": torneo_nombre,
                "fuente_name": fuente_name,
                "is_active": False,
            },
            suggestion=f"Activa el detalle usando el endpoint /api/v1/leagues/detalles/{detalle_id}/resume",
        )
```

### **5. Uso de Excepciones en el Orquestador**

```python
# backend/apps/leagues_manager/tasks/process_rastreo_data_fuentes_deportivas_task.py

from core.exceptions import ProcessInactiveException, FuenteInactiveException
from core.logger import log_with_context

async def launch_process_rastreo_data_fuentes_deportivas_task(process_code: str):
    """Orquestador con excepciones personalizadas."""
    
    # Verificar si el proceso está activo
    if not is_active:
        # Log estructurado con contexto
        log_with_context(
            "warning",
            "Proceso inactivo detectado",
            process_code=process_code,
            process_id=process_entity.id,
            is_active=False,
            suggestion=f"Marca is_active=True para '{process_code}'",
        )
        
        # Lanzar excepción personalizada
        raise ProcessInactiveException(
            process_code=process_code,
            process_id=process_entity.id,
        )
    
    # Verificar si la fuente está activa
    if detalle.fuente and not detalle.fuente.is_active:
        log_with_context(
            "debug",
            "Fuente inactiva, saltando detalle",
            fuente_id=detalle.fuente.id,
            fuente_name=detalle.fuente.name,
            is_active=False,
        )
        
        raise FuenteInactiveException(
            fuente_id=detalle.fuente.id,
            fuente_name=detalle.fuente.name,
        )
```

---

## 📊 **BENEFICIOS DE LA NUEVA ARQUITECTURA**

### **1. Un Solo Archivo de Logs**
```
backend/logs/
├── application.log    ← TODOS los logs (JSON estructurado)
└── errors.log         ← Solo errores (retención 90 días)
```

**Ventajas:**
- ✅ **Búsqueda eficiente**: `grep "trace_id:req_abc123" application.log`
- ✅ **Correlación completa**: Seguir un request de principio a fin
- ✅ **Gestión simple**: Solo 2 archivos que rotar
- ✅ **Parsing fácil**: JSON permite filtrar por cualquier campo

### **2. Trace ID Automático**
```bash
# Buscar todos los logs de una request específica
grep "req_abc123def456" application.log

# Resultado:
# {"timestamp":"...", "message":"Iniciando orquestador", "trace_id":"req_abc123def456", ...}
# {"timestamp":"...", "message":"Proceso activo", "trace_id":"req_abc123def456", ...}
# {"timestamp":"...", "message":"Ejecutando robot", "trace_id":"req_abc123def456", ...}
# {"timestamp":"...", "message":"Orquestador finalizado", "trace_id":"req_abc123def456", ...}
```

### **3. Contexto Enriquecido**
```json
{
  "timestamp": "2026-03-20T20:30:15.123456-05:00",
  "level": "ERROR",
  "message": "Proceso falló",
  "trace_id": "req_abc123def456",
  "process_code": "PROCESS_STANDINGS_EXTRACTION",
  "run_id": "run_xyz789",
  "is_active": false,
  "suggestion": "Marca is_active=True en la tabla 'process'",
  "exception": {
    "type": "ProcessInactiveException",
    "value": "Proceso 'PROCESS_STANDINGS_EXTRACTION' está INACTIVO",
    "traceback": "..."
  }
}
```

### **4. Excepciones Personalizadas**
```python
# Antes (genérico)
logger.error("Proceso falló")

# Después (específico y accionable)
raise ProcessInactiveException(
    process_code="PROCESS_STANDINGS_EXTRACTION",
    process_id=2,
)
# Genera log estructurado con:
# - error_code: "PROCESS_INACTIVE"
# - context: {process_code, process_id, is_active}
# - suggestion: "Marca is_active=True..."
```

---

## 🧪 **PRUEBAS DE ESCRITORIO**

### **Prueba 1: Buscar logs por Trace ID**
```bash
# Request con trace_id=req_abc123def456
grep "req_abc123def456" backend/logs/application.log

# Resultado: Todos los logs de esa request en orden cronológico
```

### **Prueba 2: Filtrar por nivel de log**
```bash
# Solo errores
grep '"level":"ERROR"' backend/logs/application.log

# Solo warnings
grep '"level":"WARNING"' backend/logs/application.log
```

### **Prueba 3: Filtrar por módulo**
```bash
# Solo logs del scheduler
grep '"logger":"core.scheduler' backend/logs/application.log

# Solo logs de leagues_manager
grep '"logger":"apps.leagues_manager' backend/logs/application.log
```

### **Prueba 4: Filtrar por contexto**
```bash
# Solo logs de procesos inactivos
grep '"is_active":false' backend/logs/application.log

# Solo logs de un proceso específico
grep '"process_code":"PROCESS_STANDINGS_EXTRACTION"' backend/logs/application.log
```

### **Prueba 5: Análisis de errores**
```bash
# Ver errores con contexto completo
grep '"level":"ERROR"' backend/logs/application.log | jq '.exception.type, .context, .suggestion'

# Resultado:
# "ProcessInactiveException"
# {"process_code":"PROCESS_STANDINGS_EXTRACTION", "process_id":2, "is_active":false}
# "Marca is_active=True en la tabla 'process' para el código 'PROCESS_STANDINGS_EXTRACTION'"
```

---

## 📋 **PLAN DE MIGRACIÓN**

### **Fase 1: Preparación (1 día)**
1. Crear nuevo `core/logger.py` con arquitectura JSON
2. Crear `core/exceptions.py` con excepciones base
3. Crear middleware de Trace ID
4. Tests unitarios

### **Fase 2: Migración Gradual (2-3 días)**
1. Migrar orquestador a nuevo sistema de logging
2. Migrar scheduler a nuevo sistema
3. Migrar robots a nuevo sistema
4. Migrar endpoints REST

### **Fase 3: Validación (1 día)**
1. Ejecutar pruebas de escritorio
2. Verificar que todos los logs se generan correctamente
3. Verificar que Trace ID funciona
4. Verificar que excepciones personalizadas funcionan

### **Fase 4: Limpieza (1 día)**
1. Eliminar archivos de logs antiguos
2. Actualizar documentación
3. Crear guía de uso de nuevas excepciones

---

## 🎯 **EJEMPLOS DE USO REAL**

### **Caso 1: Debug de un error específico**
```bash
# Usuario reporta error en request específica
# Trace ID: req_abc123def456

# 1. Buscar todos los logs de esa request
grep "req_abc123def456" backend/logs/application.log

# 2. Ver el flujo completo:
# 2026-03-20T20:30:15 | INFO | Iniciando orquestador | trace_id=req_abc123def456
# 2026-03-20T20:30:15 | DEBUG | Verificando proceso | trace_id=req_abc123def456 | process_code=PROCESS_STANDINGS_EXTRACTION
# 2026-03-20T20:30:15 | WARNING | Proceso inactivo | trace_id=req_abc123def456 | is_active=false
# 2026-03-20T20:30:15 | ERROR | Proceso falló | trace_id=req_abc123def456 | exception=ProcessInactiveException

# 3. Ver contexto del error:
# {"error_code":"PROCESS_INACTIVE", "suggestion":"Marca is_active=True..."}
```

### **Caso 2: Monitoreo de producción**
```bash
# Contar errores por tipo
grep '"level":"ERROR"' backend/logs/application.log | jq -r '.exception.type' | sort | uniq -c

# Resultado:
# 15 ProcessInactiveException
# 3 FuenteInactiveException
# 1 DetalleInactiveException
```

### **Caso 3: Análisis de rendimiento**
```bash
# Ver cuántos requests se procesaron por hora
grep '"message":"Iniciando orquestador"' backend/logs/application.log | \
  jq -r '.timestamp' | \
  cut -d'T' -f2 | \
  cut -d':' -f1 | \
  sort | uniq -c

# Resultado:
# 45 20  (45 requests a las 20:00)
# 52 21  (52 requests a las 21:00)
```

---

## ✅ **RESUMEN DE MEJORAS**

| Aspecto              | Antes                    | Después                                      |
| -------------------- | ------------------------ | -------------------------------------------- |
| **Archivos de logs** | 6+ archivos fragmentados | 2 archivos (application.log + errors.log)    |
| **Formato**          | Texto plano              | JSON estructurado                            |
| **Trace ID**         | ❌ No existe              | ✅ Automático por request                     |
| **Contexto**         | ❌ Limitado               | ✅ Enriquecido (process_code, run_id, etc.)   |
| **Excepciones**      | ❌ Genéricas              | ✅ Personalizadas con error_code y suggestion |
| **Búsqueda**         | ❌ Difícil (6+ archivos)  | ✅ Fácil (grep/jq en JSON)                    |
| **Correlación**      | ❌ Imposible              | ✅ Por trace_id                               |
| **Gestión**          | ❌ Compleja               | ✅ Simple (2 archivos)                        |
| **Producción**       | ❌ No preparado           | ✅ Profesional                                |

---

## 🚀 **PRÓXIMOS PASOS**

1. **Revisar esta propuesta** con el equipo
2. **Aprobar arquitectura** de logging
3. **Implementar Fase 1** (preparación)
4. **Migrar gradualmente** (Fase 2-4)
5. **Crear excepciones personalizadas** para cada caso de uso
6. **Documentar guía de uso** de nuevas excepciones