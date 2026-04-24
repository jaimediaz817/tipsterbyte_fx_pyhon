# ✅ HISTORIA DE USUARIO: Backup Selectivo Modular
> **ID**: HU-BACKUP-001  
> **Versión**: 1.0  
> **Estado**: 🚧 EN PROGRESO  
> **Fecha Creación**: 22/04/2026  
> **Responsable**: Equipo Backend

---

## 📋 DESCRIPCION
Como administrador del sistema, quiero poder seleccionar que tablas incluir o excluir en los backups para poder optimizar el tamaño, velocidad y proposito del backup sin perder la integridad referencial de la base de datos.

---

## ✅ CRITERIOS DE ACEPTACION

| #   | Criterio                                                                            | Estado     |
| --- | ----------------------------------------------------------------------------------- | ---------- |
| 1   | ✅ Por defecto TODO se incluye. Ninguna tabla se excluye automaticamente             | ✅ ACORDADO |
| 2   | ✅ Flag `--exclude-logs` excluye automaticamente todas las tablas de logs historicos | ✅ ACORDADO |
| 3   | ✅ Flag `--exclude tabla1 tabla2` permite excluir tablas especificas                 | ✅ ACORDADO |
| 4   | ✅ El sistema detecta automaticamente dependencias de Foreign Keys                   | ✅ ACORDADO |
| 5   | ✅ No permite excluir una tabla si otra depende de ella                              | ✅ ACORDADO |
| 6   | ✅ Flag `--cascade` permite excluir todo el arbol de dependencias                    | ✅ ACORDADO |
| 7   | ✅ 100% compatible hacia atras. No rompe ningun comando existente                    | ✅ ACORDADO |
| 8   | ✅ Mantiene toda la funcionalidad actual de backup y restore                         | ✅ ACORDADO |

---

## 🎯 TABLAS A EXCLUIR DISPONIBLES
| Categoria               | Tablas                                                 | Tamaño estimado            |
| ----------------------- | ------------------------------------------------------ | -------------------------- |
| 📌 Logs Historicos       | `process_run_logs`, `session_log`, `access_log`        | 90% del tamaño total de BD |
| 📌 Historial Ejecuciones | `process_run`                                          | 7% del tamaño              |
| 📌 Configuracion         | `process`                                              | 2% del tamaño              |
| 📌 Datos Maestros        | `continentes`, `paises`, `ligas`, `torneos`, `fuentes` | 1% del tamaño              |

---

## 🚀 PLAN DE IMPLEMENTACION
### Cronograma estimado: 3 dias

| Fasem    | Tarea                                                    | Responsable | Estado      | Fecha Estimada |
| -------- | -------------------------------------------------------- | ----------- | ----------- | -------------- |
| 🔹 FASE 1 | Analizar grafo de Foreign Keys desde SQLAlchemy MetaData |             | ⬜ PENDIENTE | Dia 1          |
| 🔹 FASE 1 | Implementar detector automatico de dependencias          |             | ⬜ PENDIENTE | Dia 1          |
| 🔹 FASE 2 | Añadir flags nuevos al comando `sql backup`              |             | ⬜ PENDIENTE | Dia 2          |
| 🔹 FASE 2 | Añadir validacion de integridad pre-backup               |             | ⬜ PENDIENTE | Dia 2          |
| 🔹 FASE 3 | Implementar flag `--cascade` para exclusion recursiva    |             | ⬜ PENDIENTE | Dia 3          |
| 🔹 FASE 3 | Pruebas unitarias y de integracion                       |             | ⬜ PENDIENTE | Dia 3          |
| 🔹 FASE 3 | Documentacion y actualizacion de manuales                |             | ⬜ PENDIENTE | Dia 3          |

---

## 📌 BLOQUEOS Y DEPENDENCIAS
- ❌ Ningun bloqueo actualmente
- ✅ No depende de ningun otro desarrollo
- ✅ Se puede implementar en paralelo al resto de historias de usuario de Web Scraping

---

## 📊 ESTADO ACTUAL DEL SISTEMA
| Item                     | Estado        |
| ------------------------ | ------------- |
| ✅ Sistema Backup Actual  | 🟢 FUNCIONANDO |
| ✅ Sistema Restore Actual | 🟢 FUNCIONANDO |
| ✅ Pruebas existentes     | 🟢 PASANDO     |
| ✅ Integridad Referencial | 🟢 VERIFICADA  |

---

## 🎯 DEFINICION DE LISTO (DOD)
- [ ] Todos los criterios de aceptacion cumplidos
- [ ] Todas las pruebas unitarias pasando
- [ ] Prueba de integracion creada y pasando
- [ ] Documentacion actualizada
- [ ] Comando funcionando tanto en desarrollo como en produccion
- [ ] No rompe ningun comando existente
- [ ] Verificado que no se pierde integridad referencial

---

### 📝 NOTAS ADICIONALES
> Esta mejora es completamente opcional y no bloquea ningun otro desarrollo. Se puede empezar Web Scraping inmediatamente mientras se implementa esta funcionalidad en paralelo.
>
> El sistema actual es 100% seguro y funcional.