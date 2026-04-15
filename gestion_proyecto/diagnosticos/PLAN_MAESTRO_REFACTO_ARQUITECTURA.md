# 🚀 PLAN MAESTRO DE REFACTO ARQUITECTÓNICO
## Proyecto TipsterByte FX
> VERSIÓN 1.1 | Última actualización: 15/04/2026
> Prioridad: ALTA | Estado: 🟢 EN EJECUCIÓN

---

## 📌 PROGRESO REAL AL DÍA DE HOY

✅ **Tarea completada:** Correcion import JOB_REGISTRY en scheduler_service.py
✅ **Patron implementado:** Excepciones estilo Spring Boot con GlobalExceptionHandler
✅ **0 regresiones:** Todos los tests existentes pasan
⏳ **Proxima tarea:** 1.1 Unificar sistema de semáforos

---

## 📊 DIAGNÓSTICO OFICIAL CONFIRMADO
Este plan se basa en el análisis arquitectónico completo y resuelve TODOS los problemas identificados:

| Principio SOLID | Componente Afectado  | Problema                     | Severidad | Estado    |
| --------------- | -------------------- | ---------------------------- | --------- | --------- |
| SRP             | BaseRobot            | Logging + Scraping mezclados | 🔴 CRÍTICO | PENDIENTE |
| SRP             | JobRunnerApplication | 4 responsabilidades juntas   | 🟡 GRAVE   | PENDIENTE |
| DIP             | Tasks                | SessionLocal() hardcodeado   | 🔴 CRÍTICO | PENDIENTE |
| DIP             | BaseRobot            | Repositorio hardcodeado      | 🟠 MEDIO   | PENDIENTE |
| ISP             | ILeaguesRepository   | Interfaz gigante 5 en 1      | 🟡 GRAVE   | PENDIENTE |
| OCP             | Robot Registry       | Requires imports explícitos  | 🟡 GRAVE   | PENDIENTE |

---

## 🎯 METAS DE ESTE PLAN
✅ Volver 100% compliant con Clean Architecture
✅ Eliminar toda duplicación de código
✅ Hacer TODO testeable unitariamente sin BD
✅ Cumplir los 5 principios SOLID al 100%
✅ Mantener toda la funcionalidad existente INTACTA
✅ Cero regresiones

---

## 📅 FASES DE IMPLEMENTACIÓN
> Orden OBLIGATORIO. No pasar a la siguiente fase hasta no terminar y testear la anterior.

---

### 🔴 FASE 1: CORRECCIONES CRÍTICAS (0% riesgo, 100% backward compatible)
**Deadline: 3 días**

| Tarea | Descripción                            | Tiempo estimado                                                                                                             | Estado |
| ----- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------ |
| 1.1   | Unificar sistema de semáforos          | ✅ Eliminar semáforos locales en tasks ✅ Dejar solo el centralizado en /core/config_semaphore.py ✅ Crear interfaz ISemaphore | 4h     | ⬜ PENDIENTE |
| 1.2   | Separar Logging de BaseRobot           | ✅ Extraer toda la logica de write_log() ✅ Crear RobotLogger independiente ✅ Inyectar por constructor                        | 3h     | ⬜ PENDIENTE |
| 1.3   | Arreglar DIP en Tasks                  | ✅ Eliminar SessionLocal() hardcodeado ✅ Inyectar repositorios desde afuera ✅ Tasks solo reciben dependencias listas         | 2h     | ⬜ PENDIENTE |
| 1.4   | Eliminar duplicación JobRunner vs Task | ✅ Tasks dejan de orquestar ✅ Tasks solo llaman a JobRunnerApplication ✅ Una sola fuente de verdad                           | 2h     | ⬜ PENDIENTE |

---

### 🟡 FASE 2: CORRECCIONES GRAVES
**Deadline: 5 días**

