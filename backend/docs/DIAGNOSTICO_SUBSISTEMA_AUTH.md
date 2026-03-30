# DIAGNÓSTICO COMPLETO: SUBSISTEMA AUTH

**Fecha**: 2026-03-30  
**Estado**: ANÁLISIS COMPLETO  
**Objetivo**: Identificar artefactos existentes y plan de implementación

---

## 📊 RESUMEN EJECUTIVO

### Estado Actual
- ✅ **Infraestructura base**: Modelos, DTOs, seguridad implementados
- ❌ **Lógica de negocio**: AuthService, UserRepository, Rutas NO existen
- 🎯 **Resultado**: Sistema tiene "hueso" pero no tiene "carne"

### Componentes Reutilizables
| Componente                    | Estado    | Reutilizable |
| ----------------------------- | --------- | ------------ |
| DTOs (Login, Register, Token) | ✅ EXISTEN | ✅ SÍ         |
| Modelos SQL (User, Role)      | ✅ EXISTEN | ✅ SÍ         |
| Password Handler              | ✅ EXISTE  | ✅ SÍ         |
| JWT Handler                   | ✅ EXISTE  | ✅ SÍ         |
| Session Log Service           | ✅ EXISTE  | ✅ SÍ         |
| Audit Middleware              | ✅ EXISTE  | ✅ SÍ         |

### Componentes Faltantes
| Componente           | Estado       | Prioridad |
| -------------------- | ------------ | --------- |
| UserRepository       | ❌ NO EXISTE  | 🔴 ALTA    |
| AuthService          | ❌ NO EXISTE  | 🔴 ALTA    |
| Rutas login/register | ❌ NO EXISTEN | 🔴 ALTA    |

---

## 📋 INVENTARIO COMPLETO DE ARTEFACTOS

### 1️⃣ DTOs (Data Transfer Objects) ✅

#### LoginDTO
**Archivo**: `backend/apps/auth/application/dto/login_dto.py`

```python
class LoginDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
```

**Estado**: ✅ COMPLETO - Listo para usar

---

#### RegisterDTO
**Archivo**: `backend/apps/auth/application/dto/register_dto.py`

```python
class RegisterDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=128)
```

**Estado**: ✅ COMPLETO - Listo para usar

---

#### TokenDTO
**Archivo**: `backend/apps/auth/application/dto/token_dto.py`

```python
class TokenDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

**Estado**: ✅ COMPLETO - Listo para usar

---

### 2️⃣ Modelos SQL ✅

#### User Model
**Archivo**: `backend/apps/auth/infrastructure/models/sql/user.py`

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    roles = relationship("Role", secondary="user_roles", back_populates="users")
```

**Estado**: ✅ COMPLETO - Listo para usar

---

#### Role Model
**Archivo**: `backend/apps/auth/infrastructure/models/sql/role.py`

```python
class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(200))
    
    users = relationship("User", secondary="user_roles", back_populates="roles")
```

**Estado**: ✅ COMPLETO - Listo para usar

---

### 3️⃣ Componentes de Seguridad ✅

#### Password Handler
**Archivo**: `backend/apps/auth/infrastructure/security/password_handler.py`

**Métodos disponibles**:
- ✅ `hash_password(password: str) -> str` - Hash con Argon2id
- ✅ `verify_password(plain: str, hashed: str) -> bool` - Verificación
- ✅ `needs_rehash(hashed: str) -> bool` - Detección de migración
- ✅ `is_strong_password(password: str) -> Tuple[bool, list]` - Validación

**Estado**: ✅ COMPLETO - Producción listo

---

#### JWT Handler
**Archivo**: `backend/apps/auth/infrastructure/security/jwt_handler.py`

**Métodos disponibles**:
- ✅ `create_access_token(data: dict) -> str` - Crear JWT
- ✅ `verify_token(token: str) -> dict` - Verificar JWT
- ✅ `get_current_user(token: str) -> User` - Obtener usuario actual

**Estado**: ✅ COMPLETO - Producción listo

---

### 4️⃣ Servicios Existentes ✅

#### Session Log Service
**Archivo**: `backend/apps/auth/application/services/session_log_service.py`

