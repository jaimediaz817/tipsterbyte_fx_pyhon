# ✅ PLAN DE IMPLEMENTACION: Reubicacion Inspecciones LLM
## HU-087: Alineamiento estricto Clean Architecture / DDD

---

## 🎯 DESCRIPCION
Como arquitecto del sistema, necesito separar completamente el codigo operativo y herramientas de desarrollo de los dominios de negocio para mantener la pureza del modelo y cumplir con la regla de dependencias de Clean Architecture.

---

## ✅ CRITERIOS DE ACEPTACION
1.  ✅ Todo el modulo `inspecciones_llm/` se encuentra ubicado en `backend/apps/operations/`
2.  ✅ No existe ninguna referencia a inspecciones_llm dentro de ningun dominio de negocio
3.  ✅ El modulo continua funcionando exactamente igual que antes
4.  ✅ Se actualiza correctamente la configuracion de coverage
5.  ✅ Todas las pruebas unitarias siguen pasando
6.  ✅ No se modifico absolutamente nada de logica de negocio
7.  ✅ Cumplimiento 100% con regla de dependencias: Capa Operations solo depende hacia adentro

---

## 📋 ESTADO ACTUAL DEL SISTEMA
| Componente             | Ubicacion Actual                    | Estado                             |
| ---------------------- | ----------------------------------- | ---------------------------------- |
| inspecciones_llm       | `/inspecciones_llm` (raiz proyecto) | ❌ Fuera de la arquitectura oficial |
| Directorio operations  | No existe aun                       | ⬜ Pendiente                        |
| Configuracion Coverage | No incluye el modulo                | ⬜ Pendiente                        |

---

## 🚀 PLAN DE IMPLEMENTACION POR FASES

| Fase | Descripcion                                               | Estado | Responsable |
| ---- | --------------------------------------------------------- | ------ | ----------- |
| 1    | Crear estructura de directorios oficial                   | ⬜      | Cline       |
| 2    | Mover todo el modulo inspecciones_llm a nueva ubicacion   | ⬜      | Cline       |
| 3    | Actualizar archivo .coveragerc para incluir el nuevo path | ⬜      | Cline       |
| 4    | Verificar integridad de archivos y estructura             | ⬜      | Cline       |
| 5    | Ejecutar pruebas unitarias del modulo                     | ⬜      | Cline       |
| 6    | Eliminar directorio antiguo de la raiz                    | ⬜      | Cline       |

---

## ✅ DEFINICION DE LISTO (DOD)
- [ ] Directorio `backend/apps/operations/` creado
- [ ] Directorio `backend/apps/operations/__init__.py` existe
- [ ] Todos los archivos de inspecciones_llm se encuentran en la nueva ubicacion
- [ ] Archivo `.coveragerc` actualizado con el nuevo path
- [ ] No existe el directorio `/inspecciones_llm` en la raiz
- [ ] Ejecutar `pytest backend/apps/operations/inspecciones_llm/tests/` pasa correctamente
- [ ] Ejecutar coverage report incluye el modulo sin errores
- [ ] Git reconoce correctamente el movimiento de archivos

---

## ⚡ VENTAJAS OBTENIDAS
1.  ✅ No contamina el modelo de negocio de TipsterByte
2.  ✅ Cumplimiento estricto con la regla de dependencias de Clean Architecture
3.  ✅ Se incluye automaticamente en coverage sin hacks ni trucos
4.  ✅ Se separa perfectamente codigo de negocio vs codigo operativo
5.  ✅ Si algun dia se puede desactivar completamente sin tocar nada mas
6.  ✅ Aplica para todos los principios de separacion de responsabilidades
7.  ✅ Estructura alineada con estandares de proyectos serios

---

## ❌ LO QUE NO SE VA A HACER
- ❌ No se modifica absolutamente ninguna logica dentro de inspecciones_llm
- ❌ No se cambia ningun import interno del modulo
- ❌ No se toca ningun archivo de dominio de negocio
- ❌ No se modifican dependencias ni requirements

---

## 📊 CRONOGRAMA ESTIMADO
| Tarea                  | Tiempo Estimado |
| ---------------------- | --------------- |
| Creacion estructura    | 1 minuto        |
| Movimiento archivos    | 2 minutos       |
| Actualizacion coverage | 1 minuto        |
| Verificacion y pruebas | 3 minutos       |
| **TOTAL**              | **✅ 7 MINUTOS** |

---

## 🔒 BLOQUEOS Y DEPENDENCIAS
✅ Sin bloqueos
✅ Sin dependencias externas
✅ Se puede implementar en caliente sin afectar produccion

---

## 📝 REGISTRO DE CAMBIOS
| Fecha      | Estado     | Comentario                                |
| ---------- | ---------- | ----------------------------------------- |
| 23/04/2026 | ACORDADO ✅ | Plan aprobado y listo para implementacion |

---

> ✅ Este plan cumple con todas las reglas establecidas en .clinerules/default-rules.md
> ✅ Alineado 100% con Clean Architecture y DDD
> ✅ Sin efectos colaterales, implementacion segura