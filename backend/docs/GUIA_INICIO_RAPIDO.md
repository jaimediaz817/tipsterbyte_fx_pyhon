# 🚀 GUÍA DE INICIO RÁPIDO - TipsterByte FX

**Fecha**: 2026-03-30  
**Objetivo**: Iniciar el servidor y verificar funcionamiento de Auth y Scheduler

---

## 📋 PRERREQUISITOS

### Bases de datos corriendo
```bash
# PostgreSQL (puerto 5433)
docker-compose up -d postgres

# MongoDB (puerto 27017)
docker-compose up -d mongodb
```

### Variables de entorno
```bash
# Verificar que existe backend/.env con:
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/tipsterbyte_fx_db
MONGO_URI=mongodb://tipster_admin:tipster_mongo_pass@localhost:27017/tipsterbyte_fx_nosql_db?authSource=admin
```

---

## 🔐 PASO 1: GENERAR CLAVE FERNET

```bash
cd backend
python manage.py secrets generate
```

**Salida esperada**:
```
✅ Clave generada y guardada exitosamente en: backend/core/.fernet.key
```

**Verificar**:
```bash
python manage.py secrets show
```

---

## 🗄️ PASO 2: EJECUTAR MIGRACIONES SQL

```bash
cd backend
python manage.py sql migrate
```

**Salida esperada**:
```
🔄 Aplicando migraciones de Alembic hasta la revisión: 'head'...
✅ Migraciones aplicadas exitosamente.
  ℹ️ No había migraciones pendientes por aplicar.
```

**Si es primera vez**:
```bash
# Crear migración inicial
python manage.py sql create-migration -m "migracion_inicial"

# Aplicar migración
python manage.py sql migrate
```

---

## 🍃 PASO 3: INICIALIZAR MONGODB

```bash
cd backend
python manage.py nosql init-schema
```

**Salida esperada**:
```
🔌 Validando conexión con MongoDB...
✅ Conexión exitosa
🔎 Buscando modelos Beanie...
✅ Inicialización completada
```

---

## 🌱 PASO 4: EJECUTAR SEEDERS (OPCIONAL)

### SQL (PostgreSQL)
```bash
# Todos los seeders
python manage.py sql seed

# Seeder específico
python manage.py sql seed AuthSeeder
python manage.py sql seed PlatformConfigSeeder
```

### NoSQL (MongoDB)
```bash
python manage.py nosql seed
```

---

## 🚀 PASO 5: INICIAR SERVIDOR

### Opción A: Usando manage.py (RECOMENDADO)
```bash
cd backend
python manage.py server run
```

### Opción B: Usando uvicorn directamente
```bash
cd backend
python -m uvicorn main_init_web_server:app --reload --host 127.0.0.1 --port 8000
```

**Salida esperada**:
```
🚀 Iniciando scheduler de procesos programados...
🗄️  Verificando conexión a base de datos...
✅ Conexión a PostgreSQL verificada correctamente.
🔄 Ejecutando migraciones pendientes...
✅ No hay migraciones pendientes. Esquema actualizado.
✅ Base de datos y migraciones listas.

--- API Endpoints Disponibles ---
📦 Versión: V1
  [GET]         /api/v1/auth/ping
  [GET]         /api/v1/users/{user_id}/logs
  [GET]         /api/v1/users/sessions/{session_id}
  ...

INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## ✅ PASO 6: VERIFICACIONES

### 6.1 Health Check Auth
```bash
curl http://localhost:8000/api/v1/auth/ping
```

**Respuesta esperada**:
```json
{
  "ok": true,
  "service": "auth",
  "message": "pong"
}
```

### 6.2 Documentación Swagger
```
http://localhost:8000/docs
```

### 6.3 Verificar Scheduler
```bash
# Ver estado del scheduler
curl http://localhost:8000/api/v1/scheduler/status
```

---

## 📊 VERIFICAR DATOS EN BASES DE DATOS

### PostgreSQL - Verificar tablas
```bash
python manage.py sql state
```

### MongoDB - Verificar colecciones
```bash
# En MongoDB Compass o mongo shell
use tipsterbyte_fx_nosql_db
show collections
```

**Colecciones esperadas**:
- `session_logs` (se crea al primer request autenticado)
- `access_logs` (si se ejecutó seeder)

---

## 🔍 PRUEBAS FUNCIONALES

### Test 1: Registrar usuario
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!",
    "nombre": "Usuario Test"
  }'
```

### Test 2: Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!"
  }'
```

**Respuesta**: JWT token

### Test 3: Ver logs de sesión
```bash
# Usar el token obtenido en el login
curl http://localhost:8000/api/v1/users/{user_id}/logs \
  -H "Authorization: Bearer <tu_token>"
```

---

## 📅 TAREAS PROGRAMADAS (SCHEDULER)

### Verificar jobs programados
```bash
# Ver configuración de procesos
python manage.py sql seed PlatformConfigSeeder
```

### Ejecutar job manualmente
```bash
# Ver jobs disponibles
python manage.py --help

# Ejecutar job específico (si está configurado)
python -c "from core.scheduler import run_job; run_job('log_cleanup')"
```

### Ver logs de ejecuciones
```bash
# En PostgreSQL
SELECT * FROM process_run_logs ORDER BY created_at DESC LIMIT 10;
```

---

## 🛠️ COMANDOS ÚTILES

### Ver estado de la BD
```bash
python manage.py sql state
```

### Backup de BD
```bash
python manage.py sql state backup
```

### Resetear BD (CUIDADO)
```bash
python manage.py sql state reset
```

### Ver migraciones
```bash
python manage.py sql migrate  # Muestra migraciones disponibles
```

---

## ❌ SOLUCIÓN DE PROBLEMAS

### Error: "Fernet key not found"
```bash
python manage.py secrets generate
```

### Error: "Connection refused" (PostgreSQL)
```bash
docker-compose up -d postgres
# Esperar 5 segundos
sleep 5
python manage.py sql migrate
```

### Error: "Connection refused" (MongoDB)
```bash
docker-compose up -d mongodb
# Esperar 5 segundos
sleep 5
python manage.py nosql init-schema
```

### Error: "Table already exists"
```bash
python manage.py sql state clear-migrations
python manage.py sql create-migration -m "reset"
python manage.py sql migrate
```

---

## 📝 RESUMEN RÁPIDO

```bash
# 1. Generar clave
python manage.py secrets generate

# 2. Migraciones
python manage.py sql migrate

# 3. MongoDB
python manage.py nosql init-schema

# 4. Seeders (opcional)
python manage.py sql seed
python manage.py nosql seed

# 5. Iniciar servidor
python manage.py server run

# 6. Verificar
curl http://localhost:8000/api/v1/auth/ping
```

---

**Autor**: Arquitecto de Software Senior  
**Fecha**: 2026-03-30  
**Versión**: 1.0.0