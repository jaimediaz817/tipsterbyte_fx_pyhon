# Diagnóstico: Excepciones MongoDB y Session Logs

## Fecha: 2026-03-29
## Estado: PENDIENTE DE IMPLEMENTACIÓN

---

## 1. ANÁLISIS DEL SITUACIÓN ACTUAL

### 1.1 Eventos que Generan Registros en MongoDB

Los registros en la colección `session_logs` se generan en dos puntos:

#### Punto 1: AuditMiddleware (Automático)
**Archivo**: `backend/core/middleware/audit_middleware.py`

```python
# Líneas 52-71
if user_id:
    try:
        log = SessionLog(...)
        await log.insert()  # ← Escritura en MongoDB
    except Exception as e:
        # ❌ PROBLEMA: Excepción ignorada silenciosamente
        pass
```

**Eventos capturados**:
- Cada request HTTP de un usuario autenticado
- Incluye: endpoint, método HTTP, status code, tiempo de respuesta, IP, user-agent

#### Punto 2: SessionLogService (Manual)
**Archivo**: `backend/apps/auth/application/services/session_log_service.py`

```python
# Método log_action()
async def log_action(...) -> SessionLog:
    log = SessionLog(...)
    return await self.repository.save(log)  # ← Escritura en MongoDB
```

**Eventos capturados**:
- Login/logout
- Eventos específicos de negocio
- Acciones críticas del sistema

---

## 2. PROBLEMAS IDENTIFICADOS

### 2.1 ⚠️ VIOLACIÓN DE PRINCIPIOS DE ARQUITECTURA (CRÍTICO)

**Ubicación**: `backend/core/middleware/audit_middleware.py` líneas 52-71

```python
# ❌ PROBLEMA CRÍTICO: El middleware manipula DIRECTAMENTE el modelo
if user_id:
    try:
        # ❌ VIOLACIÓN: Crear instancia del modelo directamente
        log = SessionLog(
            user_id=user_id,
            session_id=session_id,
            action="api_call",
            # ... más campos
        )
        # ❌ VIOLACIÓN: Insertar directamente sin pasar por servicio
        await log.insert()
    except Exception as e:
        pass
```

**Principios Violados**:

1. **❌ Separación de Responsabilidades (SRP)**
   - El middleware NO debería conocer la estructura del modelo `SessionLog`
   - El middleware NO debería saber cómo crear instancias del modelo
   - El middleware NO debería ejecutar operaciones de persistencia directamente

2. **❌ Inversión de Dependencias (DIP)**
   - El middleware depende directamente de la implementación concreta (`SessionLog`)
   - Debería depender de una abstracción (servicio)

3. **❌ Arquitectura Limpia (Clean Architecture)**
   - Las capas externas (middleware) están accediendo directamente a la capa de infraestructura (modelo MongoDB)
   - Se salta la capa de aplicación (servicio)

**Arquitectura Correcta**:
```
Middleware → Servicio → Repositorio → Modelo
```

**Arquitectura Actual (INCORRECTA)**:
```
Middleware → Modelo (SALTA SERVICIO Y REPOSITORIO)
```

**Consecuencias de la Violación**:
1. **Duplicación de lógica**: Si se necesita lógica de negocio para crear logs, se duplicará
2. **Dificultad para testing**: No se puede mockear el servicio en tests del middleware
3. **Mantenibilidad**: Cambios en el modelo requieren cambios en el middleware
4. **Inconsistencia**: El `SessionLogService` tiene lógica que el middleware ignora

---

### 2.2 Excepción Silenciosa en AuditMiddleware

**Ubicación**: `backend/core/middleware/audit_middleware.py` líneas 68-71

```python
try:
    await log.insert()
except Exception as e:
    # ❌ No se loggea el error
    # ❌ No se notifica que MongoDB está caído
    # ❌ Se pierden datos de auditoría
    pass
```

