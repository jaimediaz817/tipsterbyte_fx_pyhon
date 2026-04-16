# HUS - TAREAS

Para este proyecto se sugiere llevar a  cabo la siguiente nomenclatura 

## Resumen de Esfuerzo Estimado (Epics tb-hu-*)

| Código                               | Descripción                                                   | Esfuerzo (h) | Holgura Pruebas (h) | Total (h) | Notas / Estado |
|--------------------------------------|---------------------------------------------------------------|-------------:|--------------------:|----------:|----------------|
| tb-hu-cli-01-db-diagnostics          | Diagnóstico de BD y refactor CLI (inspector, commands, status)| 5.5          | 2.5                 | 8.0       | 0% progreso (subtareas sin completar) |
| tb-hu-core-01-commands-refactors     | Refactor generación y gestión de secrets / commands           | -            | -                   | -         | Subtareas definidas, sin estimación |
| tb-hu-auth-01-users-or-clients       | Definir uso de user_id vs client_id                           | -            | -                   | -         | En análisis |
| **Total (estimado)**                 |                                                               | **5.5**      | **2.5**             | **8.0**   | (Sólo tareas estimadas) |

Detalle subtareas (mapeo a tb-hu-cli-01-db-diagnostics):
- Crear Módulo de Inspector de BD (HU-CORE-02) 1.5h + 1.0h holgura
- Refactorizar manage.py a Comandos Aislados (HU-CLI-01) 1.5h + 0.5h holgura
- Implementar Comando sql status (HU-CLI-02) 1.0h + 0.5h holgura
- Documentar Comando sql status en README (HU-DOCS-03) 0.5h + 0.0h holgura
- Probar Funcionalidad y Regresión (HU-TEST-01) 1.0h + 0.5h holgura

-----------------------------------------------------------------------------------------------------

## Fases de Desarrollo y Checklist

A continuación se presentan los objetivos organizados por fases de desarrollo.

### Fase 0: Configuración Inicial y Estructura de BD

tb-hu-f0-t1-creacion-arq-arranque

- [x] **Crear un script de migración de base de datos**  
    _Implementar un script que permita crear y aplicar migraciones a la base de datos utilizando Alembic._
- [x] **Organizar las bases SQL sueltas**  
    _Ubicar y estructurar los archivos SQL en la raíz de `core/db/sql/...` para mejorar la gestión y el acceso._

tb-hu-f0-t2-refactorizar-parents-all
- [ ] Refactorizar todas las importaciones que tengan parent.parent-... esto quedo deprecado!
- [ ] Testear los cambios realizados mediante ejecuciones y comandos


-----------------------------------------------------------------------------------------------------

### Fase 1: Comandos de BD (SQL y NoSQL) y Documentación

## NOTE: HU: tb-hu-creacion-arq-arranque

- [x] **Actualizar el README**  
    _Incluir instrucciones claras sobre cómo utilizar el script de migración y los comandos de gestión de base de datos._
- [x] **Probar de nuevo los comandos en ambos motores de BD**
    _Verificar que los comandos de migración y gestión de base de datos funcionen correctamente tanto en PostgreSQL como en MongoDB._
- [X] **Testear comandos NO SQL (reset y clear)**  
    _Comando: reset y clear. Se espera que no fallen y muestren LOG en la terminal. Se ejecuta bien el comando clear, pide: CONFIRMAR:ACCION._
- [X] ~~***Testear comandos NO SQL (backup y restore)***~~ [2025-08-21]  
    _Comando: backup y restore. Se espera que no fallen y muestren LOG en la terminal._
- [ ] Refactorizar todas las importaciones que tengan parent.parent-... esto quedo deprecado!
- [ ] Testear todo nuevamente: sql y nosql para medir el impacto
- [X] ~~*Complementar implementación de llamados asincronos para cada cliente: crear runner básico*~~ [2025-08-23]
- [X] ~~*implementar los mocks respectivos para simular repositorio de clientes y procesos activos*~~ [2025-08-23]





### Fase 2: Nuevos Modelos de Datos y Procesos Programados

- [X] ~~*Crear modelo: scheduled_process_config*~~ [2025-08-21]
- [X] ~~*Crear modelo: process*~~ [2025-08-21]
- [X] ~~***Crear modelo: process_runs***~~ [2025-08-21]
- [X] ~~***Crear modelo: process_run_log***~~ [2025-08-21]
- [X] ~~***Crear el primer runner relativo a población e inspección de datos iniciales (países, equipos, ligas)***~~ [2025-08-23]
- [ ] **Scheduler de Scraper #1 fuente deportiva equipos por liga**
    _Implementar un scheduler responsable de llevar a cabo el primer proceso de scraper para consultar una web deportiva, identificar ascensos/descensos y poblar las tablas de país y equipos por liga._


-----------------------------------------------------------------------------------------------------

### Fase 3: Refactorización del CLI y Core

**HU: tb-hu-core-01-commands-refactors** - Refactorizar generación de key secret manualmente por el uso de comandos.
- [ ] **Refactorizar secret.py**
    _Mejorar el módulo de secretos para incluir funciones que verifiquen la existencia de claves específicas._
- [ ] **Refactorizar manage.py**
    _Mejorar el script de gestión para simplificar la ejecución de comandos para la generación de fernet.keys._
- [ ] **Probar los comandos refactorizados**
    _Verificar que los comandos refactorizados funcionen correctamente en el módulo `core`._

**HU: tb-hu-cli-01-db-diagnostics** - Implementar Diagnóstico de Base de Datos y Refactorizar CLI.
- [ ] **Crear Módulo de Inspector de BD** (2.5h)  
    _Crear la lógica en `core/db/sql/db_inspector.py` para comparar modelos con tablas reales. Incluir pruebas unitarias._
- [X] ~~***Refactorizar manage.py a Comandos Aislados** (2.0h)*~~ [2025-08-21]  
    _Mover la lógica de los grupos de comandos (`sql`, `nosql`) a una nueva carpeta `commands/` para desacoplar `manage.py`._
- [X] ~~***Implementar Comando sql status** (1.5h)*~~ [2025-08-21]  
    _Crear el comando `status` en `commands/sql_commands.py` que use el inspector y Alembic para mostrar el estado de la BD._
- [ ] **Documentar Comando sql status en README** (0.5h)  
    _Añadir la sección de uso del nuevo comando, con ejemplos de salida, al `README.md`._
- [ ] **Probar Funcionalidad y Regresión** (1.5h)  
    _Verificar que el nuevo comando `status` funcione y que los comandos refactorizados no tengan regresiones._


-----------------------------------------------------------------------------------------------------

### Fase 4: Análisis y Tareas Futuras

- [ ] **HU: tb-hu-auth-01-users-or-clients** - Definir uso de user_id vs client_id (En análisis).
- [ ] **Entender y aplicar cambios incrementales en la ejecución de procesos en paralelo**  
    _Investigar y aplicar técnicas para ejecutar procesos de migración y seeders de forma paralela._
- [ ] **Actualizar el diagrama de draw.io para incluir el módulo: platform_config**
- [ ] **HU: tb-hu-structure-commands-refactors** - Refactorización e inspección de comandos para NoSQL después de los cambios.

<!-- 
TODO: Pendiente validar todo lo referente a sql
TODO: Pendiente validar todo lo referente a nosql
-->

> **Pautas para mantener este formato en Markdown:**
>
> - Utiliza listas de verificación (`- [ ]`) para marcar el progreso de cada objetivo.
> - Agrega descripciones breves para cada objetivo.
> - Organiza los objetivos por semana o sprint.
> - Actualiza el checklist conforme avances en cada tarea.
