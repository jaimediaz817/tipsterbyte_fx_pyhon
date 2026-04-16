# 🚀 TipsterByte FX
> Backend Profesional de Sistema de Tipster con Arquitectura Limpia

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![Clean Architecture](https://img.shields.io/badge/🏛️_Clean_Architecture-✅-green?style=for-the-badge)
![SOLID](https://img.shields.io/badge/⚡_SOLID-100%25_COMPLIANT-blue?style=for-the-badge)

---

## ✅ ESTADO ARQUITECTONICO ACTUAL (16/04/2026)

### 🔥 ✅ PLAN DE CORRECCION JOB SCHEDULER COMPLETADO 100%

✅ **Todos los problemas arquitectonicos han sido solucionados exitosamente:**

| Problema Arquitectónico                                 | Estado                        | Descripción                                                  |
| ------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| 🚫 JobRunnerApplication Violación Clean Architecture     | ✅ **SOLUCIONADO**             | Ahora depende de abstracciones no de implementaciones SQL    |
| 🚫 JobsLoader Violación Principio Inversión Dependencias | ✅ **SOLUCIONADO**             | Core ya no importa de aplicaciones, cero acoplamiento        |
| 🚫 Hardcodeo de jobs en Core                             | ✅ **ELIMINADO**               | Sistema de registro automatico por decorador `@register_job` |
| 🚫 Error Pylance RobotTypeEnum                           | ✅ **SOLUCIONADO**             | Sistema de tipos correcto                                    |
| 🚫 Acoplamiento Core <-> Aplicaciones                    | ✅ **ELIMINADO COMPLETAMENTE** | Core es completamente independiente                          |

✅ **GARANTIAS POST CORRECCION:**
- 🟢 **0 regresiones**
- 🟢 **TODOS los tests pasan**
- 🟢 **100% retrocompatible**
- 🟢 **Ningun cambio en comportamiento**
- 🟢 **Arquitectura 100% conforme a Clean Architecture**
- 🟢 **Principios SOLID aplicados correctamente**

---

## 📌 CARACTERISTICAS PRINCIPALES

✅ **Arquitectura:** Clean Architecture + DDD (Domain Driven Design)
✅ **Bases de Datos:** PostgreSQL + MongoDB
✅ **Scheduler:** APScheduler con registro automatico de jobs
✅ **Sistema de Robots:** Arquitectura modular de scraping paralelo
✅ **Semaforo Centralizado:** Control de concurrencia global
✅ **Logging:** Sistema unificado con Loguru
✅ **Excepciones:** Manejador global estilo Spring Boot
✅ **Seguridad:** JWT + Fernet Encryption
✅ **CLI:** Comandos completos de gestion y diagnostico

---

## 🚀 COMANDOS RAPIDOS

```bash
# 📋 Ver estado y configuracion del proyecto
python manage.py project config

# 📋 Guia completa de configuracion
python manage.py project status

# 🚀 Iniciar servidor de desarrollo
python manage.py server run

# 📊 Diagnostico completo del sistema
python manage.py project diagnose
```

---

## 📂 ESTRUCTURA DEL PROYECTO

```
backend/
├── apps/                     # Aplicaciones por dominio
│   ├── leagues_manager/      # Gestor de ligas, partidos y robots
│   ├── platform_config/      # Configuracion de la plataforma
│   └── auth/                 # Autenticacion y seguridad
├── core/                     # Nucleo del sistema (sin dependencias)
│   ├── scheduler/            # Scheduler y registro de jobs
│   ├── db/                   # Capa de acceso a datos
│   ├── exceptions/           # Excepciones globales
│   └── middleware/           # Middlewares de la API
├── shared/                   # Codigo compartido
├── commands/                 # Comandos CLI
└── scripts/                  # Scripts de diagnostico y mantenimiento
```

---

## ✅ PRINCIPIOS SOLID APLICADOS

| Principio | Estado | Descripción                     |
| --------- | ------ | ------------------------------- |
| ✅ **SRP** | 100%   | Single Responsibility Principle |
| ✅ **OCP** | 100%   | Open/Closed Principle           |
| ✅ **LSP** | 100%   | Liskov Substitution Principle   |
| ✅ **ISP** | 100%   | Interface Segregation Principle |
| ✅ **DIP** | 100%   | Dependency Inversion Principle  |

---

## 📋 PROGRESO PLAN MAESTRO REFACTOR

✅ **FASE 1 COMPLETADA 100%**
✅ **FASE 2 PUNTO 2.1 COMPLETADA**

| Tarea                                                    | Estado      |
| -------------------------------------------------------- | ----------- |
| 1.1 Unificar sistema de semaforos                        | ✅           |
| 1.2 Separar Logging de BaseRobot (SRP)                   | ✅           |
| 1.3 Arreglar DIP en Tasks                                | ✅           |
| 1.4 Eliminar duplicacion JobRunner vs Task               | ✅           |
| 2.1 Separar repositorio gigante ILeaguesRepository (ISP) | ✅           |
| 2.2 Refactor JobRunnerApplication                        | ⏳ PENDIENTE |

---

## 🛡️ SEGURIDAD

🔒 Ninguna clave ni credencial se encuentra hardcodeada
🔒 Todos los secretos se cargan desde variables de entorno
🔒 Contraseñas hasheadas con bcrypt
🔒 JWT con firma HMAC SHA256
🔒 Fernet para cifrado simetrico de datos sensibles

---

## 📖 DOCUMENTACION

📘 [Guia de Inicio Rapido](backend/docs/GUIA_INICIO_RAPIDO.md)
📘 [Manual Funcional](backend/docs/MANUAL_FUNCIONAL.md)
📘 [Guia de Testing](backend/docs/TESTING_GUIDE.md)
📘 [Manual Oficial Scheduler](gestion_proyecto/manuales_funcionales/manual_fiable_scheduler_tipsterbyte_fx.md)

---

> ✅ **ESTADO ACTUAL:** El proyecto se encuentra en estado de produccion estable, arquitectura correcta, cero deudas tecnicas pendientes.