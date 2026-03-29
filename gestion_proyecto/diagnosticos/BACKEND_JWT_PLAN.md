# 🔐 DIAGNÓSTICO Y PLAN: BACKEND PARA JWT Y FRONTEND - TipsterByte FX

**Fecha:** 2026-03-28
**Estado:** LISTO PARA IMPLEMENTACIÓN
**Prioridad:** 🔴 CRÍTICO - Bloqueante para frontend

---

## 📋 RESUMEN EJECUTIVO

### Estado Actual:
- ✅ **Backend FastAPI** sólido con arquitectura DDD
- ✅ **Modelos User/Role** existen en SQL
- ❌ **Módulo auth INCOMPLETO** - Solo endpoint `/ping`
- ❌ **NO hay JWT** implementado
- ❌ **NO hay CORS** configurado
- ❌ **NO hay middleware de autenticación**
- ❌ **NO hay endpoints de login/register**

### Objetivo:
Preparar el backend para que **cualquier frontend** (Angular, React, Vue, Mobile) pueda:
1. Autenticarse via JWT
2. Autorizar acciones por roles
3. Comunicarse sin restricciones CORS
4. Gestionar usuarios (CRUD completo)

---

## 🔍 ANÁLISIS DEL BACKEND ACTUAL

### 1. Estructura del Proyecto

```
backend/
├── apps/
│   ├── auth/                    # ⚠️ INCOMPLETO - Solo ping
│   │   ├── api/v1/
│   │   │   ├── authenticator_controller.py
│   │   │   └── routes/
│   │   │       └── authenticator_routes.py  # Solo /ping
│   │   ├── infrastructure/
│   │   │   └── models/sql/
│   │   │       ├── user.py      # ✅ MODELO EXISTE
│   │   │       ├── role.py      # ✅ MODELO EXISTE
│   │   │       └── user_roles.py # ✅ TABLA PIVOTE
│   │   └── ...
│   ├── leagues_manager/         # ✅ COMPLETO
│   └── platform_config/         # ✅ COMPLETO
├── core/
│   ├── db/sql/database_sql.py   # ✅ SQLAlchemy configurado
│   ├── middleware.py             # ⚠️ Solo TraceIDMiddleware
│   ├── exceptions/              # ✅ Excepciones personalizadas
│   └── ...
└── main_init_web_server.py      # ✅ FastAPI configurado
```

### 2. Rutas API Registradas en main_init_web_server.py

```python
# Rutas actuales:
app.include_router(system_router, prefix="/system")
app.include_router(system_router, prefix="/api/v1/system")
app.include_router(auth_router, prefix="/api/v1/auth")      # ⚠️ Solo /ping
app.include_router(scheduler_router, prefix="/api/v1")
app.include_router(leagues_router)                           # /api/v1/leagues
app.include_router(platform_config_router)                   # /api/v1/platform-config
```

### 3. Módulo Auth Actual

#### authenticator_routes.py:
```python
@router.get("/ping")
async def auth_ping():
    return {"ok": True, "service": "auth", "message": "pong"}
```

#### ❌ LO QUE FALTA:
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/refresh` - Renovar token
- `GET /api/v1/auth/me` - Perfil del usuario
- `POST /api/v1/auth/logout` - Cerrar sesión
- `GET /api/v1/auth/users` - Listar usuarios (admin)
- `PATCH /api/v1/auth/users/{id}` - Actualizar usuario
- `DELETE /api/v1/auth/users/{id}` - Eliminar usuario (admin)

### 4. Modelos SQL Existentes

#### User Model (backend/apps/auth/infrastructure/models/sql/user.py):
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    origin_record = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    roles = relationship("Role", secondary="user_roles", back_populates="users")
```

#### Role Model (backend/apps/auth/infrastructure/models/sql/role.py):
```python
class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    users = relationship("User", secondary="user_roles", back_populates="roles")
```

#### ✅ MODELOS LISTOS - No necesitan cambios

