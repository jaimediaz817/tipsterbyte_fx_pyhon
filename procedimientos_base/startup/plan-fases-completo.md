# 🎯 PLAN COMPLETO DE FASES - TipsterByte FX

**Fecha:** 2026-03-21
**Estado:** APROBADO PARA IMPLEMENTACIÓN

---

## 📋 **ROADMAP DE IMPLEMENTACIÓN**

```
FASE 1: Factory Function (scheduled_jobs.py)
    ↓
FASE 2: Inyección de dependencias (job_runner_application.py)
    ↓
FASE 3: Excepciones personalizadas (core/exceptions/)
    ↓
FASE 4: Semáforos diferenciados (job_runner_application.py)
    ↓
FASE 5: Refactor de logs (core/logger.py)
```

---

## 🔑 **PALABRA CLAVE PARA RECORDAR**

### **"CONTINUAR FASES"**

Cuando quieras que continúe con las siguientes fases después de completar Fase 1 y 2, usa esta palabra clave en tu mensaje:

```
CONTINUAR FASES
```

Esto me recordará que:
1. ✅ Fase 1 y 2 están completadas
2. ✅ Debo implementar Fase 3 (excepciones personalizadas)
3. ✅ Debo implementar Fase 4 (semáforos diferenciados)
4. ✅ Debo implementar Fase 5 (refactor de logs)

---

## 📊 **DETALLE DE CADA FASE**

### **FASE 1: Factory Function** ⏳ PENDIENTE
- **Archivo:** `backend/apps/leagues_manager/scheduler/scheduled_jobs.py`
- **Cambio:** Eliminar 4 funciones duplicadas con 1 función genérica
- **Tiempo:** 30 minutos
- **Riesgo:** 🟢 MUY BAJO
- **Impacto:** -69% líneas de código

### **FASE 2: Inyección de Dependencias** ⏳ PENDIENTE
- **Archivo:** `backend/apps/leagues_manager/application/job_runner_application.py`
- **Cambio:** Eliminar singleton global, usar DI
- **Tiempo:** 45 minutos
- **Riesgo:** 🟢 MUY BAJO
- **Impacto:** Testing posible, múltiples configuraciones

### **FASE 3: Excepciones Personalizadas** ⏳ PENDIENTE
- **Archivos nuevos:** `backend/core/exceptions/` (5 archivos)
- **Archivos a modificar:** 3 archivos
- **Tiempo:** 2-3 horas
- **Riesgo:** 🟡 MEDIO
- **Impacto:** Debugging 10x más fácil

**Excepciones a crear:**
- `ProcessNotFoundException`
- `ProcessInactiveException`
- `ProcessRunCreationException`
- `FuenteNotFoundException`
- `FuenteInactiveException`
- `DetalleInactiveException`
- `RobotNotFoundException`
- `ScrapingException`
- `ScrapingTimeoutException`
- `ScrapingParsingException`
- `SemaphoreTimeoutException`
- `MaxRetriesExceededException`

### **FASE 4: Semáforos Diferenciados** ⏳ PENDIENTE
- **Archivo:** `backend/apps/leagues_manager/application/job_runner_application.py`
- **Cambio:** Semáforo global → Semáforos por tipo de robot
- **Tiempo:** 1 hora
- **Riesgo:** 🟡 MEDIO
- **Impacto:** Rate limiting, priorización

**Configuración propuesta:**
```python
self.semaphores = {
    RobotTypeEnum.STANDINGS: asyncio.Semaphore(3),   # Rápido
    RobotTypeEnum.ODDS_WPLAY: asyncio.Semaphore(1),  # Lento (rate limit)
    RobotTypeEnum.CALENDAR: asyncio.Semaphore(2),    # Medio
}
```

### **FASE 5: Refactor de Logs** ⏳ PENDIENTE
- **Archivos:** `backend/core/logger.py`, `backend/core/middleware.py`
- **Cambio:** Logs fragmentados → JSON estructurado + Trace ID
- **Tiempo:** 3-5 días
- **Riesgo:** 🟡 MEDIO
- **Impacto:** Debugging profesional, correlación de eventos

**Cambios:**
- Un solo archivo de logs (`application.log`)
- Formato JSON estructurado
- Trace ID automático por request
- Excepciones personalizadas integradas

---

## ✅ **VERIFICACIONES REALIZADAS**

| Verificación        | Estado        | Detalle                      |
| ------------------- | ------------- | ---------------------------- |
| Tests unitarios     | ✅ SIN IMPACTO | No dependen de cambios       |
| Seeders             | ✅ SIN IMPACTO | Sin acoplamiento             |
| Flujo de ejecución  | ✅ SIN CAMBIO  | Comportamiento idéntico      |
| Logs                | ✅ SIN CAMBIO  | Mismos logs                  |
| Concurrencia        | ✅ SIN CAMBIO  | Mismo semáforo               |
| Backward compatible | ✅ SÍ          | Interfaz pública se mantiene |

---

## 📁 **DOCUMENTACIÓN GENERADA**

- `procedimientos_base/startup/pruebas-escritorio-fase1-2.md` - Pruebas de escritorio comparativas
- `procedimientos_base/startup/control-cambios-llm.md` - Control de cambios actualizado
- `procedimientos_base/startup/plan-fases-completo.md` - Este documento

---

## 🚀 **PRÓXIMO PASO**

Implementar **FASE 1 + 2** (2-3 horas total)

Después de completar Fase 1 y 2, usa la palabra clave:

```
CONTINUAR FASES
```

Para que implemente Fase 3, 4 y 5.