**Consecuencias**:
1. **Pérdida de datos**: Los logs de auditoría se pierden silenciosamente
2. **Sin diagnóstico**: No hay forma de saber que MongoDB está caído
3. **Sin métricas**: No se registran fallos para monitoreo
4. **Falsa sensación de seguridad**: El sistema parece funcionar normalmente

### 2.3 Falta de Excepciones Específicas

**Excepciones existentes** (ver `backend/core/exceptions/__init__.py`):
- ProcessException, FuenteException, RobotException, ConcurrencyException

**Excepciones faltantes**:
- ❌ MongoDBConnectionException
- ❌ SessionLogWriteException
- ❌ DatabaseException (excepción base para BD)

---

## 3. PROPUESTA DE SOLUCIÓN

### 3.1 Nuevas Excepciones a Crear

#### 3.1.1 Excepción Base de Datos
```python
# backend/core/exceptions/database_exceptions.py

class DatabaseException(TipsterByteException):
    """Excepción base para errores de base de datos."""
    pass

class MongoDBException(DatabaseException):
    """Excepción base para errores de MongoDB."""
    pass

class MongoDBConnectionException(MongoDBException):
    """MongoDB no está disponible o no se puede conectar."""
    pass

class MongoDBWriteException(MongoDBException):
    """Error al escribir en MongoDB."""
    pass

class MongoDBReadException(MongoDBException):
    """Error al leer de MongoDB."""
    pass
```

#### 3.1.2 Excepciones de Session Log
```python
# backend/core/exceptions/session_log_exceptions.py

class SessionLogException(TipsterByteException):
    """Excepción base para errores de session logs."""
    pass

class SessionLogWriteException(SessionLogException):
    """Error al escribir un session log."""
    pass

class SessionLogReadException(SessionLogException):
    """Error al leer session logs."""
    pass
```

---

## 4. IMPLEMENTACIÓN RECOMENDADA

### 4.1 Archivos a Crear

1. **`backend/core/exceptions/database_exceptions.py`**
   - DatabaseException (base)
   - MongoDBException (base MongoDB)
   - MongoDBConnectionException
   - MongoDBWriteException
   - MongoDBReadException

2. **`backend/core/exceptions/session_log_exceptions.py`**
   - SessionLogException (base)
   - SessionLogWriteException
   - SessionLogReadException

### 4.2 Archivos a Modificar

1. **`backend/core/exceptions/__init__.py`**
   - Agregar imports de nuevas excepciones
   - Agregar a __all__

2. **`backend/core/middleware/audit_middleware.py`**
   - Importar logger de Loguru
   - Agregar logging de errores
   - Mantener comportamiento de no fallar

3. **`backend/apps/auth/application/services/session_log_service.py`**
   - Importar MongoDBWriteException
   - Agregar try/except en log_action()
   - Re-lanzar excepción para manejo upstream

4. **`backend/apps/auth/infrastructure/repositories/session_log_repository.py`**
   - Importar excepciones de MongoDB
   - Agregar try/except en métodos de escritura/lectura
   - Re-lanzar excepciones específicas

---

## 5. CASOS DE USO

### 5.1 MongoDB No Disponible al Iniciar

**Escenario**: La aplicación intenta conectar a MongoDB pero no está disponible.

**Comportamiento actual**:
- La aplicación puede iniciar (MongoDB es asíncrono)
- Los primeros logs fallan silenciosamente
- No hay diagnóstico

**Comportamiento propuesto**:
- La aplicación inicia normalmente
- Se loggea advertencia: "⚠️ MongoDB no disponible, los session logs se perderán"
- Se registra métrica de "mongo_connection_failure"

### 5.2 MongoDB Se Caí Durante Operación

**Escenario**: MongoDB está corriendo pero se cae durante la operación.

**Comportamiento actual**:
- Las requests continúan funcionando
- Los logs se pierden silenciosamente
- No hay diagnóstico

