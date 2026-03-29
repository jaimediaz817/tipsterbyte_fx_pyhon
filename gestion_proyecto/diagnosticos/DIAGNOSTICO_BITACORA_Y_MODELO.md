# 📊 DIAGNÓSTICO: BITÁCORA DE SESIÓN Y MODELO DE DATOS

**Fecha:** 2026-03-28
**Estado:** LISTO PARA IMPLEMENTACIÓN

---

## 📋 RESUMEN EJECUTIVO

### Preguntas del Usuario:
1. ¿Mantener modelo desconectado (users/roles vs ligas/fuentes)?
2. ¿Extender auth para bitácora de sesión?
3. ¿MongoDB vs PostgreSQL para bitácora?
4. ¿Mantener arquitectura servicios → repositorios?

### Respuestas del Arquitecto:
1. ✅ **SÍ, mantener desconectado** - Es correcto y beneficioso
2. ✅ **SÍ, extender auth** - Ya existe AccessLog en MongoDB
3. ✅ **MongoDB es correcto** - Optimizado para logs y auditoría
4. ✅ **SÍ, mantener arquitectura** - Patrón correcto

---

## ✅ DECISIÓN 1: MANTENER MODELO DESCONECTADO

### ¿Por qué es CORRECTO?

#### 1. Separación de Responsabilidades (SRP)
```
Auth (users/roles)     → ¿QUIÉN eres? → Autenticación/Autorización
Negocio (ligas/fuentes) → QUÉ haces?   → Lógica de negocio
```

**Beneficios:**
- ✅ Cambios en auth NO afectan lógica de negocio
- ✅ Cambios en negocio NO afectan seguridad
- ✅ Testing más fácil y aislado
- ✅ Escalabilidad independiente

#### 2. Principio de Mínimo Acoplamiento
```
┌─────────────────┐         ┌─────────────────┐
│   AUTH MODULE   │         │ BUSINESS MODULE │
│                 │         │                 │
│  users          │  ──X──  │  liga           │
│  roles          │         │  torneo         │
│  user_roles     │         │  fuente_extrac  │
└─────────────────┘         └─────────────────┘
        │                           │
        └───────────┬───────────────┘
                    │
            Solo se conectan via:
            - JWT token (user_id)
            - Request context
```

#### 3. Ventajas para Superadmin Dashboard:
- ✅ Auth puede evolucionar independientemente
- ✅ Roles pueden cambiar sin afectar scraping
- ✅ Usuarios pueden eliminarse sin cascada
- ✅ Auditoría separada por dominio

#### 4. Escalabilidad Futura:
```
Futuro: Microservicios separados
├── auth-service        (PostgreSQL)
├── business-service    (PostgreSQL)
├── scraping-service    (MongoDB + PostgreSQL)
└── notification-service (MongoDB)
```

### ✅ VEREDICTO: MANTENER DESCONECTADO

---

## ✅ DECISIÓN 2: EXTENDER AUTH CON BITÁCORA

### ¡BUENA NOTICIA! Ya existe AccessLog

El modelo ya está implementado en:
```
backend/apps/auth/infrastructure/models/mongo/access_log_model.py
```

### Modelo Actual de AccessLog:
```python
class AccessLog(Document):
    user_id: UUID           # FK a PostgreSQL
    ip_address: str         # IP del usuario
    user_agent: str         # Navegador/dispositivo
    process_name: str       # Acción realizada
    process_status: ProcessStatus  # Estado
    timestamp: datetime     # Marca de tiempo UTC
    
    class Settings:
        name = "access_logs"
```

### Campos Faltantes para Bitácora Completa:
```python
class SessionLog(Document):
    user_id: UUID
    session_id: str
    action: str
    action_details: Dict[str, Any] = {}
    ip_address: str
    user_agent: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    duration_seconds: float | None = None
```

---

## ✅ DECISIÓN 3: MongoDB ES CORRECTO

### ¿Por qué MongoDB y NO PostgreSQL?

| Característica | MongoDB         | PostgreSQL                |
| -------------- | --------------- | ------------------------- |
| Escrituras     | ⚡ Ultra rápido  | 🟡 Más lento               |
| Escalabilidad  | ⚡ Horizontal    | 🟡 Vertical                |
| Schema         | 🔄 Flexible      | 🔴 Rígido                  |
| Uso ideal      | Logs, auditoría | Relacional, transacciones |

