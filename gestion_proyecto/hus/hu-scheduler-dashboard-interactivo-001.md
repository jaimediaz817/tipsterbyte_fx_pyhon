# HU-SCHEDULER-DASHBOARD-INTERACTIVO-001

## 🎯 Descripcion como usuario final
Como desarrollador, quiero que todos los cambios propuestos automaticamente por el agente aparezcan en el dashboard con botones de aprobacion/rechazo, para que ningun cambio se aplique sin mi consentimiento explicito.

## ✅ Criterios de aceptacion

| ID     | Descripcion                                                                       | Estado |
| ------ | --------------------------------------------------------------------------------- | ------ |
| CA-001 | La tarea de monitoreo de documentos NUNCA modificara archivos directamente        | ⬜      |
| CA-002 | Se creara nuevo estado `ESPERA_APROBACION` en el ciclo de vida de las tareas      | ⬜      |
| CA-003 | Cada cambio propuesto tendra: descripcion, diff y ruta del archivo afectado       | ⬜      |
| CA-004 | El dashboard mostrara cada cambio pendiente con 2 botones: ✅ Aceptar / ❌ Rechazar | ⬜      |
| CA-005 | Existiran endpoints API para aprobar y rechazar cambios                           | ⬜      |
| CA-006 | Ningun cambio se aplicara en el codigo hasta que sea explicitamente aprobado      | ⬜      |
| CA-007 | Existira historial completo de todas las decisiones tomadas                       | ⬜      |
| CA-008 | El sistema mantendra el patron de cero dependencias externas                      | ⬜      |

## 🚀 Plan de implementacion por fases

| Fase   | Descripcion                                                                              | Estado |
| ------ | ---------------------------------------------------------------------------------------- | ------ |
| Fase 1 | Añadir nuevo estado y estructura de cambios pendientes                                   | ⬜      |
| Fase 2 | Añadir endpoints API de aprobacion/rechazo                                               | ⬜      |
| Fase 3 | Modificar tarea de monitoreo para generar cambios propuestos, no modificaciones directas | ⬜      |
| Fase 4 | Actualizar dashboard con botones interactivos y vista de diff                            | ⬜      |
| Fase 5 | Añadir sistema de historial y auditoria                                                  | ⬜      |

## ✅ Definicion de Listo (DOD)
1. Todos los criterios de aceptacion cumplidos
2. Tests unitarios creados y pasando al 100%
3. Dashboard funciona sin refresco manual
4. No hay cambios automaticos sin aprobacion
5. Documentacion actualizada
6. Funciona en modo desarrollo sin afectar produccion

## 📋 Cronograma estimado
- Tiempo estimado total: 8 horas
- Prioridad: ALTA
- Complejidad: MEDIA

## 📌 Estado actual del sistema
- ✅ Agente Supervisor funcionando
- ✅ Tarea de monitoreo creada
- ✅ Dashboard basico existente
- ❌ No existe sistema de aprobacion
- ❌ Los cambios se aplican automaticamente actualmente

## 🔒 Bloqueos y dependencias
- Ninguna. El sistema es completamente standalone dentro del modulo de inspecciones_llm.

---
* Creado: 23/04/2026
* Responsable: Agente Supervisor
* Estado: ACORDADO ✅