**Comportamiento propuesto**:
- Las requests continúan funcionando (no interrumpir)
- Se loggea error: "❌ Error al escribir session log: <error>"
- Se registra métrica de "session_log_write_failure"
- Se puede configurar alerta si hay muchos fallos

---

## 6. PRIORIDAD DE IMPLEMENTACIÓN

### Prioridad ALTA (Implementar Primero)
1. ✅ Crear excepciones de MongoDB (database_exceptions.py)
2. ✅ Agregar logging de errores en AuditMiddleware
3. ✅ Agregar logging de errores en SessionLogRepository

### Prioridad MEDIA (Implementar Después)
4. ✅ Crear excepciones de SessionLog (session_log_exceptions.py)
5. ✅ Modificar SessionLogService para lanzar excepciones
6. ✅ Agregar métricas de fallos

### Prioridad BAJA (Mejoras Futuras)
7. ⬜ Implementar retry logic para escrituras fallidas
8. ⬜ Implementar cola de logs para reintentos
9. ⬜ Implementar alertas automáticas

---

## 7. OPINIÓN DEL ARQUITECTO DE SOFTWARE

### 7.1 Análisis Crítico de la Situación Actual

Como arquitecto de software senior, debo señalar que el problema de `AuditMiddleware` no es solo técnico sino **arquitectónico fundamental**. El middleware está actuando como un "atajo" que ignora toda la arquitectura diseñada.

**Analogía**: Es como construir un edificio con un plano hermoso, pero luego permitir que los albañiles construyan ventanas directamente en las paredes sin seguir el plano. El resultado es un caos estructural.

### 7.2 ¿Por qué el Middleware NO debe manipular modelos directamente?

1. **Principio de Mínima Conocimiento (Law of Demeter)**
   - El middleware solo debería conocer sus dependencias directas (servicios)
   - NO debería conocer implementaciones internas (modelos, repositorios)

2. **Principio de Inversión de Dependencias**
   - Las capas externas (middleware) deben depender de abstracciones (interfaces de servicio)
   - NO de implementaciones concretas (modelos MongoDB)

3. **Principio de Responsabilidad Única**
   - El middleware tiene UNA responsabilidad: interceptar requests/responses
   - La persistencia de logs es responsabilidad del servicio

4. **Principio Abierto/Cerrado**
   - El middleware debería estar ABIERTO a extensión (nuevos servicios)
   - CERRADO a modificación (no cambiar cuando cambia el modelo)

### 7.3 Arquitectura Propuesta (CORRECTA)

```
┌─────────────────────────────────────────────────────────────┐
│                     MIDDLEWARE (Capa Externa)               │
│  - Intercepta requests/responses                            │
│  - NO conoce modelos ni repositorios                        │
│  - Solo conoce el servicio (inyección de dependencias)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     SERVICIO (Capa de Aplicación)           │
│  - Contiene lógica de negocio                               │
│  - Crea el SessionLog con datos del middleware              │
│  - Maneja excepciones y logging                             │
│  - Llama al repositorio                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   REPOSITORIO (Capa de Infraestructura)     │
│  - Implementa operaciones de persistencia                   │
│  - Maneja errores específicos de MongoDB                    │
│  - Re-lanza excepciones de dominio                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     MODELO (Capa de Dominio)                │
│  - Define estructura de datos                               │
│  - Validaciones de Pydantic                                 │
│  - NO contiene lógica de negocio                            │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 Implementación Correcta del Middleware

```python
# backend/core/middleware/audit_middleware.py (VERSIÓN CORRECTA)

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from loguru import logger

from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.security.jwt_handler import JWTHandler

