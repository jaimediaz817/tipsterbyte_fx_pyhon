# HU-002: Sistema de Aprobacion Manual de Cambios Automaticos

---

## 🎯 Identificador Unico
**HU-002** | **Fecha Creacion**: 23/04/2026 | **Autor**: Sistema Automatizado

## 📋 Descripcion como usuario final
> Como administrador del sistema, QUIERO que TODOS los cambios automaticos que el robot quiera realizar en archivos o base de datos PASEN POR MI APROBACION MANUAL ANTES de ser aplicados, para que NUNCA mas se realicen modificaciones sin mi consentimiento explicito.

---

## ✅ Criterios de Aceptacion NUMERADOS y MEDIBLES
1. ❌ **Ningun cambio automatico se aplicara directamente** en ningun archivo o base de datos
2. ✅ Todo cambio propuesto entrara en una cola de aprobacion pendiente
3. ✅ Cada cambio incluira: descripcion, diff completo, archivo afectado, fecha y autor
4. ✅ El dashboard mostrara TODOS los cambios pendientes en tiempo real
5. ✅ Por cada cambio habra DOS botones exclusivos: `✅ ACEPTAR` y `❌ RECHAZAR`
6. ✅ Solo despues de presionar ACEPTAR se aplicara el cambio
7. ✅ Si se presiona RECHAZAR el cambio se descarta permanentemente
8. ✅ Se mantendra historial completo de todas las decisiones tomadas
9. ✅ El sistema de monitoreo NO tendra permisos para modificar nada directamente
10. ✅ Todo el flujo funcionara sin interrupcion del scheduler existente

---

## 🚀 Plan de Implementacion por Fases

| Fase      | Descripcion                                                 | Estado      |
| --------- | ----------------------------------------------------------- | ----------- |
| 🔹 Fase 1  | Añadir estado `ESPERA_APROBACION` en enumerador EstadoTarea | ⬜ PENDIENTE |
| 🔹 Fase 2  | Crear entidad de dominio `CambioPropuesto`                  | ⬜ PENDIENTE |
| 🔹 Fase 3  | Implementar repositorio y cola de cambios pendientes        | ⬜ PENDIENTE |
| 🔹 Fase 4  | Modificar tarea de monitoreo para NO modificar directamente | ⬜ PENDIENTE |
| 🔹 Fase 5  | Añadir endpoints `/api/aprobar/{id}` y `/api/rechazar/{id}` | ⬜ PENDIENTE |
| 🔹 Fase 6  | Actualizar dashboard con lista de cambios pendientes        | ⬜ PENDIENTE |
| 🔹 Fase 7  | Implementar renderizado de botones interactivos             | ⬜ PENDIENTE |
| 🔹 Fase 8  | Añadir vista previa diff por cada cambio                    | ⬜ PENDIENTE |
| 🔹 Fase 9  | Implementar logica de aplicacion de cambio al aprobar       | ⬜ PENDIENTE |
| 🔹 Fase 10 | Añadir auditoria y historial de decisiones                  | ⬜ PENDIENTE |

---

## ✅ Definicion de Listo (DOD)
1. [ ] Todos los criterios de aceptacion se cumplen al 100%
2. [ ] Existen pruebas unitarias para cada componente nuevo
3. [ ] El scheduler sigue funcionando exactamente igual que antes
4. [ ] Ningun cambio automatico se aplica sin aprobacion
5. [ ] Los botones funcionan correctamente en el dashboard
6. [ ] Se puede aprobar y rechazar cambios sin errores
7. [ ] No hay degradacion de rendimiento en el sistema
8. [ ] El plan de migracion esta documentado
9. [ ] El cambio ha sido probado en entorno de desarrollo
10. [ ] Se ha actualizado la documentacion funcional

---

## 📅 Cronograma Estimado
| Tarea                     | Tiempo Estimado          |
| ------------------------- | ------------------------ |
| Dominio y Entidades       | 30 min                   |
| Repositorio y Cola        | 20 min                   |
| Modificacion Tareas       | 15 min                   |
| Endpoints API             | 15 min                   |
| Dashboard UI              | 45 min                   |
| Logica Aplicacion Cambios | 30 min                   |
| Pruebas Unitarias         | 40 min                   |
| **TOTAL**                 | **✅ 3 horas 15 minutos** |

---

## 🔍 Estado Actual del Sistema
> ✅ El scheduler y monitoreo funcionan correctamente
> ✅ El dashboard ya esta implementado y accesible
> ✅ Existe estructura de entidades y repositorios
> ✅ Las tareas automaticas ya se ejecutan periodicamente
> ✅ Actualmente las tareas modifican archivos directamente

---

## ⛔ Bloqueos y Dependencias
- ✅ Sin dependencias externas
- ✅ No requiere cambios en infraestructura
- ✅ No requiere migraciones de base de datos iniciales
- ✅ Compatible con version actual de FastAPI

---

## 📋 Tabla de Estados General
| Estado      | Icono | Descripcion                      |
| ----------- | ----- | -------------------------------- |
| ACORDADO    | ✅     | Requisitos definidos y aprobados |
| PENDIENTE   | ⬜     | No iniciado aun                  |
| EN PROGRESO | 🚧     | Implementacion en curso          |
| EN PRUEBA   | 🧪     | En fase de pruebas               |
| COMPLETADO  | ✅     | Terminado y verificado           |

> **Estado Actual**: ✅ ACORDADO | LISTO PARA EMPEZAR IMPLEMENTACION

---

## 📌 Reglas Inquebrantables Aplicables
1. ✅ Ningun codigo se ejecuta sin aprobacion manual
2. ✅ El sistema siempre falla del lado seguro
3. ✅ Por defecto TODO cambio es rechazado hasta que se apruebe
4. ✅ No hay excepciones, ni casos especiales
5. ✅ Todo queda registrado y auditable