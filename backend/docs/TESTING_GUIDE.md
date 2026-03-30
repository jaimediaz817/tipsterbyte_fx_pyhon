# Guía de Testing Funcional - TipsterByte FX

## Índice
1. [Requisitos Previos](#requisitos-previos)
2. [Iniciar el Servidor](#iniciar-el-servidor)
3. [Endpoints de Sistema](#endpoints-de-sistema)
4. [Endpoints de Autenticación](#endpoints-de-autenticación)
5. [Endpoints de Ligas](#endpoints-de-ligas)
6. [Endpoints de Platform Config](#endpoints-de-platform-config)
7. [Endpoints de Scheduler](#endpoints-de-scheduler)
8. [Endpoints de Session Logs](#endpoints-de-session-logs)

---

## Requisitos Previos

### 1. Bases de Datos
Asegúrate de que PostgreSQL y MongoDB estén corriendo.

### 2. Variables de Entorno
Verifica que el archivo `backend/.env` tenga la configuración correcta.

### 3. Instalar Dependencias
```bash
pip install -r backend/requirements.txt
```

### 4. Ejecutar Migraciones
```bash
cd backend
alembic upgrade head
```

---

## Iniciar el Servidor

### Opción 1: Usando el CLI (Recomendado)
```bash
python backend/manage.py server run --host 127.0.0.1 --port 8000
```

### Opción 2: Usando Uvicorn directamente
```bash
uvicorn backend.main_init_web_server:app --host 127.0.0.1 --port 8000 --reload
```

### Verificar que el servidor está corriendo
```bash
curl http://localhost:8000/system/health
```

### Acceder a la Documentación
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Endpoints de Sistema

### Health Check
```bash
curl http://localhost:8000/system/health
```

### Status Check
```bash
curl http://localhost:8000/system/status
```

---

## Endpoints de Autenticación

### Ping de Autenticación
```bash
curl http://localhost:8000/api/v1/auth/ping
```

### Test del Controlador
```bash
curl http://localhost:8000/api/v1/auth/test
```

---

## Endpoints de Ligas

### Crear Continente
```bash
curl -X POST http://localhost:8000/api/v1/leagues/continentes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Europa", "codigo": "EU"}'
```

### Listar Continentes
```bash
curl http://localhost:8000/api/v1/leagues/continentes
```

### Crear País
```bash
curl -X POST http://localhost:8000/api/v1/leagues/paises \
  -H "Content-Type: application/json" \
  -d '{"nombre": "España", "codigo": "ES", "continente_id": 1}'
```

### Crear Liga
```bash
curl -X POST http://localhost:8000/api/v1/leagues/ligas \
  -H "Content-Type: application/json" \
  -d '{"nombre": "La Liga", "pais_id": 1, "nivel": 1}'
```

### Pausar/Reanudar Fuente
```bash
curl -X POST http://localhost:8000/api/v1/leagues/fuentes/1/pause
curl -X POST http://localhost:8000/api/v1/leagues/fuentes/1/resume
```

---

## Endpoints de Platform Config

### Crear Proceso
```bash
curl -X POST http://localhost:8000/api/v1/platform-config/processes \
  -H "Content-Type: application/json" \
  -d '{"code": "TEST", "name": "Test Process", "is_active": true}'
```

### Listar Procesos
```bash
curl http://localhost:8000/api/v1/platform-config/processes
```

### Pausar/Reanudar Proceso
```bash
curl -X POST http://localhost:8000/api/v1/platform-config/processes/TEST/pause
curl -X POST http://localhost:8000/api/v1/platform-config/processes/TEST/resume
```

---

## Endpoints de Scheduler

### Obtener Estado
```bash
curl http://localhost:8000/api/v1/scheduler/status
```

### Pausar/Reanudar Jobs
```bash
curl -X POST http://localhost:8000/api/v1/scheduler/pause-all
curl -X POST http://localhost:8000/api/v1/scheduler/resume-all
```

### Limpieza de Logs
```bash
curl http://localhost:8000/api/v1/scheduler/log-cleanup/status
curl -X POST http://localhost:8000/api/v1/scheduler/log-cleanup/run-now
```

---

## Endpoints de Session Logs

### Obtener Logs de Usuario
```bash
curl "http://localhost:8000/api/v1/users/{user_id}/logs?start_date=2026-03-01T00:00:00&end_date=2026-03-31T23:59:59&limit=100"
```

### Obtener Logs por Session
```bash
curl "http://localhost:8000/api/v1/users/sessions/{session_id}?limit=50"
```

---

## Notas Importantes

1. Verifica variables de entorno antes de iniciar
2. Ejecuta migraciones antes de usar endpoints de BD
3. Revisa logs en consola para diagnosticar errores
4. Accede a Swagger UI para pruebas interactivas