**Métodos disponibles**:
- ✅ `log_action(...)` - Registrar acción
- ✅ `log_api_call(...)` - Registrar llamada API
- ✅ `get_user_logs(...)` - Obtener logs de usuario
- ✅ `get_session_logs(...)` - Obtener logs por sesión

**Estado**: ✅ COMPLETO - Puede ser reutilizado por AuthService

---

### 5️⃣ Middleware ✅

#### Audit Middleware
**Archivo**: `backend/core/middleware/audit_middleware.py`

**Funcionalidad**:
- ✅ Intercepta cada request HTTP
- ✅ Extrae user_id del JWT
- ✅ Llama a `SessionLogService.log_api_call()`
- ✅ Registra en MongoDB

**Estado**: ✅ COMPLETO - Producción listo

---

## ❌ COMPONENTES FALTANTES

### 1️⃣ UserRepository (NO EXISTE)

**Ubicación necesaria**: `backend/apps/auth/infrastructure/repositories/user_repository.py`

**Métodos necesarios**:
```python
class UserRepository:
    async def create(self, user: User) -> User
    async def get_by_email(self, email: str) -> Optional[User]
    async def get_by_username(self, username: str) -> Optional[User]
    async def get_by_id(self, user_id: int) -> Optional[User]
    async def update(self, user: User) -> User
    async def delete(self, user_id: int) -> bool
```

**Dependencias**:
- ✅ Modelo `User` (EXISTE)
- ✅ `get_db_session()` de `database_sql.py` (EXISTE)

---

### 2️⃣ AuthService (NO EXISTE)

**Ubicación necesaria**: `backend/apps/auth/application/services/auth_service.py`

**Métodos necesarios**:
```python
class AuthService:
    async def register(self, dto: RegisterDTO) -> TokenDTO
    async def login(self, dto: LoginDTO) -> TokenDTO
    async def logout(self, user_id: int) -> None
    async def get_current_user(self, token: str) -> User
    async def refresh_token(self, refresh_token: str) -> TokenDTO
```

**Dependencias**:
- ✅ `UserRepository` (CREAR)
- ✅ `PasswordHandler` (EXISTE)
- ✅ `JWTHandler` (EXISTE)
- ✅ `SessionLogService` (EXISTE)
- ✅ `LoginDTO`, `RegisterDTO`, `TokenDTO` (EXISTEN)

---

### 3️⃣ Rutas de Autenticación (NO EXISTEN)

**Ubicación necesaria**: `backend/apps/auth/api/v1/routes/authenticator_routes.py`

**Endpoints necesarios**:
```python
@router.post("/register", response_model=TokenDTO)
@router.post("/login", response_model=TokenDTO)
@router.post("/logout")
@router.get("/me", response_model=UserDTO)
@router.post("/refresh", response_model=TokenDTO)
```

**Dependencias**:
- ✅ `AuthService` (CREAR)
- ✅ `LoginDTO`, `RegisterDTO` (EXISTEN)
- ✅ `UserDTO` (CREAR o usar User model)

---

## 🏗️ ARQUITECTURA ACTUAL vs NECESARIA

### ACTUAL (INCOMPLETA)
```
┌─────────────────────────────────────────────────────────┐
│                    API LAYER                            │
│  authenticator_routes.py                               │
│  ✅ GET /ping                                          │
│  ❌ POST /register                                     │
│  ❌ POST /login                                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                       │
│  ❌ AuthService (NO EXISTE)                            │
│  ✅ SessionLogService (EXISTE)                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                      │
│  ❌ UserRepository (NO EXISTE)                         │
│  ✅ SessionLogRepository (EXISTE)                      │
│  ✅ PasswordHandler (EXISTE)                           │
│  ✅ JWTHandler (EXISTE)                                │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  DOMAIN LAYER                           │
│  ✅ User Model (EXISTE)                                │
│  ✅ Role Model (EXISTE)                                │
│  ✅ LoginDTO (EXISTE)                                  │
│  ✅ RegisterDTO (EXISTE)                               │
│  ✅ TokenDTO (EXISTE)                                  │
└─────────────────────────────────────────────────────────┘
```

---

