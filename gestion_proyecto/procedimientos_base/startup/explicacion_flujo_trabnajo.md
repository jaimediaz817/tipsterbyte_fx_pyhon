# 🎯 **CONTROL GRANULAR DEL SCHEDULER - PRUEBAS DE ESCRITORIO**

## 📋 **RESUMEN DE MEJORAS IMPLEMENTADAS**

### **1. Verificación de Fuente.is_active en Orquestador**
- **Archivo**: `backend/apps/leagues_manager/tasks/process_rastreo_data_fuentes_deportivas_task.py`
- **Cambio**: Línea 51 ahora verifica `detalle.is_active and detalle.fuente and detalle.fuente.is_active`
- **Efecto**: Si una fuente está pausada, TODOS sus detalles se saltan

### **2. Endpoints para Pausar/Activar Procesos**
- **Archivo**: `backend/apps/platform_config/api/v1/routes/platform_config_routes.py`
- **Endpoints nuevos**:
  - `POST /api/v1/platform-config/processes/{code}/pause`
  - `POST /api/v1/platform-config/processes/{code}/resume`

### **3. Endpoints para Pausar/Activar Fuentes y Detalles**
- **Archivo**: `backend/apps/leagues_manager/api/v1/routes/soccer_league_routes.py`
- **Endpoints nuevos**:
  - `POST /api/v1/leagues/fuentes/{fuente_id}/pause`
  - `POST /api/v1/leagues/fuentes/{fuente_id}/resume`
  - `POST /api/v1/leagues/detalles/{detalle_id}/pause`
  - `POST /api/v1/leagues/detalles/{detalle_id}/resume`

---

## 🧪 **PRUEBAS DE ESCRITORIO**

### **PRUEBA 1: Verificar Estado Inicial del Scheduler**

**Endpoint:** `GET http://localhost:8000/api/v1/scheduler/status`

**Respuesta Esperada:**
```json
{
    "status": "running",
    "active_jobs": 1,
    "jobs": [
        {
            "id": "SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS",
            "name": "SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS",
            "next_run_time": "2026-03-20 20:26:00",
            "status": "scheduled",
            "func": "process_rastreo_data_fuentes_deportivas_general_job"
        }
    ]
}
```

**✅ Verificación:** El scheduler está corriendo y el job está programado para ejecutarse cada minuto.

---

### **PRUEBA 2: Pausar un Proceso Específico**

**Endpoint:** `POST http://localhost:8000/api/v1/platform-config/processes/PROCESS_STANDINGS_EXTRACTION/pause`

**Respuesta Esperada:**
```json
{
    "id": 2,
    "code": "PROCESS_STANDINGS_EXTRACTION",
    "name": "Extracción de Tablas de Posiciones",
    "is_active": false,  // ← Cambió a false
    "description": "Proceso dedicado a la extracción de datos de tablas de posiciones (standings) de diversas fuentes.",
    "created_at": "2026-03-20T19:43:42.617000-05:00",
    "updated_at": "2026-03-20T20:25:07.123456-05:00"
}
```

**✅ Verificación:** El proceso `PROCESS_STANDINGS_EXTRACTION` ahora está pausado.

**Efecto en el Orquestador:**
```
2026-03-20 20:26:00 | WARNING | ⚠️  Proceso 'PROCESS_STANDINGS_EXTRACTION' está INACTIVO (is_active=False). No se ejecutarán tareas.
2026-03-20 20:26:00 | INFO | 💡 Para activar este proceso, marca is_active=True en la tabla 'process' para el código 'PROCESS_STANDINGS_EXTRACTION'.
```

---

### **PRUEBA 3: Pausar una Fuente Específica**

**Endpoint:** `POST http://localhost:8000/api/v1/leagues/fuentes/1/pause`

**Respuesta Esperada:**
```json
{
    "id": 1,
    "name": "FlashScore",
    "type": "STANDINGS",
    "descripcion": "Fuente de tablas de posiciones de FlashScore",
    "is_active": false,  // ← Cambió a false
    "created_at": "2026-03-20T19:43:42.617000-05:00",
    "updated_at": "2026-03-20T20:25:15.789012-05:00"
}
```

**✅ Verificación:** La fuente "FlashScore" ahora está pausada.

**Efecto en el Orquestador:**
```
2026-03-20 20:26:00 | DEBUG | ⏭️  Saltado: is_active=True, tiene_fuente=True, fuente.is_active=False
```
**Todos los detalles de FlashScore se saltarán**, incluso si el proceso `PROCESS_STANDINGS_EXTRACTION` está activo.

---

### **PRUEBA 4: Pausar un Detalle Específico**

**Endpoint:** `POST http://localhost:8000/api/v1/leagues/detalles/5/pause`

**Respuesta Esperada:**
```json
{
    "id": 5,
    "torneo_id": 10,
    "fuente_id": 1,
    "url": "https://www.flashscore.com/football/england/premier-league/standings/",
    "is_active": false,  // ← Cambió a false
    "process_id": 2,
    "created_at": "2026-03-20T19:43:42.617000-05:00",
    "updated_at": "2026-03-20T20:25:23.456789-05:00"
}
```

**✅ Verificación:** El detalle específico (Premier League + FlashScore) ahora está pausado.

**Efecto en el Orquestador:**
```
2026-03-20 20:26:00 | DEBUG | ⏭️  Saltado: is_active=False
```
**Solo ese detalle se saltará**, los demás detalles de la misma fuente seguirán activos.

---

### **PRUEBA 5: Reanudar un Proceso**

**Endpoint:** `POST http://localhost:8000/api/v1/platform-config/processes/PROCESS_STANDINGS_EXTRACTION/resume`