### Ventajas MongoDB:
1. **Escritura masiva** - 1000+ eventos/segundo
2. **Schema flexible** - Cada acción puede tener datos diferentes
3. **TTL automático** - Puede expirar logs viejos
4. **Compresión** - Ocupa menos espacio
5. **Sharding** - Escalabilidad horizontal

### ✅ VEREDICTO: MongoDB ES CORRECTO

---

## ✅ DECISIÓN 4: ARQUITECTURA SERVICIOS → REPOSITORIOS

### Patrón Actual (CORRECTO):
```
API → Service → Repository → Database
```

### Ejemplo para Bitácora:
```python
# API
@router.post("/login")
async def login(dto: LoginDTO, service: AuthService):
    result = await service.login(dto)
    await session_log_service.log_action(user_id=result.user_id, action="login")
    return result

# Service
class SessionLogService:
    def __init__(self, repository: SessionLogRepository):
        self.repository = repository
    
    async def log_action(self, user_id: UUID, action: str, **kwargs):
        log = SessionLog(user_id=user_id, action=action, **kwargs)
        await self.repository.save(log)

# Repository
class SessionLogRepository:
    async def save(self, log: SessionLog):
        await log.insert()
```

### ✅ VEREDICTO: MANTENER ARQUITECTURA

---

## 🔗 RELACIÓN: USUARIOS (PostgreSQL) ↔ BITÁCORA (MongoDB)

### Arquitectura de Datos Híbrida

```
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (Relacional)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │   users     │     │   roles     │     │ user_roles  │        │
│  ├─────────────┤     ├─────────────┤     ├─────────────┤        │
│  │ id (PK)     │     │ id (PK)     │     │ user_id(FK) │        │
│  │ username    │     │ name        │     │ role_id(FK) │        │
│  │ email       │     │ description │     └─────────────┘        │
│  │ hashed_pass │     └─────────────┘                            │
│  │ is_active   │                                                │
│  │ created_at  │                                                │
│  └─────────────┘                                                │
│        │                                                        │
│        │ user_id (UUID)                                         │
└────────┼────────────────────────────────────────────────────────┘
         │
         │ Referencia cruzada (NO FK)
         │
┌────────┼────────────────────────────────────────────────────────┐
│        ▼                 MongoDB (NoSQL)                        │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│  │ access_logs │     │session_logs │     │ action_logs │        │
│  ├─────────────┤     ├─────────────┤     ├─────────────┤        │
│  │ _id (PK)    │     │ _id (PK)    │     │ _id (PK)    │        │
│  │ user_id     │     │ user_id     │     │ user_id     │        │
│  │ ip_address  │     │ session_id  │     │ action      │        │
│  │ user_agent  │     │ action      │     │ details     │        │
│  │ timestamp   │     │ endpoint    │     │ timestamp   │        │
│  └─────────────┘     │ status_code │     └─────────────┘        │
│                      └─────────────┘                            │
│                                                                 │
│  Índices:                                                       │
│  - user_id (asc) + timestamp (desc)                             │
│  - session_id (asc)                                             │
│  - action (asc)                                                 │
│  - timestamp (TTL: 90 días)                                     │
└─────────────────────────────────────────────────────────────────┘
```

### ¿Cómo funciona la relación?

#### 1. **Referencia Cruzada (NO Foreign Key)**
```python
# PostgreSQL: users.id (UUID)
user_id: UUID = "550e8400-e29b-41d4-a716-446655440000"

# MongoDB: access_logs.user_id (UUID almacenado como campo)
{
    "_id": ObjectId("..."),
    "user_id": "550e8400-e29b-41d4-a716-446655440000",  # Referencia
    "ip_address": "192.168.1.100",
    "timestamp": ISODate("2026-03-28T22:00:00Z")
}
```

#### 2. **Flujo de Consulta**
```
1. Cliente pide: GET /api/v1/users/{user_id}/logs
2. Service consulta: MongoDB.find(user_id = "{user_id}")
3. Service enriquece: Opcionalmente carga User de PostgreSQL
4. API retorna: Lista de logs + datos del usuario
```

---

## 🌐 API REST PARA BITÁCORA

### Endpoints Implementados:

#### 1. **Obtener logs de un usuario**
```http
GET /api/v1/users/{user_id}/logs
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- action: string (opcional) - Filtrar por acción
- limit: int (default: 100)
- offset: int (default: 0)
```