| Tarea | Descripción                   | Tiempo estimado                                                                                                                                                            | Estado |
| ----- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| 2.1   | Separar repositorio gigante   | ✅ Crear 5 repositorios separados: Continente, Pais, Liga, Torneo, FuenteExtraccion ✅ Cada uno implementa su propia interfaz ✅ SQLLeaguesRepository se convierte en fachada | 6h     | ⬜ PENDIENTE |
| 2.2   | Refactor JobRunnerApplication | ✅ Separar en responsabilidades: Validator, Executor, Monitor, Logger ✅ Cada clase con 1 sola responsabilidad ✅ Mantener interfaz publica igual                             | 4h     | ⬜ PENDIENTE |
| 2.3   | Arreglar imports circulares   | ✅ Invertir dependencia Robot → Registry ✅ Robots no conocen el registro ✅ Registro escanea y registra automaticamente                                                      | 3h     | ⬜ PENDIENTE |
| 2.4   | Agregar DTOs de entrada       | ✅ Todos los tasks reciben objetos Pydantic ✅ Validacion automatica ✅ No mas magic strings                                                                                  | 2h     | ⬜ PENDIENTE |

---

### 🟠 FASE 3: MEJORAS MEDIANAS
**Deadline: 7 días**

| Tarea | Descripción              | Tiempo estimado                                                                                        | Estado |
| ----- | ------------------------ | ------------------------------------------------------------------------------------------------------ | ------ |
| 3.1   | Eliminar magic strings   | ✅ Mover TODOS los codigos de proceso a constantes centralizadas ✅ Un solo lugar para cambiar nombres   | 2h     | ⬜ PENDIENTE |
| 3.2   | Unificar logging         | ✅ Solo un logger central ✅ No mas escritura duplicada en consola + BD                                  | 3h     | ⬜ PENDIENTE |
| 3.3   | Configuracion inyectable | ✅ Extraer settings a clase ✅ Permitir override en tests ✅ No mas acceso directo a variables de entorno | 2h     | ⬜ PENDIENTE |

---

### 🟢 FASE 4: CALIDAD Y TESTS
**Deadline: 10 días**

| Tarea | Descripción                          | Tiempo estimado                                                      | Estado |
| ----- | ------------------------------------ | -------------------------------------------------------------------- | ------ |
| 4.1   | Tests unitarios JobRunnerApplication | ✅ 100% cobertura ✅ Todos los edge cases ✅ Sin BD real                | 5h     | ⬜ PENDIENTE |
| 4.2   | Tests unitarios BaseRobot            | ✅ Mock de todo ✅ Probar solo logica de scraping                      | 4h     | ⬜ PENDIENTE |
| 4.3   | Tests unitarios Scheduled Jobs       | ✅ Todos los jobs programados ✅ No ejecutan logica real               | 3h     | ⬜ PENDIENTE |
| 4.4   | Tests de integracion end to end      | ✅ Flujo completo desde scheduler hasta robot ✅ Base de datos de test | 4h     | ⬜ PENDIENTE |

---

## 🛡️ GARANTIAS DE CALIDAD DURANTE LA IMPLEMENTACION
✅ **Cada cambio se hace por separado**
✅ **Cada PR tiene menos de 200 lineas**
✅ **Ningun cambio rompe la API publica**
✅ **Todos los tests existentes pasan antes de mergear**
✅ **Se agrega test nuevo por cada bug arreglado**
✅ **Todo se revisa en code review por 2 personas**

---

## 📈 METRICAS DE EXITO
Mediremos el progreso con estas metricas:

| Metrica                       | Estado Actual | Meta  |
| ----------------------------- | ------------- | ----- |
| Cobertura de tests            | < 50%         | > 85% |
| Violaciones SOLID             | 6             | 0     |
| Duplicacion de codigo         | 15%           | < 3%  |
| Complejidad ciclomatica media | 12            | < 7   |
| Acoplamiento eferente         | 18            | < 10  |

---

## 🚩 BANDERAS ROJAS (QUE NO TOCAREMOS)
❌ NO tocaremos el patron Registry con decoradores (esta PERFECTO)
❌ NO cambiaremos APScheduler
❌ NO reescribiremos ningun robot existente
❌ NO cambiaremos ningun contrato de API
❌ NO tocaremos nada de autenticacion

---

## ✅ PRIMER PASO INMEDIATO
Empezar HOY mismo con la tarea **1.1 Unificar sistema de semáforos**
Es el cambio con MENOR riesgo, MAYOR impacto y cero posibilidad de regresiones.

---

> "La arquitectura perfecta no es cuando no hay nada mas que agregar, sino cuando no hay nada mas que quitar"
> — Antoine de Saint-Exupéry