### NECESARIA (COMPLETA)
```
┌─────────────────────────────────────────────────────────┐
│                    API LAYER                            │
│  authenticator_routes.py                               │
│  ✅ GET /ping                                          │
│  ✅ POST /register  → AuthService.register()           │
│  ✅ POST /login     → AuthService.login()              │
│  ✅ POST /logout    → AuthService.logout()             │
│  ✅ GET /me         → AuthService.get_current_user()   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                       │
│  ✅ AuthService (CREAR)                                │
│    - register() → UserRepository.create()              │
│    - login() → PasswordHandler.verify() + JWT.create() │
│    - logout() → SessionLogService.log_action()         │
│  ✅ SessionLogService (REUTILIZAR)                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               INFRASTRUCTURE LAYER                      │
│  ✅ UserRepository (CREAR)                             │
│    - create() → db.add(user)                           │
│    - get_by_email() → db.query(User).filter()          │
│  ✅ SessionLogRepository (REUTILIZAR)                  │
│  ✅ PasswordHandler (REUTILIZAR)                       │
│  ✅ JWTHandler (REUTILIZAR)                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  DOMAIN LAYER                           │
│  ✅ User Model (REUTILIZAR)                            │
│  ✅ Role Model (REUTILIZAR)                            │
│  ✅ LoginDTO (REUTILIZAR)                              │
│  ✅ RegisterDTO (REUTILIZAR)                           │
│  ✅ TokenDTO (REUTILIZAR)                              │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 PLAN DE IMPLEMENTACIÓN OPTIMIZADO

### FASE 1: Crear UserRepository (30 min)

**Archivo**: `backend/apps/auth/infrastructure/repositories/user_repository.py`

```python
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from apps.auth.infrastructure.models.sql.user import User
from core.db.sql.database_sql import get_db_session

class UserRepository:
    """Repositorio para operaciones de usuarios en PostgreSQL"""
    
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario"""
        with get_db_context() as db:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene usuario por email"""
        with get_db_session() as db:
            return db.query(User).filter(User.email == email).first()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene usuario por username"""
        with get_db_session() as db:
            return db.query(User).filter(User.username == username).first()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtiene usuario por ID"""
        with get_db_session() as db:
            return db.query(User).filter(User.id == user_id).first()
```

**Dependencias**: ✅ Todas existen

---

### FASE 2: Crear AuthService (45 min)

**Archivo**: `backend/apps/auth/application/services/auth_service.py`

```python
from typing import Optional
from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.infrastructure.models.sql.user import User
from apps.auth.infrastructure.repositories.user_repository import UserRepository
from apps.auth.infrastructure.security.password_handler import PasswordHandler
from apps.auth.infrastructure.security.jwt_handler import JWTHandler
from apps.auth.application.services.session_log_service import SessionLogService