class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra automáticamente las requests HTTP.
    
    Principios aplicados:
    - Inversión de dependencias: Depende del servicio, no del modelo
    - Separación de responsabilidades: Solo intercepta, no persiste
    - Mínimo conocimiento: No conoce implementación interna
    """
    
    def __init__(self, app, session_log_service: SessionLogService):
        super().__init__(app)
        self.session_log_service = session_log_service  # ✅ Inyección de dependencias
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Procesar request
        response = await call_next(request)
        
        # Calcular tiempo de respuesta
        response_time = (time.time() - start_time) * 1000
        
        # Extraer user_id del JWT
        user_id = self._extract_user_id(request)
        
        # Solo registrar si hay usuario autenticado
        if user_id:
            try:
                # ✅ LLAMAR AL SERVICIO (no al modelo directamente)
                await self.session_log_service.log_api_call(
                    user_id=user_id,
                    session_id=request.headers.get("X-Session-ID"),
                    ip_address=request.client.host if request.client else "unknown",
                    user_agent=request.headers.get("user-agent", "unknown"),
                    endpoint=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                )
            except Exception as e:
                # ✅ LOGGEAR ERROR (no ignorar silenciosamente)
                logger.error(f"❌ Error al registrar log de auditoría: {e}")
                # No interrumpir la request
                pass
        
        return response
    
    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extrae user_id del token JWT."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = JWTHandler.verify_token(token)
            if payload:
                return payload.get("sub")
        return None
```

### 7.5 Método del Servicio para el Middleware

```python
# backend/apps/auth/application/services/session_log_service.py

class SessionLogService:
    async def log_api_call(
        self,
        user_id: str,
        session_id: Optional[str],
        ip_address: str,
        user_agent: str,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
    ) -> SessionLog:
        """
        Registra una llamada a la API.
        
        Este método encapsula toda la lógica de creación del log,
        cumpliendo con SRP y DIP.
        """
        import uuid
        
        # Generar session_id si no existe
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Crear log usando el método existente
        return await self.log_action(
            user_id=user_id,
            session_id=session_id,
            action="api_call",
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time_ms=response_time_ms,
        )
```

### 7.6 Inyección de Dependencias en main_init_web_server.py

```python
# backend/main_init_web_server.py

from apps.auth.application.services.session_log_service import SessionLogService
from apps.auth.infrastructure.repositories.session_log_repository import SessionLogRepository

# Crear instancia del repositorio
session_log_repository = SessionLogRepository()

# Crear instancia del servicio
session_log_service = SessionLogService(session_log_repository)

# Inyectar servicio en el middleware
app.add_middleware(AuditMiddleware, session_log_service=session_log_service)
```

---

## 8. RESUMEN

### Problemas Identificados
1. **Violación de principios de arquitectura** (CRÍTICO)
   - Middleware manipula modelo directamente
   - Salta capas de servicio y repositorio
   - Viola SRP, DIP y Clean Architecture

2. **Excepción silenciosa**
   - Errores de MongoDB se ignoran
   - Sin logging ni diagnóstico

3. **Falta de excepciones específicas**
   - No hay excepciones para MongoDB
   - No hay excepciones para session logs

### Solución Propuesta
1. **Corrección arquitectónica** (PRIORIDAD ALTA)
   - Middleware usa servicio (no modelo)
   - Servicio usa repositorio
   - Repositorio usa modelo
   - Inyección de dependencias

2. **Excepciones específicas**
   - MongoDBConnectionException
   - MongoDBWriteException
   - MongoDBReadException
   - SessionLogWriteException

3. **Logging de errores**
   - Loggear errores en middleware
   - Loggear errores en repositorio
   - No ignorar silenciosamente

### Beneficios
- ✅ Arquitectura limpia y mantenible@DIAG
- ✅ Principios SOLID aplicados correctamente
- ✅ Testing facilitado (mock del servicio)
- ✅ Diagnóstico claro de problemas
- ✅ Métricas para monitoreo
- ✅ Base para retry logic y alertas

### Orden de Implementación
1. **Fase 1** (Inmediata): Corregir arquitectura del middleware
2. **Fase 2** (Urgente): Crear excepciones de MongoDB
3. **Fase 3** (Importante): Agregar logging de errores
4. **Fase 4** (Mejora): Métricas y alertas
