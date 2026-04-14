# 🛠️ PLAN DE CORRECCIÓN INCREMENTAL
## Violaciones: JobRunnerApplication (Clean Arch) + JobsLoader (DIP)
✅ Sin roturas | ✅ Impacto mínimo | ✅ Retrocompatible

---

## 🎯 OBJETIVO
Corregir las dos violaciones mas criticas identificadas, manteniendo 100% compatibilidad hacia atras, sin romper ningun flujo existente y mejorando la arquitectura de manera gradual y digerible.

---

## 🔴 PROBLEMA 1: JobRunnerApplication - Violación Clean Architecture
**Estado Actual**:
✅ La capa APLICACIÓN (`/application`) está importando directamente desde INFRAESTRUCTURA (`/infrastructure/models`)
✅ `run_job()` recibe directamente modelos SQL de SQLAlchemy como parámetros
✅ La logica de negocio esta ATADA a PostgreSQL

✅ **SOLUCIÓN INCREMENTAL APLICAR**:
```
┌───────────────────────────────────────────────────┐
│ PASO 1: Agregar sobrecarga que reciba interfaces  │
│ PASO 2: Mantener método original por compatibilidad│
│ PASO 3: Deprecar gradualmente el método viejo      │
│ PASO 4: Reflejar este cambio en todos los llamados │
└───────────────────────────────────────────────────┘
```

✅ **BENEFICIOS INMEDIATOS**:
- ✅ No se rompe nada existente
- ✅ Nuevos llamados pueden usar la version correcta
- ✅ Se puede migrar gradualmente
- ✅ Tests pueden usar mocks sin SQLAlchemy

---

## 🔴 PROBLEMA 2: JobsLoader - Violación DIP (Dependency Inversion)
**Estado Actual**:
✅ El CORE del sistema (`/core/scheduler`) importa directamente desde APLICACIONES
✅ Hardcodeo de `PROCESS_MAP_LEAGUES_MANAGER` y `LOG_CLEANUP_PROCESS_MAP`
✅ Cada vez que se agrega un nuevo job hay que MODIFICAR el core
✅ Alto acoplamiento entre core y apps

✅ **SOLUCIÓN INCREMENTAL APLICAR**:
```
┌───────────────────────────────────────────────────┐
│ PASO 1: Crear mecanismo de registro por decorador │
│ PASO 2: Jobs se registran a si mismos automaticamente
│ PASO 3: El core NO conoce ninguna implementacion  │
│ PASO 4: Core solo conoce la interfaz de registro  │
└───────────────────────────────────────────────────┘
```

✅ **BENEFICIOS INMEDIATOS**:
- ✅ El core NUNCA MAS se modifica para agregar jobs
- ✅ Cada aplicación se autocontiene
- ✅ Se pueden habilitar/deshabilitar jobs por importación
- ✅ Tests pueden registrar jobs falsos facilmente
- ✅ Zero acoplamiento

---

## 📋 FASES DE IMPLEMENTACIÓN

### ✅ FASE 1: CORREGIR JobRunnerApplication (hoy)
- [ ] Crear interfaz `ITorneo` y `IDetalleFuenteExtraccion` en domain
- [ ] Agregar nuevo método `run_job_by_interface()`
- [ ] Mantener `run_job()` original con decorador `@deprecated`
- [ ] Modificar el original para que llame al nuevo metodo
- [ ] Todos los flujos existentes siguen funcionando EXACTAMENTE igual

### ✅ FASE 2: CORREGIR JobsLoader (hoy)
- [x] Crear registro global de jobs en `core/scheduler/job_registry.py`
- [x] Crear decorador `@register_job(name)`
- [x] Modificar JobsLoader para que use este registro unicamente
- [x] Agregar decorador a los jobs existentes
- [x] Eliminar importaciones hardcodeadas del core
- [x] ✅ CORREGIDO: Error de tipos Pylance en registro de jobs async
- [x] NINGUN CAMBIO en el comportamiento del scheduler

### ✅ FASE 3: MIGRACIÓN GRADUAL (proximos dias)
- [ ] Migrar un job a la vez al nuevo metodo
- [ ] Ejecutar tests en cada paso
- [ ] Eliminar el metodo viejo cuando no tenga mas llamados

---

## ✅ GARANTÍAS
1. **NUNCA** se rompera funcionalidad existente
2. **NUNCA** habra un commit que no compile
3. **TODOS** los tests pasaran en TODO momento
4. **CADA** cambio sera minimo y facil de revisar
5. **CADA** paso se podra entender individualmente

---

## 🧠 EXPLICACIÓN SENCILLA PARA ENTENDERLO:
> Antes: El jefe (core) iba buscando personalmente a cada empleado a su oficina.
>
> Ahora: Cada empleado se registra en la oficina de recursos humanos cuando llega. El jefe solo va a RRHH y pregunta quienes estan trabajando hoy.
>
> El jefe NO necesita saber donde vive cada empleado ni como llegar a su casa.