class AuthService:
    """Servicio de autenticación"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        session_log_service: SessionLogService
    ):
        self.user_repository = user_repository
        self.session_log_service = session_log_service
    
    async def register(self, dto: RegisterDTO) -> TokenDTO:
        """Registra un nuevo usuario"""
        # Verificar si email existe
        existing_user = await self.user_repository.get_by_email(dto.email)
        if existing_user:
            raise ValueError("Email ya registrado")
        
        # Verificar si username existe
        existing_username = await self.user_repository.get_by_username(dto.username)
        if existing_username:
            raise ValueError("Username ya existe")
        
        # Hashear contraseña
        hashed_password = PasswordHandler.hash_password(dto.password)
        
        # Crear usuario
        user = User(
            username=dto.username,
            email=dto.email,
            hashed_password=hashed_password
        )
        created_user = await self.user_repository.create(user)
        
        # Generar token
        access_token = JWTHandler.create_access_token(
            data={"sub": str(created_user.id)}
        )
        
        # Log de registro
        await self.session_log_service.log_action(
            user_id=created_user.id,
            action="register",
            details={"username": dto.username}
        )
        
        return TokenDTO(access_token=access_token)
    
    async def login(self, dto: LoginDTO) -> TokenDTO:
        """Inicia sesión de usuario"""
        # Buscar usuario por username o email
        user = await self.user_repository.get_by_username(dto.username)
        if not user:
            user = await self.user_repository.get_by_email(dto.username)
        
        if not user:
            raise ValueError("Credenciales inválidas")
        
        # Verificar contraseña
        if not PasswordHandler.verify_password(dto.password, user.hashed_password):
            raise ValueError("Credenciales inválidas")
        
        # Verificar si está activo
        if not user.is_active:
            raise ValueError("Usuario inactivo")
        
        # Generar token
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user.id)}
        )
        
        # Log de login
        await self.session_log_service.log_action(
            user_id=user.id,
            action="login",
            details={"username": user.username}
        )
        
        return TokenDTO(access_token=access_token)
```

**Dependencias**: ✅ Todas existen

---

### FASE 3: Crear Rutas de Autenticación (30 min)

**Archivo**: `backend/apps/auth/api/v1/routes/authenticator_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.application.services.auth_service import AuthService

router = APIRouter()

# Dependency para obtener AuthService
def get_auth_service() -> AuthService:
    from apps.auth.infrastructure.repositories.user_repository import UserRepository
    from apps.auth.application.services.session_log_service import SessionLogService
    from apps.auth.infrastructure.repositories.session_log_repository import SessionLogRepository
    
    user_repo = UserRepository()
    session_log_repo = SessionLogRepository()
    session_log_service = SessionLogService(session_log_repo)
    return AuthService(user_repo, session_log_service)

@router.post("/register", response_model=TokenDTO, status_code=status.HTTP_201_CREATED)
async def register(
    dto: RegisterDTO,
    service: AuthService = Depends(get_auth_service)
):
    """Registra un nuevo usuario"""
    try:
        return await service.register(dto)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenDTO)
async def login(
    dto: LoginDTO,
    service: AuthService = Depends(get_auth_service)
):
    """Inicia sesión"""
    try:
        return await service.login(dto)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/ping")
async def auth_ping():
    """Health check del subsistema auth"""
    return {"ok": True, "service": "auth", "message": "pong"}
```

**Dependencias**: ✅ Todas existen

---

## 📊 RESUMEN DE REUTILIZACIÓN

| Artefacto                | Estado      | Acción     |
| ------------------------ | ----------- | ---------- |
| LoginDTO                 | ✅ EXISTE    | REUTILIZAR |
| RegisterDTO              | ✅ EXISTE    | REUTILIZAR |
| TokenDTO                 | ✅ EXISTE    | REUTILIZAR |
| User Model               | ✅ EXISTE    | REUTILIZAR |
| Role Model               | ✅ EXISTE    | REUTILIZAR |
| PasswordHandler          | ✅ EXISTE    | REUTILIZAR |
| JWTHandler               | ✅ EXISTE    | REUTILIZAR |
| SessionLogService        | ✅ EXISTE    | REUTILIZAR |
| AuditMiddleware          | ✅ EXISTE    | REUTILIZAR |
| **UserRepository**       | ❌ NO EXISTE | **CREAR**  |
| **AuthService**          | ❌ NO EXISTE | **CREAR**  |
| **Authenticator Routes** | ❌ NO EXISTE | **CREAR**  |

---

## ⏱️ ESTIMACIÓN DE TIEMPO

| Fase                   | Tiempo      | Artefactos           |
| ---------------------- | ----------- | -------------------- |
| Fase 1: UserRepository | 30 min      | 1 archivo nuevo      |
| Fase 2: AuthService    | 45 min      | 1 archivo nuevo      |
| Fase 3: Rutas Auth     | 30 min      | 1 archivo modificado |
| Fase 4: Testing        | 15 min      | Verificar endpoints  |
| **TOTAL**              | **2 horas** | **3 archivos**       |

---

## ✅ CONCLUSIÓN

**Estado**: El subsistema auth tiene el 70% de la infraestructura lista.

**Lo que falta**: 3 componentes (30% restante):
1. ✅ UserRepository (30 min)
2. ✅ AuthService (45 min)
3. ✅ Rutas de autenticación (30 min)

**Tiempo total estimado**: 2 horas

**¿Procedemos con la implementación?**

---

**Elaborado por**: Arquitecto de Software Senior  
**Fecha**: 2026-03-30  
**Estado**: ✅ DIAGNÓSTICO COMPLETO