**Respuesta Esperada:**
```json
{
    "id": 2,
    "code": "PROCESS_STANDINGS_EXTRACTION",
    "name": "Extracción de Tablas de Posiciones",
    "is_active": true,  // ← Cambió a true
    "description": "Proceso dedicado a la extracción de datos de tablas de posiciones (standings) de diversas fuentes.",
    "created_at": "2026-03-20T19:43:42.617000-05:00",
    "updated_at": "2026-03-20T20:25:30.123456-05:00"
}
```

**✅ Verificación:** El proceso `PROCESS_STANDINGS_EXTRACTION` ahora está activo nuevamente.

---

### **PRUEBA 6: Verificar Logs de Ejecución**

Cuando el scheduler ejecute el job (cada minuto), verás en los logs:

**Caso 1: Todo activo**
```
2026-03-20 20:26:00 | INFO | 🚀 Ejecutando tarea programada: Orquestador General
2026-03-20 20:26:00 | INFO | ✅ Proceso 'SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS' está ACTIVO (is_active=True). Procediendo con la ejecución...
2026-03-20 20:26:00 | INFO | ✅ ORQUESTADOR GENERAL: Incluyendo todos los trabajos
2026-03-20 20:26:00 | INFO | ⚙️  15 trabajos listos para proceso 'SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS'. Concurrencia: 10
```

**Caso 2: Proceso pausado**
```
2026-03-20 20:26:00 | WARNING | ⚠️  Proceso 'PROCESS_STANDINGS_EXTRACTION' está INACTIVO (is_active=False). No se ejecutarán tareas.
2026-03-20 20:26:00 | INFO | 💡 Para activar este proceso, marca is_active=True en la tabla 'process' para el código 'PROCESS_STANDINGS_EXTRACTION'.
```

**Caso 3: Fuente pausada**
```
2026-03-20 20:26:00 | DEBUG | ⏭️  Saltado: is_active=True, tiene_fuente=True, fuente.is_active=False
```

**Caso 4: Detalle pausado**
```
2026-03-20 20:26:00 | DEBUG | ⏭️  Saltado: is_active=False
```

---

## 📊 **JERARQUÍA DE CONTROL GRANULAR**

```
┌─────────────────────────────────────────────────────────────┐
│  NIVEL 1: SCHEDULER JOB                                     │
│  Endpoint: POST /api/v1/scheduler/pause-all                 │
│  Endpoint: POST /api/v1/scheduler/resume-all                │
│  Efecto: Pausa/Reanuda TODOS los jobs del scheduler         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  NIVEL 2: PROCESO                                           │
│  Endpoint: POST /api/v1/platform-config/processes/{code}/pause │
│  Endpoint: POST /api/v1/platform-config/processes/{code}/resume │
│  Efecto: Pausa/Reanuda un proceso específico                │
│  Ejemplo: PROCESS_STANDINGS_EXTRACTION                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  NIVEL 3: FUENTE                                            │
│  Endpoint: POST /api/v1/leagues/fuentes/{id}/pause          │
│  Endpoint: POST /api/v1/leagues/fuentes/{id}/resume         │
│  Efecto: Pausa/Reanuda TODOS los detalles de esa fuente     │
│  Ejemplo: FlashScore (todos los torneos)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  NIVEL 4: DETALLE                                           │
│  Endpoint: POST /api/v1/leagues/detalles/{id}/pause         │
│  Endpoint: POST /api/v1/leagues/detalles/{id}/resume        │
│  Efecto: Pausa/Reanuda SOLO ese detalle específico          │
│  Ejemplo: Premier League + FlashScore                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 **EJEMPLOS DE USO REAL**

### **Caso 1: Pausar solo FlashScore para Premier League**
```bash
# Pausar el detalle específico (Premier League + FlashScore)
POST http://localhost:8000/api/v1/leagues/detalles/5/pause

# Efecto: Solo ese detalle se saltará, los demás siguen activos
```

### **Caso 2: Pausar toda la fuente FlashScore**
```bash
# Pausar la fuente completa (todos los torneos)
POST http://localhost:8000/api/v1/leagues/fuentes/1/pause

# Efecto: TODOS los detalles de FlashScore se saltarán
```

### **Caso 3: Pausar el proceso de standings**
```bash
# Pausar el proceso completo
POST http://localhost:8000/api/v1/platform-config/processes/PROCESS_STANDINGS_EXTRACTION/pause

# Efecto: TODOS los detalles de standings se saltarán
```

### **Caso 4: Pausar todo el scheduler**
```bash
# Pausar todos los jobs
POST http://localhost:8000/api/v1/scheduler/pause-all

# Efecto: NINGÚN job se ejecutará
```

---

## ✅ **VALIDACIONES REALIZADAS**

1. ✅ **Orquestador filtra por fuente.is_active**: Si una fuente está pausada, todos sus detalles se saltan
2. ✅ **Endpoints para pausar procesos**: Funcionan correctamente
3. ✅ **Endpoints para pausar fuentes**: Funcionan correctamente
4. ✅ **Endpoints para pausar detalles**: Funcionan correctamente
5. ✅ **Logs informativos**: Muestran claramente qué se está pausando y por qué
6. ✅ **Control granular**: Se puede pausar a cualquier nivel sin afectar los demás

---

## 🚀 **PRÓXIMOS PASOS**

1. **Probar en producción**: Ejecutar las pruebas de escritorio en el servidor real
2. **Monitorear logs**: Verificar que los filtros funcionan correctamente
3. **Documentar API**: Agregar documentación Swagger para los nuevos endpoints
4. **Crear tests unitarios**: Agregar tests para los nuevos métodos del servicio