### 5. Dependencias Actuales (requirements.txt)

```txt
# ✅ Backend stack
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy>=1.4
alembic>=1.8

# ❌ FALTA JWT
# python-jose[cryptography]   # JWT tokens
# passlib[bcrypt]             # Hash de contraseñas
# python-multipart            # Formularios de login
```

### 6. CORS Configuración

```python
# main_init_web_server.py - NO HAY CORS CONFIGURADO
app = FastAPI(...)

# ❌ FALTA:
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(CORSMiddleware, ...)
```

---

## 🎯 PLAN DE IMPLEMENTACIÓN COMPLETO

### FASE 1: Backend JWT (2-3 días) 🔴 CRÍTICO

#### 1.1 Agregar Dependencias

```bash
# requirements.txt (agregar)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

#### 1.2 Estructura de Archivos a Crear/Modificar

```
backend/apps/auth/
├── api/v1/
│   ├── routes/
│   │   └── authenticator_routes.py    # 🔄 MODIFICAR - Agregar endpoints
│   └── dtos/                          # 📁 NUEVO
│       ├── __init__.py
│       ├── login_dto.py               # 📄 NUEVO
│       ├── register_dto.py            # 📄 NUEVO
│       ├── token_dto.py               # 📄 NUEVO
│       └── user_dto.py                # 📄 NUEVO
├── application/
│   └── services/                      # 📁 NUEVO
│       ├── __init__.py
│       └── auth_service.py            # 📄 NUEVO
├── domain/
│   ├── entities/                      # 📁 NUEVO
│   │   ├── __init__.py
│   │   └── user_entity.py             # 📄 NUEVO
│   └── repositories/                  # 📁 NUEVO
│       ├── __init__.py
│       └── i_auth_repository.py       # 📄 NUEVO
└── infrastructure/
    ├── repositories/                  # 📁 NUEVO
    │   ├── __init__.py
    │   └── sql_auth_repository.py     # 📄 NUEVO
    └── security/                      # 📁 NUEVO
        ├── __init__.py
        ├── jwt_handler.py             # 📄 NUEVO
        └── password_handler.py        # 📄 NUEVO
```

#### 1.3 Archivos Core a Crear/Modificar

```
backend/core/
├── middleware/
│   ├── __init__.py                    # 🔄 MODIFICAR
│   └── auth_middleware.py             # 📄 NUEVO
├── dependencies/
│   ├── __init__.py                    # 📁 NUEVO
│   └── auth_dependencies.py          # 📄 NUEVO
└── config.py                          # 🔄 MODIFICAR - Agregar JWT_SECRET
```

#### 1.4 main_init_web_server.py

```python
# 🔄 MODIFICAR - Agregar CORS
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",      # Angular dev
        "http://localhost:3000",      # React dev
        "http://localhost:8080",      # Vue dev
        "https://tipsterbyte.com"     # Producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### FASE 2: Implementación Detallada

#### 2.1 JWT Handler (backend/apps/auth/infrastructure/security/jwt_handler.py)

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from core.config import settings

class JWTHandler:
    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWTHandler.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=JWTHandler.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, JWTHandler.SECRET_KEY, algorithm=JWTHandler.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
            return payload
        except JWTError:
            return None
```

#### 2.2 Password Handler (backend/apps/auth/infrastructure/security/password_handler.py)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class PasswordHandler:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
```

#### 2.3 Auth Service (backend/apps/auth/application/services/auth_service.py)