**Ejemplo Request:**
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/logs?start_date=2026-03-01&end_date=2026-03-28&action=login
```

**Ejemplo Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "total_logs": 45,
    "logs": [
        {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "action": "login",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "endpoint": "/api/v1/auth/login",
            "method": "POST",
            "status_code": 200,
            "response_time_ms": 150.5,
            "timestamp": "2026-03-28T22:00:00Z"
        },
        {
            "id": "660e8400-e29b-41d4-a716-446655440002",
            "action": "view_dashboard",
            "ip_address": "192.168.1.100",
            "endpoint": "/api/v1/dashboard",
            "method": "GET",
            "status_code": 200,
            "response_time_ms": 45.2,
            "timestamp": "2026-03-28T22:05:00Z"
        }
    ],
    "pagination": {
        "limit": 100,
        "offset": 0,
        "has_more": false
    }
}
```

#### 2. **Exportar logs a CSV/JSON**
```http
GET /api/v1/users/{user_id}/logs/export
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- format: string (csv|json|excel)
```

**Response:** Archivo descargable

#### 3. **Obtener resumen de actividad**
```http
GET /api/v1/users/{user_id}/logs/summary
```

**Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "period": {
        "start": "2026-03-01",
        "end": "2026-03-28"
    },
    "total_actions": 156,
    "actions_by_type": {
        "login": 45,
        "view_dashboard": 89,
        "update_profile": 12,
        "api_call": 10
    },
    "average_session_duration_minutes": 25.5,
    "unique_ips": 3,
    "devices": [
        {"name": "Chrome/Windows", "count": 120},
        {"name": "Safari/iOS", "count": 36}
    ],
    "peak_activity_hour": 14
}
```

#### 4. **Obtener detalles de sesión**
```http
GET /api/v1/sessions/{session_id}
```

**Response:**
```json
{
    "session_id": "sess_abc123xyz",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "started_at": "2026-03-28T22:00:00Z",
    "ended_at": "2026-03-28T22:45:00Z",
    "duration_minutes": 45,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "actions": [
        {
            "action": "login",
            "timestamp": "2026-03-28T22:00:00Z",
            "endpoint": "/api/v1/auth/login"
        },
        {
            "action": "view_dashboard",
            "timestamp": "2026-03-28T22:02:00Z",
            "endpoint": "/api/v1/dashboard"
        }
    ],
    "total_actions": 15,
    "status": "completed"
}
```

---

## 📐 IMPLEMENTACIÓN CÓDIGO

### Repositorio MongoDB:
```python
# backend/apps/auth/infrastructure/repositories/session_log_repository.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from beanie import PydanticObjectId
from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog

class SessionLogRepository:
    async def save(self, log: SessionLog) -> SessionLog:
        """Guarda un log en MongoDB"""
        await log.insert()
        return log
    
    async def get_by_user(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[SessionLog]:
        """Obtiene logs de un usuario por rango de fechas"""
        query = SessionLog.find(
            SessionLog.user_id == user_id,
            SessionLog.timestamp >= start_date,
            SessionLog.timestamp <= end_date
        )
        
        if action:
            query = query.find(SessionLog.action == action)
        
        return await query.sort(-SessionLog.timestamp).skip(offset).limit(limit).to_list()
    
    async def count_by_user(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Cuenta logs de un usuario"""
        return await SessionLog.find(
            SessionLog.user_id == user_id,
            SessionLog.timestamp >= start_date,
            SessionLog.timestamp <= end_date
        ).count()
```

### Servicio:
```python
# backend/apps/auth/application/services/session_log_service.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from apps.auth.infrastructure.repositories.session_log_repository import SessionLogRepository
from apps.auth.infrastructure.models.mongo.session_log_model import SessionLog

class SessionLogService:
    def __init__(self, repository: SessionLogRepository):
        self.repository = repository
    
    async def log_action(
        self,
        user_id: UUID,
        action: str,
        **kwargs
    ) -> SessionLog:
        """Registra una acción en la bitácora"""
        log = SessionLog(
            user_id=user_id,
            action=action,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        return await self.repository.save(log)
    
    async def get_user_logs(
        self,
        user_id: UUID,
        start_date: datetime,
        end_date: datetime,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> dict:
        """Obtiene logs de un usuario con paginación"""
        logs = await self.repository.get_by_user(
            user_id, start_date, end_date, action, limit, offset
        )
        total = await self.repository.count_by_user(user_id, start_date, end_date)
        
        return {
            "user_id": str(user_id),
            "total_logs": total,
            "logs": [log.dict() for log in logs],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        }
```

### Endpoint:
```python
# backend/apps/auth/api/v1/routes/session_log_routes.py
from fastapi import APIRouter, Depends, Query
from uuid import UUID
from datetime import datetime
from apps.auth.application.services.session_log_service import SessionLogService

router = APIRouter(prefix="/api/v1/users", tags=["Session Logs"])

@router.get("/{user_id}/logs")
async def get_user_logs(
    user_id: UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: SessionLogService = Depends()
):
    """Obtiene bitácora de accesos de un usuario"""
    return await service.get_user_logs(
        user_id, start_date, end_date, action, limit, offset
    )

@router.get("/{user_id}/logs/export")
async def export_user_logs(
    user_id: UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    format: str = Query("csv"),
    service: SessionLogService = Depends()
):
    """Exporta bitácora a CSV/JSON"""
    return await service.export_logs(user_id, start_date, end_date, format)

@router.get("/{user_id}/logs/summary")
async def get_user_activity_summary(
    user_id: UUID,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    service: SessionLogService = Depends()
):
    """Obtiene resumen de actividad del usuario"""
    return await service.get_activity_summary(user_id, start_date, end_date)
```

---

## 🗂️ FRAGMENTACIÓN DE LOGS EN MONGODB

### Arquitectura de Colecciones:

```
MongoDB
├── access_logs          ← Accesos HTTP (login, logout, requests)
│   ├── _id
│   ├── user_id
│   ├── ip_address
│   ├── user_agent
│   ├── endpoint
│   ├── method
│   ├── status_code
│   ├── response_time_ms
│   └── timestamp
│
├── session_logs         ← Sesiones completas (inicio → fin)
│   ├── _id
│   ├── user_id
│   ├── session_id
│   ├── started_at
│   ├── ended_at
│   ├── duration_minutes
│   ├── ip_address
│   ├── user_agent
│   └── total_actions
│
└── action_logs          ← Acciones específicas del usuario
    ├── _id
    ├── user_id
    ├── action
    ├── action_details
    ├── endpoint
    ├── status_code
    └── timestamp
```

### ¿Por qué fragmentar?

| Colección        | Contenido        | Escritura  | Lectura | Retención |
| ---------------- | ---------------- | ---------- | ------- | --------- |
| **access_logs**  | HTTP requests    | ⚡ Muy alta | 🟡 Media | 30 días   |
| **session_logs** | Sesiones         | 🟡 Media    | ⚡ Alta  | 90 días   |
| **action_logs**  | Acciones usuario | 🟡 Media    | ⚡ Alta  | 365 días  |

**Beneficios:**
- ✅ Cada colección optimizada para su caso de uso
- ✅ TTL diferente por tipo de log
- ✅ Índices específicos por consulta frecuente
- ✅ Compresión independiente

---

## 🌐 API REST - ENDPOINTS COMPLETOS

### TIPO 1: CONSULTA FULL POR USUARIO (Todos los logs)

#### Endpoint Principal:
```http
GET /api/v1/users/{user_id}/logs/full
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- limit: int (default: 50)
- offset: int (default: 0)
```

**Ejemplo Request:**
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/logs/full?start_date=2026-03-01&end_date=2026-03-28
```

**Ejemplo Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "period": {
        "start": "2026-03-01T00:00:00Z",
        "end": "2026-03-28T23:59:59Z"
    },
    "summary": {
        "total_access_logs": 150,
        "total_session_logs": 45,
        "total_action_logs": 320,
        "total_all_logs": 515
    },
    "logs": {
        "access_logs": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "type": "access",
                "ip_address": "192.168.1.100",
                "endpoint": "/api/v1/auth/login",
                "method": "POST",
                "status_code": 200,
                "response_time_ms": 150.5,
                "timestamp": "2026-03-28T22:00:00Z"
            }
        ],
        "session_logs": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440010",
                "type": "session",
                "session_id": "sess_abc123",
                "started_at": "2026-03-28T22:00:00Z",
                "ended_at": "2026-03-28T22:45:00Z",
                "duration_minutes": 45,
                "total_actions": 15
            }
        ],
        "action_logs": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440020",
                "type": "action",
                "action": "view_dashboard",
                "action_details": {"page": "overview"},
                "endpoint": "/api/v1/dashboard",
                "status_code": 200,
                "timestamp": "2026-03-28T22:02:00Z"
            }
        ]
    },
    "pagination": {
        "limit": 50,
        "offset": 0,
        "has_more": true
    }
}
```

---

### TIPO 2: CONSULTAS INDEPENDIENTES POR TIPO

#### 2.1 Solo Access Logs:
```http
GET /api/v1/users/{user_id}/logs/access
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- method: string (opcional) - GET, POST, PUT, DELETE
- status_code: int (opcional) - 200, 401, 500, etc.
- limit: int (default: 100)
- offset: int (default: 0)
```

**Ejemplo:**
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/logs/access?start_date=2026-03-01&end_date=2026-03-28&method=POST&status_code=200
```

**Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "log_type": "access",
    "total": 89,
    "logs": [
        {
            "id": "...",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "endpoint": "/api/v1/auth/login",
            "method": "POST",
            "status_code": 200,
            "response_time_ms": 150.5,
            "timestamp": "2026-03-28T22:00:00Z"
        }
    ]
}
```

#### 2.2 Solo Session Logs:
```http
GET /api/v1/users/{user_id}/logs/sessions
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- min_duration: int (opcional) - Minutos mínimos de sesión
- limit: int (default: 50)
- offset: int (default: 0)
```

**Ejemplo:**
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/logs/sessions?start_date=2026-03-01&end_date=2026-03-28&min_duration=30
```

**Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "log_type": "sessions",
    "total": 12,
    "logs": [
        {
            "id": "...",
            "session_id": "sess_abc123",
            "started_at": "2026-03-28T22:00:00Z",
            "ended_at": "2026-03-28T22:45:00Z",
            "duration_minutes": 45,
            "ip_address": "192.168.1.100",
            "total_actions": 15
        }
    ]
}
```

#### 2.3 Solo Action Logs:
```http
GET /api/v1/users/{user_id}/logs/actions
```

**Parámetros:**
```
- start_date: datetime (requerido)
- end_date: datetime (requerido)
- action: string (opcional) - Tipo de acción específica
- limit: int (default: 100)
- offset: int (default: 0)
```

**Ejemplo:**
```http
GET /api/v1/users/550e8400-e29b-41d4-a716-446655440000/logs/actions?start_date=2026-03-01&end_date=2026-03-28&action=view_dashboard
```

**Response:**
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "log_type": "actions",
    "total": 234,
    "logs": [
        {
            "id": "...",
            "action": "view_dashboard",
            "action_details": {"page": "overview", "section": "metrics"},
            "endpoint": "/api/v1/dashboard",
            "status_code": 200,
            "timestamp": "2026-03-28T22:02:00Z"
        },
        {
            "id": "...",
            "action": "update_profile",
            "action_details": {"field": "email", "old_value": "***", "new_value": "***"},
            "endpoint": "/api/v1/users/profile",
            "status_code": 200,
            "timestamp": "2026-03-28T22:10:00Z"
        }
    ]
}
```

---

## 📊 RESUMEN DE ENDPOINTS

| Endpoint                             | Descripción                      | Tipo Consulta                      |
| ------------------------------------ | -------------------------------- | ---------------------------------- |
| `GET /users/{user_id}/logs/full`     | **Todos los logs** de un usuario | FULL (access + sessions + actions) |
| `GET /users/{user_id}/logs/access`   | Solo **access logs**             | INDEPENDIENTE (HTTP requests)      |
| `GET /users/{user_id}/logs/sessions` | Solo **session logs**            | INDEPENDIENTE (sesiones)           |
| `GET /users/{user_id}/logs/actions`  | Solo **action logs**             | INDEPENDIENTE (acciones usuario)   |
| `GET /users/{user_id}/logs/summary`  | Resumen de actividad             | AGREGADO                           |
| `GET /users/{user_id}/logs/export`   | Exportar a CSV/JSON              | DESCARGA                           |
| `GET /sessions/{session_id}`         | Detalles de sesión               | ESPECÍFICO                         |

---

## 📋 PLAN DE IMPLEMENTACIÓN

### FASE 1: Extender Modelo (1 día)
- Crear modelo SessionLog en MongoDB
- Crear repositorio SessionLogRepository
- Crear servicio SessionLogService

### FASE 2: Middleware Auditoría (1 día)
- Crear AuditMiddleware para logging automático
- Registrar en main.py

### FASE 3: API Consulta (1 día)
- GET /users/{user_id}/logs/full
- GET /users/{user_id}/logs/access
- GET /users/{user_id}/logs/sessions
- GET /users/{user_id}/logs/actions
- GET /users/{user_id}/logs/export
- GET /users/{user_id}/logs/summary
- GET /sessions/{session_id}

### FASE 4: Testing (1 día)
- Tests unitarios
- Tests de integración

---

**Autor:** Cline (AI Assistant - Arquitecto de Software)
**Fecha:** 2026-03-28
**Estado:** ✅ LISTO PARA APROBACIÓN E IMPLEMENTACIÓN
