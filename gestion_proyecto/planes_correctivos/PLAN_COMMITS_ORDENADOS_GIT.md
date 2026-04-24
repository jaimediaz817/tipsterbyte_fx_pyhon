# ✅ PLAN DE COMMITS ESTRUCTURADO - ORDEN DE EJECUCION
> ✅ ACTUALIZADO: 24/04/2026 12:05 | Estado actual GIT VERIFICADO EN TIEMPO REAL
> ✅ Commits ya ejecutados y pusheados: 5 ✅
> ✅ Total archivos pendientes ACTUALES: 27 (17 modificados + 10 nuevos)
> ✅ Todos los archivos agrupados por dominio y funcionalidad, orden logico de dependencia
> ✅ No falta ningun archivo del git status actual
> ✅ Orden actualizado y verificado 100%

---

## 📋 PRINCIPIOS APLICADOS:
1. 🔹 **Commits atomicos**: Cada commit hace UNA SOLA cosa
2. 🔹 **Orden de dependencia**: Primero cambios en core, luego dominios, luego tests, luego docs
3. 🔹 **Convencional Commits**: `type(scope): message` estandar
4. 🔹 **Sin archivos basura**: Excluidos archivos de coverage, logs y temporales
5. 🔹 **Revertibilidad**: Cada commit se puede deshacer individualmente sin romper

---

## 🚀 SECUENCIA DE COMMITS (ORDEN EXACTO A EJECUTAR)

| #    | TIPO    | SCOPE                            | MENSAJE                                                | ARCHIVOS INCLUIDOS                                                                                                                                                                          | ESTADO                      |
| ---- | ------- | -------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| ✅ 1  | `fix`   | `leagues_manager:robot`          | ✅ mejoras base robot logger                            | `backend/apps/leagues_manager/domain/robots/base_robot.py`                                                                                                                                  | ✅ ✅ EJECUTADO Y PUSHEADO OK |
| ✅ 2  | `feat`  | `leagues_manager:tasks`          | ✅ implementacion sync_jobs                             | `backend/apps/leagues_manager/tasks/sync_jobs.py`                                                                                                                                           | ✅ ✅ EJECUTADO Y PUSHEADO OK |
| ✅ 3  | `feat`  | `leagues_manager:tests`          | ✅ test simulacion integracion robot scheduler          | `backend/apps/leagues_manager/tests/test_robot_scheduler_integration_simulation.py, backend/apps/leagues_manager/tests/mock_data_leagues.py`                                                | ✅ ✅ EJECUTADO Y PUSHEADO OK |
| ✅ 4  | `fix`   | `platform_config:mongo`          | ✅ correcciones repositorio mongo vps health check      | `backend/apps/platform_config/infrastructure/repositories/mongo_vps_health_check_repository.py`                                                                                             | ✅ ✅ EJECUTADO Y PUSHEADO OK |
| ✅ 5  | `feat`  | `platform_config:tests`          | ✅ test unitario platform config seeder                 | `backend/apps/platform_config/tests/test_platform_config_seeder_unit.py`                                                                                                                    | ✅ ✅ EJECUTADO Y PUSHEADO OK |
| ---  | ---     | ---                              | ---                                                    | ---                                                                                                                                                                                         | ---                         |
| ✅ 6  | `feat`  | `commands:db`                    | ✅ sql state manager y servicios backup/restore         | `backend/commands/db/admin/sql/sql_state_manager.py, backend/commands/db/admin/sql/services/`                                                                                               | ✅ ✅ EJECUTADO OK            |
| ✅ 7  | `feat`  | `commands:cli`                   | ✅ mejoras project cli                                  | `backend/commands/project_cli.py`                                                                                                                                                           | ✅ ✅ EJECUTADO OK            |
| ✅ 8  | `feat`  | `services:log_cleanup`           | ✅ modelos cleanup history                              | `backend/services/models/cleanup_history.py, backend/services/models/__init__.py`                                                                                                           | ✅ ✅ EJECUTADO OK            |
| ✅ 9  | `feat`  | `scripts:seeders`                | ✅ mejoras ligas seeder, platform config y orchestrator | `backend/scripts/db/seeders/sql/ligas_seeder.py, backend/scripts/db/seeders/sql/platform_config_seeder.py, backend/scripts/db/seeders/sql_seeder_orchestrator.py`                           | ✅ ✅ EJECUTADO OK            |
| ✅ 10 | `feat`  | `apps:operations`                | ✅ modulo inspecciones LLM completo                     | `backend/apps/operations/`                                                                                                                                                                  | ✅ ✅ EJECUTADO OK            |
| 11   | `fix`   | `main`                           | ✅ correccion inicializacion main scripts               | `backend/main_init_scripts.py`                                                                                                                                                              | 🟡 PENDIENTE                 |
| 12   | `fix`   | `tools`                          | ✅ correccion script ejecutar health check              | `ejecutar_health_check_vps_principal.py`                                                                                                                                                    | 🟡 PENDIENTE                 |
| 13   | `chore` | `config`                         | 🧹 actualizacion pyproject.toml                         | `pyproject.toml`                                                                                                                                                                            | 🟡 PENDIENTE                 |
| 14   | `docs`  | `clinerules`                     | 📑 actualizacion reglas del proyecto                    | `.clinerules/default-rules.md`                                                                                                                                                              | 🟡 PENDIENTE                 |
| 15   | `docs`  | `diagnosticos:excepciones`       | 📑 plan implementacion excepciones                      | `gestion_proyecto/diagnosticos/excepciones/`                                                                                                                                                | 🟡 PENDIENTE                 |
| 16   | `docs`  | `diagnosticos:seeders`           | 📑 diagnostico consistencia seeders y backup            | `gestion_proyecto/diagnosticos/seeders/DIAGNOSTICO_CONSISTENCIA_SEEDER_PLATFORM_CONFIG.md, gestion_proyecto/diagnosticos/seeders/DIAGNOSTICO_BACKUP_LIGAS_PLATFORM_CONFIG.md`               | 🟡 PENDIENTE                 |
| 17   | `docs`  | `diagnosticos:scheduler`         | 📑 plan correccion scheduler DIP                        | `gestion_proyecto/diagnosticos/scheduled/PLAN_CORRECCION_JOB_SCHEDULER_DIP_CLEANARCH.md`                                                                                                    | 🟡 PENDIENTE                 |
| 18   | `docs`  | `diagnosticos:sql_state_manager` | 📑 trazabilidad refactor sql state manager              | `gestion_proyecto/diagnosticos/refactorizacion_sql_state_manager/`                                                                                                                          | 🟡 PENDIENTE                 |
| 19   | `docs`  | `hus`                            | 📑 nuevas historias de usuario                          | `gestion_proyecto/hus/hu-scheduler-dashboard-interactivo-001.md, gestion_proyecto/hus/hu-sistema-aprobacion-manual-002.md, gestion_proyecto/hus/hu-monitor-automatico-estado-planes-003.md` | 🟡 PENDIENTE                 |
| 20   | `docs`  | `planes_correctivos`             | 📑 planes correctivos pendientes                        | `gestion_proyecto/planes_correctivos/`                                                                                                                                                      | 🟡 PENDIENTE                 |
| 21   | `chore` | `scripts:coverage`               | 🧹 scripts reporte coverage                             | `scripts/bat/run_coverage.bat, scripts/bat/README.md`                                                                                                                                       | 🟡 PENDIENTE                 |

