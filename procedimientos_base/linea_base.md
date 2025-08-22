# HUS - TAREAS

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

## Objetivos Semanales: Checklist de Casos de Uso y Propuestas de Valor

A continuación se presentan los objetivos semanales organizados como checklist. Cada ítem representa un caso de uso o propuesta de valor a implementar:

### Semana 1 - FINAL JULIO

- [x] **Crear un script de migración de base de datos**  
    _Implementar un script que permita crear y aplicar migraciones a la base de datos utilizando Alembic._
- [x] **Organizar las bases SQL sueltas**  
    _Ubicar y estructurar los archivos SQL en la raíz de `core/db/sql/...` para mejorar la gestión y el acceso._

### Semana 2 - COMIENZO AGOSTO

04 AGOSTO

- [x] **Actualizar el README**  
    _Incluir instrucciones claras sobre cómo utilizar el script de migración y los comandos de gestión de base de datos._
- [x] **probar de nuevo los comandos en ambos motores de BD**
    _Verificar que los comandos de migración y gestión de base de datos funcionen correctamente tanto en PostgreSQL como en MongoDB._
- [ ] **Entender y aplicar cambios incrementales en la ejecución de procesos en paralelo**  
    _Investigar y aplicar técnicas para ejecutar procesos de migración y seeders de forma paralela,
     mejorando la eficiencia del sistema._
- [x] **Crear modelo: scheduled_process_config**
- [x] **Crear modelo: process**
- TODO: tb-hu-auth-01-users-or-clients: pendiente definir si es user_id o client_id
- [ ] **Crear modelo: process_runs**
- [ ] **Crear modelo: process_run_log**
- [ ] **Crear mel primer runner relativo a población e inspección de datos iniciales (países, equipos, ligas)**
- [ ] **Actualizar el diagrama de google draw.io para incluir el módulo: platform_config**

- [ ] **Entender y aplicar cambios incrementales en la ejecución de procesos en paralelo**
- [ ] **Scheduler de Scraper #1 fuente deportiva equipos por liga**
    _Implementar un sceduler responsable de llevar a cabo primer proceso de scraper que es consultar una web deportiva para saber que equipos ascienden y descienden, con ello de paso se busca autopoblar de paso las tablas pertinentes como país y equipos por liga de dicho páis._

- TODO: tb-hu-core-01-commands-refactors: Refactorizar generación de key secret manualmente por el uso de comandos
- [ ] **Refactorizar secret.py**
    _Mejorar el módulo de secretos para incluir funciones que verifiquen la existencia de claves específicas, facilitando la gestión de secretos en el proyecto._
- [ ] **Refactorizar manage.py**
    _Mejorar el script de gestión para simplificar la ejecución de comandos y la interacción con el entorno de desarrollo en cuanto a la generación de fernet.keys mediante el uso de comandos._
- [ ] **Probar los comandos refactorizados**
    _Verificar que los comandos refactorizados funcionen correctamente y cumplan con los requisitos del proyecto
    módulo: core._

TODO: tb-hu-cli-01-db-diagnostics: Implementar Diagnóstico de Base de Datos y Refactorizar CLI

- [ ] **Crear Módulo de Inspector de BD** (2.5h)  
    Crear la lógica en `core/db/sql/db_inspector.py` para comparar los modelos definidos en el código con las tablas reales en la base de datos. Incluir pruebas unitarias para la lógica de comparación.

- [ ] **Refactorizar manage.py a Comandos Aislados** (2.0h)  
    Mover la lógica de los grupos de comandos (`sql`, `nosql`, etc.) a una nueva carpeta `commands/` para desacoplar y limpiar `manage.py`, dejando este como orquestador.

- [ ] **Implementar Comando sql status** (1.5h)  
    Crear el comando `status` dentro de `commands/sql_commands.py` que use el nuevo inspector y Alembic para mostrar un diagnóstico completo del estado de la BD.

- [ ] **Documentar Comando sql status en README** (0.5h)  
    Añadir la sección de uso del nuevo comando, con ejemplos de salida, al `README.md` principal.

- [ ] **Probar Funcionalidad y Regresión** (1.5h)  
    Verificar que el nuevo comando `status` funcione y que los comandos refactorizados (`migrate`, `seed`, `secrets`, etc.) no tengan regresiones.

- TODO: tb-hu-structure-commands-refactors: Refactorización e inspección de comandos para no sql después del cambio en varios apartados.

- [] **Testear comandos NO SQL STATE** (2.0h)  
    Comando: backup y restore
    se espera que no fallen y muestre LOG en la terminal
    RESULTADOS/OBSERVACIONES: Crea el backup en la carpeta correcta dentro dfe backend/backups/...
    - restore: restaura y me informa el total de documentos por colección restaurada: OK
    - backup: crea un nuevo backup y me informa el nombre del archivo: OK
    - clear-migrations: limpia las migraciones y me informa del estado: OK

- [X] **Testear comandos NO SQL STATE** (2.0h)  
    Comando: reset y clear
    se espera que no fallen y muestre LOG en la terminal
    RESULTADOS/OBSERVACIONES: Se ejecuta bien el comando clear, pide: CONFIRMAR:ACCION
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