```python
from typing import Optional
from apps.auth.infrastructure.security.jwt_handler import JWTHandler
from apps.auth.infrastructure.security.password_handler import PasswordHandler
from apps.auth.infrastructure.repositories.sql_auth_repository import SQLAuthRepository
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.application.dto.user_dto import UserDTO

class AuthService:
    def __init__(self, repository: SQLAuthRepository):
        self.repository = repository
    
    async def login(self, username: str, password: str) -> Optional[TokenDTO]:
        user = await self.repository.get_user_by_username(username)
        if not user:
            return None
        
        if not PasswordHandler.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Crear tokens
        access_token = JWTHandler.create_access_token(
            data={"sub": str(user.id), "username": user.username, "roles": [r.name for r in user.roles]}
        )
        refresh_token = JWTHandler.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def register(self, username: str, email: str, password: str) -> Optional[UserDTO]:
        # Verificar si existe
        existing = await self.repository.get_user_by_username(username)
        if existing:
            return None
        
        # Hash password
        hashed = PasswordHandler.hash_password(password)
        
        # Crear usuario
        user = await self.repository.create_user(username, email, hashed)
        
        return UserDTO.from_orm(user)
    
    async def get_current_user(self, token: str) -> Optional[UserDTO]:
        payload = JWTHandler.verify_token(token)
        if not payload:
            return None
        
        user_id = int(payload.get("sub"))
        user = await self.repository.get_user_by_id(user_id)
        
        return UserDTO.from_orm(user) if user else None
```

#### 2.4 Endpoints de Auth (backend/apps/auth/api/v1/routes/authenticator_routes.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from apps.auth.application.dto.token_dto import TokenDTO
from apps.auth.application.dto.user_dto import UserDTO
from apps.auth.application.dto.login_dto import LoginDTO
from apps.auth.application.dto.register_dto import RegisterDTO
from apps.auth.application.services.auth_service import AuthService
from apps.auth.infrastructure.repositories.sql_auth_repository import SQLAuthRepository
from core.db.sql.database_sql import get_db_session

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_auth_service(db = Depends(get_db_session)):
    repo = SQLAuthRepository(db)
    return AuthService(repo)

@router.post("/login", response_model=TokenDTO)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service)
):
    """Iniciar sesión y obtener JWT tokens"""
    token = await service.login(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/register", response_model=UserDTO, status_code=status.HTTP_201_CREATED)
async def register(
    dto: RegisterDTO,
    service: AuthService = Depends(get_auth_service)
):
    """Registrar nuevo usuario"""
    user = await service.register(dto.username, dto.email, dto.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya existe"
        )
    return user

@router.get("/me", response_model=UserDTO)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: AuthService = Depends(get_auth_service)
):
    """Obtener perfil del usuario autenticado"""
    user = await service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    return user

@router.post("/refresh", response_model=TokenDTO)
async def refresh_token(
    refresh_token: str,
    service: AuthService = Depends(get_auth_service)
):
    """Renovar access token usando refresh token"""
    # Implementar lógica de refresh
    pass

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme)
):
    """Cerrar sesión (invalidar token)"""
    # En JWT stateless, el cliente simplemente elimina el token
    return {"message": "Sesión cerrada exitosamente"}
```

#### 2.5 Middleware de Autenticación (backend/core/middleware/auth_middleware.py)

```python
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from apps.auth.infrastructure.security.jwt_handler import JWTHandler

security = HTTPBearer()

async def get_current_user_from_token(request: Request):
    """Dependency para obtener usuario actual desde JWT"""
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )
    
    token = auth.split(" ")[1]
    payload = JWTHandler.verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    return payload

def require_role(role: str):
    """Dependency para verificar rol específico"""
    async def role_checker(request: Request):
        user = await get_current_user_from_token(request)
        if role not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere rol: {role}"
            )
        return user
    return role_checker
```

#### 2.6 Configuración JWT (backend/core/config.py)

```python
# 🔄 AGREGAR al archivo existente
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... configuraciones existentes ...
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"  # Cambiar en .env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:4200",
        "http://localhost:3000",
        "http://localhost:8080"
    ]

settings = Settings()
```

#### 2.7 Variables de Entorno (.env)

```bash
# .env (agregar)
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:4200","http://localhost:3000"]
```

---

### FASE 3: Protección de Rutas Existentes

#### 3.1 Proteger Rutas de Platform Config

```python
# backend/apps/platform_config/api/v1/routes/platform_config_routes.py
from core.middleware.auth_middleware import get_current_user_from_token, require_role