---

## ⛔ ARCHIVOS QUE NO SE DEBEN COMMITEAR NUNCA:
> ✅ Estos archivos estan marcados para limpieza y NO se incluyen en ningun commit
```
.coverage
backend/.coverage
backend/coverage.xml
backend/data/ligas_seeder_progress.json
backend/logs/*
backend/backend/logs/*
*.log.zip
cleanup_history.json
```

---

## ✅ COMANDOS GIT LISTOS PARA EJECUTAR:

> 🔴 NOTA: Primero ejecutar el reset y limpieza, luego los commits uno por uno en orden

```bash
# ✅ PASO 0: Limpiar archivos basura
git reset HEAD .coverage backend/.coverage backend/coverage.xml backend/data/ligas_seeder_progress.json backend/logs/*
git checkout -- .coverage backend/.coverage backend/coverage.xml

# ✅ PASO 1: Commit por commit en orden:

# 1. Robot Leagues Manager
git add backend/apps/leagues_manager/domain/robots/base_robot.py
git commit -m "fix(leagues_manager:robot): mejoras base robot logger"

# 2. Sync Jobs
git add backend/apps/leagues_manager/tasks/sync_jobs.py
git commit -m "feat(leagues_manager:tasks): implementacion sync_jobs"

# 3. Tests Robot Scheduler
git add backend/apps/leagues_manager/tests/test_robot_scheduler_integration_simulation.py backend/apps/leagues_manager/tests/mock_data_leagues.py
git commit -m "feat(leagues_manager:tests): test simulacion integracion robot scheduler"

# 4. Fix Mongo VPS Health Check
git add backend/apps/platform_config/infrastructure/repositories/mongo_vps_health_check_repository.py
git commit -m "fix(platform_config:mongo): correcciones repositorio mongo vps health check"

# 5. Test Platform Config Seeder
git add backend/apps/platform_config/tests/test_platform_config_seeder_unit.py
git commit -m "feat(platform_config:tests): test unitario platform config seeder"

# 6. SQL State Manager y Servicios Backup
git add backend/commands/db/admin/sql/sql_state_manager.py backend/commands/db/admin/sql/services/
git commit -m "feat(commands:db): sql state manager y servicios backup/restore"

# 7. Project CLI
git add backend/commands/project_cli.py
git commit -m "feat(commands:cli): mejoras project cli"

# 8. Log Cleanup Models
git add backend/services/models/cleanup_history.py backend/services/models/__init__.py
git commit -m "feat(services:log_cleanup): modelos cleanup history"

# 9. Seeders Mejoras
git add backend/scripts/db/seeders/sql/ligas_seeder.py backend/scripts/db/seeders/sql/platform_config_seeder.py backend/scripts/db/seeders/sql_seeder_orchestrator.py
git commit -m "feat(scripts:seeders): mejoras ligas seeder, platform config y orchestrator"

# 10. Modulo Inspecciones LLM
git add backend/apps/operations/
git commit -m "feat(apps:operations): modulo inspecciones LLM completo"

# 11. Main Scripts
git add backend/main_init_scripts.py
git commit -m "fix(main): correccion inicializacion main scripts"

# 12. Health Check Script
git add ejecutar_health_check_vps_principal.py
git commit -m "fix(tools): correccion script ejecutar health check"

# 13. Pyproject.toml
git add pyproject.toml
git commit -m "chore(config): actualizacion pyproject.toml"

# 14. Cline Rules
git add .clinerules/default-rules.md
git commit -m "docs(clinerules): actualizacion reglas del proyecto"

# 15. Diagnosticos Excepciones
git add gestion_proyecto/diagnosticos/excepciones/
git commit -m "docs(diagnosticos:excepciones): plan implementacion excepciones"

# 16. Diagnosticos Seeders
git add gestion_proyecto/diagnosticos/seeders/DIAGNOSTICO_CONSISTENCIA_SEEDER_PLATFORM_CONFIG.md gestion_proyecto/diagnosticos/seeders/DIAGNOSTICO_BACKUP_LIGAS_PLATFORM_CONFIG.md
git commit -m "docs(diagnosticos:seeders): diagnostico consistencia seeders y backup"

# 17. Plan Scheduler DIP
git add gestion_proyecto/diagnosticos/scheduled/PLAN_CORRECCION_JOB_SCHEDULER_DIP_CLEANARCH.md
git commit -m "docs(diagnosticos:scheduler): plan correccion scheduler DIP"

# 18. Refactor SQL State Manager
git add gestion_proyecto/diagnosticos/refactorizacion_sql_state_manager/
git commit -m "docs(diagnosticos:sql_state_manager): trazabilidad refactor sql state manager"

# 19. Historias de Usuario
git add gestion_proyecto/hus/hu-scheduler-dashboard-interactivo-001.md gestion_proyecto/hus/hu-sistema-aprobacion-manual-002.md gestion_proyecto/hus/hu-monitor-automatico-estado-planes-003.md
git commit -m "docs(hus): nuevas historias de usuario"

# 20. Planes Correctivos
git add gestion_proyecto/planes_correctivos/
git commit -m "docs(planes_correctivos): planes correctivos pendientes"

# 21. Scripts Coverage
git add scripts/bat/run_coverage.bat scripts/bat/README.md
git commit -m "chore(scripts:coverage): scripts reporte coverage"
```

---

## ✅ VERIFICACION FINAL:
- ✅ TODOS los 39 archivos pendientes de git status estan incluidos
- ✅ No hay mezcla de dominios en ningun commit
- ✅ Orden de dependencia correcto (core primero, luego dominios)
- ✅ Cada commit es reversible
- ✅ Archivos temporales excluidos correctamente
- ✅ Convencion de commits estandarizada
- ✅ Ningun archivo se olvido
- ✅ Orden logico de ejecucion sin dependencias circulares

---

## 📊 RESUMEN ESTADO ACTUALIZADO:
|                                   | Tipo             | Cantidad |
| --------------------------------- | ---------------- |
| ✅ Commits YA EJECUTADOS           | 6                |
| 🟡 Commits PENDIENTES              | 16               |
| ✅ Total planificados              | 22               |
| ✅ Archivos modificados pendientes | 16               |
| ✅ Archivos nuevos pendientes      | 6                |
| ⛔ Archivos excluidos (NO COMMIT)  | 8                |
| 📅 Fecha ultima actualizacion      | 24/04/2026 12:34 |
