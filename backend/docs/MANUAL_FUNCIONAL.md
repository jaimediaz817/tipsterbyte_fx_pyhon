# 📚 Manual Funcional - TipsterByte FX

## Tabla de Contenidos
1. [Iniciar el Servidor](#1-iniciar-el-servidor)
2. [Ver Documentación de la API](#2-ver-documentación-de-la-api)
3. [Crear un Usuario](#3-crear-un-usuario)
4. [Iniciar Sesión](#4-iniciar-sesión)
5. [Usar el Token JWT](#5-usar-el-token-jwt)
6. [Endpoints de Autenticación](#6-endpoints-de-autenticación)
7. [Endpoints del Scheduler](#7-endpoints-del-scheduler)
8. [Ejemplos Completos con cURL](#8-ejemplos-completos-con-curl)

---

## 1. Iniciar el Servidor

### Opción A: Usando manage.py (Recomendado)
```bash
cd backend
python manage.py server run --host 127.0.0.1 --port 8000
```

### Opción B: Usando uvicorn directamente
```bash
cd backend
uvicorn backend.main_init_web_server:app --reload --host 127.0.0.1 --port 8000
```

### Opción C: Sin recarga automática (producción)
```bash
cd backend
uvicorn backend.main_init_web_server:app --host 0.0.0.0 --port 8000
```

**Salida esperada:**
```
🚀 Iniciando scheduler de procesos programados...
🗄️  Verificando conexión a base de datos...
🔄 Ejecutando migraciones pendientes...
✅ Base de datos y migraciones listas.

--- API Endpoints Disponibles ---

📦 Versión: V1
  [POST]     /api/v1/auth/register
  [POST]     /api/v1/auth/login
  [POST]     /api/v1/auth/logout
  [GET]      /api/v1/auth/me
  [GET]      /api/v1/auth/ping
  [GET]      /api/v1/scheduler/status
  ...
```

---

## 2. Ver Documentación de la API

Una vez el servidor esté corriendo, accede a:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

---

## 3. Crear un Usuario

### Endpoint
```
POST /api/v1/auth/register
```

### Parámetros del Body (JSON)
| Campo      | Tipo   | Requerido | Descripción                               | Ejemplo              |
| ---------- | ------ | --------- | ----------------------------------------- | -------------------- |
| `username` | string | ✅ Sí      | Nombre de usuario único (3-50 caracteres) | `"john_doe"`         |
| `email`    | string | ✅ Sí      | Email válido del usuario                  | `"john@example.com"` |
| `password` | string | ✅ Sí      | Contraseña segura (mínimo 8 caracteres)   | `"MiPassword123!"`   |

### Ejemplo de Request
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "MiPassword123!"
  }'
```

### Respuesta Exitosa (201 Created)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Posibles Errores
- **400 Bad Request**: Email o username ya existen, o contraseña débil
```json
{
  "detail": "El email ya está registrado"
}
```

---

## 4. Iniciar Sesión

### Endpoint
```
POST /api/v1/auth/login
```

### Parámetros del Body (JSON)
| Campo      | Tipo   | Requerido | Descripción               | Ejemplo                             |
| ---------- | ------ | --------- | ------------------------- | ----------------------------------- |
| `username` | string | ✅ Sí      | Nombre de usuario O email | `"john_doe"` o `"john@example.com"` |
| `password` | string | ✅ Sí      | Contraseña del usuario    | `"MiPassword123!"`                  |

### Ejemplo de Request con username
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "MiPassword123!"
  }'
```

### Ejemplo de Request con email
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john@example.com",
    "password": "MiPassword123!"
  }'
```

### Respuesta Exitosa (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Posibles Errores
- **401 Unauthorized**: Credenciales inválidas o usuario inactivo
```json
{
  "detail": "Credenciales inválidas"
}
```

---

## 5. Usar el Token JWT

### Estructura de la Respuesta de Token

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

| Campo           | Descripción                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------------- |
| `access_token`  | Token de acceso de corta duración (30 min por defecto). Úsalo para autenticar requests.                  |
| `refresh_token` | Token de refresh de larga duración. Úsalo para obtener un nuevo access token sin hacer login nuevamente. |
| `token_type`    | Siempre será `"bearer"`                                                                                  |
| `expires_in`    | Segundos hasta que expire el access token (1800 = 30 minutos)                                            |

### Cómo usar el Token en peticiones

Incluye el token en el header `Authorization` con el prefijo `Bearer `:

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Formato del Header
```
Authorization: Bearer <access_token>
```

---

## 6. Endpoints de Autenticación

### 6.1 Registrar Usuario
- **Método**: `POST`
- **Ruta**: `/api/v1/auth/register`
- **Auth**: No requerida
- **Descripción**: Crea una nueva cuenta de usuario

### 6.2 Iniciar Sesión
- **Método**: `POST`
- **Ruta**: `/api/v1/auth/login`
- **Auth**: No requerida
- **Descripción**: Autentica un usuario y retorna tokens

### 6.3 Cerrar Sesión
- **Método**: `POST`
- **Ruta**: `/api/v1/auth/logout`
- **Auth**: ✅ Requerida (Bearer Token)
- **Descripción**: Cierra la sesión del usuario actual

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer <tu_access_token>"
```

### 6.4 Obtener Usuario Actual
- **Método**: `GET`
- **Ruta**: `/api/v1/auth/me`
- **Auth**: ✅ Requerida (Bearer Token)
- **Descripción**: Retorna información del usuario autenticado

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <tu_access_token>"
```

**Respuesta:**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-03-30T16:00:00"
}
```

### 6.5 Health Check de Auth
- **Método**: `GET`
- **Ruta**: `/api/v1/auth/ping`
- **Auth**: No requerida
- **Descripción**: Verifica que el servicio de autenticación funciona

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/auth/ping"
```

**Respuesta:**
```json
{
  "ok": true,
  "service": "auth",
  "message": "pong"
}
```

---

## 7. Endpoints del Scheduler

### 7.1 Ver Estado del Scheduler
- **Método**: `GET`
- **Ruta**: `/api/v1/scheduler/status`
- **Auth**: No requerida (ajustar según configuración)

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/scheduler/status"
```

### 7.2 Pausar Todas las Tareas
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/pause-all`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/pause-all"
```

### 7.3 Reanudar Todas las Tareas
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/resume-all`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/resume-all"
```

### 7.4 Pausar una Tarea Específica
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/pause/{job_id}`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/pause/log_cleanup_job"
```

### 7.5 Reanudar una Tarea Específica
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/resume/{job_id}`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/resume/log_cleanup_job"
```

### 7.6 Recargar Tareas
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/reload`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/reload"
```

### 7.7 Estado de Limpieza de Logs
- **Método**: `GET`
- **Ruta**: `/api/v1/scheduler/log-cleanup/status`

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/scheduler/log-cleanup/status"
```

### 7.8 Pausar Limpieza de Logs
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/log-cleanup/pause`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/log-cleanup/pause"
```

### 7.9 Reanudar Limpieza de Logs
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/log-cleanup/resume`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/log-cleanup/resume"
```

### 7.10 Ejecutar Limpieza de Logs Ahora
- **Método**: `POST`
- **Ruta**: `/api/v1/scheduler/log-cleanup/run-now`

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/scheduler/log-cleanup/run-now"
```

---

## 8. Ejemplos Completos con cURL

### Flujo Completo: Registro → Login → Usar Token

#### Paso 1: Registrar usuario
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Respuesta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJ0ZXN0X3VzZXIiLCJleHAiOjE3MTE0NzEyMDAsImlhdCI6MTcxMTQ2OTQwMCwidHlwZSI6ImFjY2VzcyJ9.abc123...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzEyMDc0MjAwLCJpYXQiOjE3MTE0Njk0MDAsInR5c</parameter>
</write_to_file>