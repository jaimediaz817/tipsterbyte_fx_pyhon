# 📋 DIAGNOSTICO: Excepciones Personalizadas Leagues Manager

📅 Fecha: 21/04/2026
👤 Responsable: JDiaz
🔧 Modulo: Leagues Manager
🏗️ Nivel Arquitectonico: Dominio + Infraestructura

---

## ✅ ESTADO ACTUAL

### 🚩 Problemas detectados:

1.  ❌ **No existen excepciones especificas del dominio**
    - Se esta lanzando `Exception` generica en todos lados
    - No se puede diferenciar errores
    - No hay contexto en los errores
    - No se pueden manejar de forma granular

2.  ❌ **`FuenteExtraccionAdapterFactory` no lanza excepciones tipadas**
    - Solo loggea warning y retorna adaptador por defecto
    - No hay forma de saber cuando el adaptador no existe
    - No hay forma de interceptar este error

3.  ❌ **`BaseRobot` no tiene excepciones de dominio**
    - Cualquier error se propaga como Exception generica
    - No se diferencian errores de scraping, timeout, rate limit

4.  ❌ **Scheduler no tiene excepciones de concurrencia**
    - No se sabe cuando un robot no pudo ejecutarse por semaforo
    - No hay forma de reintentar inteligente

---

## 🎯 EXCEPCIONES ACTUALES EXISTENTES:

| Ubicacion                                   | Nombre                 | Estado                   |
| ------------------------------------------- | ---------------------- | ------------------------ |
| `core/exceptions/fuente_exceptions.py`      | `FuenteException`      | ✅ Existe, pero no se usa |
| `core/exceptions/robot_exceptions.py`       | `RobotException`       | ✅ Existe, pero no se usa |
| `core/exceptions/concurrency_exceptions.py` | `ConcurrencyException` | ✅ Existe, pero no se usa |

✅ Tenemos las clases base ya creadas, solo faltan las especificas por caso de uso.

---

## 🎯 ARQUITECTURA REQUERIDA:

```
BaseDomainException
├── FuenteException
│   ├── FuenteNotFoundException
│   ├── DetalleFuenteInvalidoException
│   ├── AdapterClassNotFoundException
│   └── AdapterInvalidContractException
│
├── RobotException
│   ├── RobotExecutionException
│   ├── ScrapingTimeoutException
│   ├── ScrapingParseException
│   └── ApiRateLimitException
│
└── ConcurrencyException
    ├── SchedulerSemaphoreFullException
    └── RobotAlreadyRunningException
```

---

## 🔴 PUNTOS DE DOLOR ACTUALES:

1.  ❌ No se pueden escribir tests que verifiquen tipos de error
2.  ❌ No se pueden agregar handlers especificos en middleware
3.  ❌ No se puede monitorear por tipo de error
4.  ❌ No hay trazabilidad de fallos
5.  ❌ Rompe el principio de Fail Fast

---

## ✅ PRIORIDAD: ALTA
Es bloqueante para pasar a produccion.