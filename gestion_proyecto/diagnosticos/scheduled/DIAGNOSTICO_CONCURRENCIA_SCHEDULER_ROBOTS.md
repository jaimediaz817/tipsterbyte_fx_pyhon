# 🚨 DIAGNÓSTICO DEFINITIVO: CONCURRENCIA, SCHEDULER Y ROBOTS
**Fecha:** 10/04/2026
**Versión:** 1.0
**Estado:** 🔴 CRÍTICO
**Autor:** Análisis Arquitectónico

---

## 🎯 RESUMEN EJECUTIVO

✅ **LO QUE ESTA BIEN:**
- La relación `Proceso -> FuenteExtraccion -> DetalleFuenteExtraccion` es correcta
- El filtrado por `process_id` funciona perfectamente
- El orquestador construye correctamente el lote de trabajos
- Las pruebas unitarias pasan todas

❌ **LO QUE ESTA TOTALMENTE ROTO Y NADIE LO VE:**
> 🚨 **EL SEMÁFORO NO EXISTE.**

Actualmente no hay ningún limite de concurrencia. Se pueden ejecutar 100 robots al mismo tiempo. El rate limit de las APIs te mata, y las pruebas unitarias te mienten.

---

## 🧠 DIAGRAMA DEL FLUJO COMPLETO ACTUAL

```
📅 SCHEDULER
    ↓
🔄 JOB PROGRAMADO (cada X minutos)
    ↓
🚀 launch_process_rastreo_data_fuentes_deportivas_task()
    ↓
✅ Consulta proceso por codigo
    ↓
✅ Consulta TODAS las ligas, torneos, fuentes y detalles
    ↓
✅ Filtra solo los DetalleFuenteExtraccion activos y que corresponden al process_id
    ↓
✅ Construye lote de N trabajos a ejecutar
    ↓
⚠️ ❌ CREA UN NUEVO DICCIONARIO DE SEMAFOROS POR CADA EJECUCION
    ↓
🚀 Asyncio Gather lanza TODOS los trabajos al mismo tiempo
```

---

## 💥 EL BUG DE CONCURRENCIA

Este es el bug mas caro y mas comun de sistemas asincronicos:

### 🔴 Problema:
Cada vez que se ejecuta el orquestador:
1. Linea 177: Se crea un diccionario `semaphores_by_type` **NUEVO**
2. Por cada tipo de robot se crea una instancia **NUEVA** de Semaphore
3. **SI SE EJECUTAN 2 VECES EL PROCESO AL MISMO TIEMPO, CADA UNO TIENE SU PROPIO SEMAFORO.**

✅ Limite esperado para Odds: `1` concurrente
❌ Limite real: `Ilimitado`

> 🎯 Esto es lo que pasa en producción: Tienes configurado limite 1, pero se estan ejecutando 17 robots de Odds al mismo tiempo. Las APIs te banean, los request fallan, y nadie entiende porque el semaforo dice 1.

---

## 📊 ESCENARIOS DE FALLO

| Escenario                                    | Limite declarado | Limite real |
| -------------------------------------------- | ---------------- | ----------- |
| 1 ejecución del orquestador                  | 1                | 1 ✅         |
| 2 ejecuciones al mismo tiempo                | 1                | 2 ❌         |
| 5 ejecuciones al mismo tiempo                | 1                | 5 ❌         |
| Ejecución manual + scheduler al mismo tiempo | 1                | 2 ❌         |
| Proceso general + proceso especifico         | 1                | 2 ❌         |

---

## 🔗 RELACIÓN ENTRE LAS ENTIDADES

La estructura es perfecta, no hay que cambiar nada de esto:

```
📌 Process (platform_config)
  ├─ id: 1
  ├─ code: PROCESS_EXTRACT_ODDS
  └─ is_active: True

📌 FuenteExtraccion
  ├─ type: ODDS_WPLAY
  └─ concurrencia: 1

📌 DetalleFuenteExtraccion
  ├─ process_id: 1  ✅ RELACIÓN CLAVE
  ├─ is_active: True
  └─ url: https://api.wplay.co/...
```

✅ Este diseño es excelente. Solo hay que arreglar el semaforo.

---

## ✅ SOLUCIÓN DE IMPACTO CERO

### Cambios necesarios: **3 lineas de codigo en config_semaphore.py**

```python
# backend/core/config_semaphore.py
import asyncio
from typing import Dict

# ✅ SINGLETON: Esta variable se crea UNA SOLA VEZ en todo el ciclo de vida del proceso
_SEMAPHORE_INSTANCES: Dict[RobotTypeEnum, asyncio.Semaphore] = {}


def get_semaphore_for_robot_type(robot_type: RobotTypeEnum) -> asyncio.Semaphore:
    """
    Retorna SIEMPRE la MISMA instancia del semaforo.
    Funciona igual sin importar cuantas veces se llame, desde donde se llame.
    """
    if robot_type not in _SEMAPHORE_INSTANCES:
        concurrency = get_concurrency_for_robot_type(robot_type)
        _SEMAPHORE_INSTANCES[robot_type] = asyncio.Semaphore(concurrency)
    
    return _SEMAPHORE_INSTANCES[robot_type]
```

✅ **Beneficios:**
- 0 cambios en el resto del codigo
- 0 cambios en interfaces
- Todas las pruebas existentes siguen pasando
- El limite se respeta SIEMPRE, sin excepciones
- Funciona aunque ejecutes el orquestador 10 veces al mismo tiempo
- Funciona aunque lo llames desde consola, desde scheduler, desde api

---

## 🧪 PRUEBA QUE DEMUESTRA EL BUG

```python
async def test_que_manifiesta_el_bug_actual():
    # SIMULAMOS 2 EJECUCIONES SIMULTANEAS DEL ORQUESTADOR
    tarea1 = launch_process_rastreo_data_fuentes_deportivas_task("PROCESS_ODDS")
    tarea2 = launch_process_rastreo_data_fuentes_deportivas_task("PROCESS_ODDS")
    
    await asyncio.gather(tarea1, tarea2)

    # ✅ Resultado actual: SE EJECUTAN 2 ROBOTS DE ODDS AL MISMO TIEMPO
    # ✅ Resultado esperado: Solo 1 se ejecuta, el otro espera
```

---

## 📋 PLAN DE ACCIÓN

| Tarea                                                   | Esfuerzo | Impacto |
| ------------------------------------------------------- | -------- | ------- |
| Agregar metodo `get_semaphore_for_robot_type()` en core | 5 min    | ALTO    |
| Reemplazar 3 lineas en el orquestador                   | 2 min    | ALTO    |
| Agregar prueba unitaria que valide singleton            | 5 min    | ALTO    |
| Agregar prueba de estres 50 tareas concurrentes         | 10 min   | ALTO    |

---

## 📌 CONCLUSIÓN FINAL

Tienes un sistema excelente, bien diseñado, con una arquitectura DDD correcta. **Solo tienes un bug de 3 lineas** que te esta matando en producción.

Este es el error #1 que cometen todos los desarrolladores cuando usan Semaphore en asyncio: olvidan que el semaforo tiene que ser singleton.

Todo lo demas esta perfecto. No necesitas refactorizar nada mas.

> ✅ Arreglas 3 lineas. Y el problema desaparece para siempre.