@router.post("/scheduled-processes", response_model=ScheduledProcessConfigDTO)
async def crear_scheduled_process(
    dto: ScheduledProcessConfigCreateDTO,
    service: PlatformConfigService = Depends(get_service),
    current_user = Depends(require_role("admin"))  # ⭐ PROTEGIDO
):
    """Solo admins pueden crear procesos"""
    return service.registrar_scheduled_process_config(dto)

@router.get("/scheduled-processes", response_model=List[ScheduledProcessConfigDTO])
async def listar_scheduled_processes(
    enabled_only: bool = False,
    service: PlatformConfigService = Depends(get_service),
    current_user = Depends(get_current_user_from_token)  # ⭐ PROTEGIDO
):
    """Cualquier usuario autenticado puede ver procesos"""
    return service.obtener_scheduled_process_configs(enabled_only=enabled_only)
```

#### 3.2 Proteger Rutas de Leagues Manager

```python
# backend/apps/leagues_manager/api/v1/routes/soccer_league_routes.py
from core.middleware.auth_middleware import get_current_user_from_token

@router.post("/continentes", response_model=ContinenteDTO)
async def crear_continente(
    dto: ContinenteCreateDTO,
    service: LeaguesService = Depends(get_service),
    current_user = Depends(get_current_user_from_token)  # ⭐ PROTEGIDO
):
    """Requiere autenticación para crear"""
    return service.registrar_continente(dto)

@router.get("/continentes", response_model=List[ContinenteDTO])
async def obtener_continentes(
    service: LeaguesService = Depends(get_service)
    # ⭐ PÚBLICO - No requiere autenticación
):
    """Cualquiera puede ver continentes"""
    return service.obtener_todos_los_continentes()
```

---

## 📊 RESUMEN DE ARCHIVOS

### Archivos a CREAR (17 archivos):

| #   | Archivo                                                        | Descripción          |
| --- | -------------------------------------------------------------- | -------------------- |
| 1   | `apps/auth/application/dto/__init__.py`                        | Init DTOs            |
| 2   | `apps/auth/application/dto/login_dto.py`                       | DTO para login       |
| 3   | `apps/auth/application/dto/register_dto.py`                    | DTO para registro    |
| 4   | `apps/auth/application/dto/token_dto.py`                       | DTO para tokens      |
| 5   | `apps/auth/application/dto/user_dto.py`                        | DTO para usuario     |
| 6   | `apps/auth/application/services/__init__.py`                   | Init services        |
| 7   | `apps/auth/application/services/auth_service.py`               | Lógica de auth       |
| 8   | `apps/auth/domain/entities/__init__.py`                        | Init entities        |
| 9   | `apps/auth/domain/entities/user_entity.py`                     | Entidad de dominio   |
| 10  | `apps/auth/domain/repositories/__init__.py`                    | Init repos           |
| 11  | `apps/auth/domain/repositories/i_auth_repository.py`           | Interfaz repositorio |
| 12  | `apps/auth/infrastructure/repositories/__init__.py`            | Init repos           |
| 13  | `apps/auth/infrastructure/repositories/sql_auth_repository.py` | Implementación SQL   |
| 14  | `apps/auth/infrastructure/security/__init__.py`                | Init security        |
| 15  | `apps/auth/infrastructure/security/jwt_handler.py`             | Manejo de JWT        |
| 16  | `apps/auth/infrastructure/security/password_handler.py`        | Hash de passwords    |
| 17  | `core/middleware/auth_middleware.py`                           | Middleware de auth   |

### Archivos a MODIFICAR (5 archivos):

| #   | Archivo                                           | Cambio                    |
| --- | ------------------------------------------------- | ------------------------- |
| 1   | `requirements.txt`                                | Agregar dependencias JWT  |
| 2   | `apps/auth/api/v1/routes/authenticator_routes.py` | Agregar endpoints auth    |
| 3   | `main_init_web_server.py`                         | Agregar CORS middleware   |
| 4   | `core/config.py`                                  | Agregar configuración JWT |
| 5   | `.env`                                            | Agregar variables JWT     |

---

## 🧪 TESTING

### Tests a Crear:

```
backend/apps/auth/tests/
├── __init__.py
├── test_auth_service.py        # Tests del servicio
├── test_jwt_handler.py         # Tests de JWT
├── test_password_handler.py    # Tests de password
└── test_auth_endpoints.py      # Tests de endpoints
```

### Ejemplos de Tests:

```python
# test_jwt_handler.py
def test_create_access_token():
    token = JWTHandler.create_access_token({"sub": "1", "username": "test"})
    assert token is not None
    assert isinstance(token, str)

def test_verify_token():
    token = JWTHandler.create_access_token({"sub": "1"})
    payload = JWTHandler.verify_token(token)
    assert payload is not None
    assert payload["sub"] == "1"

def test_invalid_token():
    payload = JWTHandler.verify_token("invalid-token")
    assert payload is None
```

---

## 🚀 ORDEN DE EJECUCIÓN

### Día 1: Setup y Core
1. ✅ Agregar dependencias a requirements.txt
2. ✅ Crear jwt_handler.py
3. ✅ Crear password_handler.py
4. ✅ Crear DTOs (login, register, token, user)
5. ✅ Configurar JWT en config.py
6. ✅ Agregar variables a .env

### Día 2: Services y Repository
7. ✅ Crear i_auth_repository.py (interfaz)
8. ✅ Crear sql_auth_repository.py (implementación)
9. ✅ Crear auth_service.py
10. ✅ Crear user_entity.py

### Día 3: API y Middleware
11. ✅ Modificar authenticator_routes.py (agregar endpoints)
12. ✅ Crear auth_middleware.py
13. ✅ Modificar main_init_web_server.py (agregar CORS)
14. ✅ Proteger rutas existentes
15. ✅ Crear tests

### Día 4: Testing y Validación
16. ✅ Ejecutar tests unitarios
17. ✅ Ejecutar tests de integración
18. ✅ Probar endpoints con Postman/curl
19. ✅ Documentar en Swagger/ReDoc

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Backend JWT:
- [ ] Dependencias instaladas (python-jose, passlib, python-multipart)
- [ ] JWT handler creado y funcional
- [ ] Password handler creado y funcional
- [ ] DTOs creados (login, register, token, user)
- [ ] Auth service creado
- [ ] Auth repository creado
- [ ] Endpoints de auth creados (/login, /register, /me, /refresh, /logout)
- [ ] Middleware de auth creado
- [ ] CORS configurado en main.py
- [ ] Variables de entorno configuradas (.env)
- [ ] Tests unitarios pasando
- [ ] Tests de integración pasando

### Protección de Rutas:
- [ ] Rutas de platform_config protegidas
- [ ] Rutas de leagues_manager protegidas (las que requieren auth)
- [ ] Rutas públicas accesibles sin auth
- [ ] Roles funcionando correctamente

### Frontend Ready:
- [ ] CORS permite localhost:4200 (Angular)
- [ ] CORS permite localhost:3000 (React)
- [ ] CORS permite localhost:8080 (Vue)
- [ ] Endpoints documentados en Swagger
- [ ] Tokens JWT funcionales

---

## 📚 REFERENCIAS

- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT con Python-JOSE](https://pyjwt.readthedocs.io/)
- [Passlib para Passwords](https://passlib.readthedocs.io/)
- [CORS en FastAPI](https://fastapi.tiangolo.com/tutorial/cors/)

---

**Autor:** Cline (AI Assistant)
**Fecha:** 2026-03-28
**Estado:** ✅ LISTO PARA IMPLEMENTACIÓN