# 🚀 Guía de Inicialización del Proyecto TipsterByte FX

Guía completa para configurar y ejecutar el proyecto desde cero, incluyendo las **2 formas principales de ejecución**.

---

## 📋 Índice

1. [Prerrequisitos](#prerrequisitos)
2. [Formas de Ejecución del Proyecto](#formas-de-ejecución-del-proyecto)
3. [Paso 1: Diagnóstico Inicial](#paso-1-diagnóstico-inicial)
4. [Paso 2: Inicialización de PostgreSQL](#paso-2-inicialización-de-postgresql)
5. [Paso 3: Inicialización de MongoDB](#paso-3-inicialización-de-mongodb)
6. [Paso 4: Verificación Final](#paso-4-verificación-final)
7. [Comandos Adicionales Útiles](#comandos-adicionales-útiles)

---

## Prerrequisitos

### Docker (Bases de Datos)

Asegúrate de que los contenedores de las bases de datos estén en ejecución:

```bash
# Desde la raíz del proyecto (donde está docker-compose.yml)
docker-compose up -d

# Verificar que los contenedores están corriendo
docker-compose ps
```

**Contenedores que se levantan:**
- `db_pg_tipsterbyte_fx` → PostgreSQL en `localhost:5433`
- `db_mongo_tipsterbyte_fx` → MongoDB en `localhost:27017`

### Entorno Virtual Python

```bash
# Desde la carpeta backend/
cd backend

# Crear entorno virtual (si no existe)
python -m venv .venv

# Activar entorno virtual
# Windows PowerShell:
.\.venv\Scripts\activate

# Windows CMD:
.venv\Scripts\activate.bat

# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Formas de Ejecución del Proyecto

El proyecto tiene **2 formas principales de ejecución**:

### 🎯 Forma 1: Ejecución Manual de Tareas (Scripts)

Ejecuta procesos específicos directamente sin necesidad del servidor web.

**Archivo de entrada:** `backend/main_init_scripts.py`

**Uso:**
```bash
cd backend
python main_init_scripts.py --process SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
```

**Procesos disponibles:**
- `SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS` → Orquestador principal de extracción de datos deportivos

**Ideal para:**
- Ejecutar tareas puntuales
- Pruebas y debugging
- Procesos batch sin necesidad del servidor

---

### 🌐 Forma 2: Ejecución a través del Servidor Web (FastAPI)

Inicia el servidor web que expone endpoints REST API y ejecuta el scheduler automático.

**Archivo de entrada:** `backend/main_init_web_server.py`

**Uso:**
```bash
cd backend

# Opción 1: Usando manage.py (recomendado)
python manage.py server run

# Opción 2: Usando uvicorn directamente
uvicorn main_init_web_server:app --host 127.0.0.1 --port 8000 --reload
```

**Endpoints disponibles al iniciar:**
- `http://localhost:8000/docs` → Documentación Swagger
- `http://localhost:8000/redoc` → Documentación ReDoc
- `http://localhost:8000/api/v1/system/health` → Health check

**Ideal para:**
- Desarrollo interactivo
- Acceso vía API REST
- Monitoreo en tiempo real
- Scheduler automático de tareas

---

## Paso 1: Diagnóstico Inicial

Utiliza el comando de estado para verificar la configuración actual:

```bash
cd backend
python manage.py project status
```

**Salida esperada:**
- ✅ Docker: Contenedores PostgreSQL y MongoDB en ejecución
- ✅ PostgreSQL: Base de datos migrada
- ✅ PostgreSQL: Datos iniciales presentes
- ✅ MongoDB: Esquema inicializado
- ✅ MongoDB: Datos iniciales presentes

---

## Paso 2: Inicialización de PostgreSQL (SQL)

### 2.1 Crear la Migración Inicial

```bash
cd backend
python manage.py sql create-migration -m "initial project structure"
```

### 2.2 Aplicar la Migración

```bash
python manage.py sql migrate
```

### 2.3 Poblar la Base de Datos (Seeders)

```bash
python manage.py seed-sql
```

**Seeders disponibles:**
- `PlatformConfigSeeder` → Configuración de procesos y scheduler
- `LeaguesManagerSeeder` → Ligas, torneos, fuentes de extracción

---

## Paso 3: Inicialización de MongoDB (NoSQL)

### 3.1 Inicializar el Esquema

```bash
cd backend
python manage.py nosql init-schema
```

### 3.2 (Opcional) Poblar la Base de Datos

```bash
python manage.py nosql seed
```

---

## Paso 4: Verificación Final

### 4.1 Verificar Estado del Proyecto

```bash
cd backend
python manage.py project status
```

**Salida esperada:**
```
🎉 ¡El proyecto está completamente configurado y listo!
Inicia el servidor con `python manage.py server run`
```

### 4.2 Iniciar el Proyecto

**Opción A: Servidor Web (Desarrollo interactivo)**
```bash
python manage.py server run
```

**Opción B: Ejecutar Tarea Manual (Proceso batch)**
```bash
python main_init_scripts.py --process SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
```

Aquí tienes los comandos para ejecutar cada proceso y todos juntos:

---

## 📋 Comandos de Ejecución de Procesos

### Ejecutar TODOS los procesos (Orquestador General)

```bash
cd backend
python main_init_scripts.py --process SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
```

__Descripción:__ Ejecuta el orquestador general que procesa TODOS los trabajos (Standings + Odds + Calendar).
cd backend
python main_init_scripts.py --process PROCESS_STANDINGS_EXTRACTION

cd backend
python main_init_scripts.py --process PROCESS_ODDS_WPLAY_EXTRACTION

cd backend
python main_init_scripts.py --process PROCESS_CALENDAR_EXTRACTION

📊 Resumen de Procesos Disponibles
Código del Proceso	Descripción	Ejecuta
SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS	Orquestador General	TODOS los trabajos
PROCESS_STANDINGS_EXTRACTION	Extracción de Standings	Solo Standings
PROCESS_ODDS_WPLAY_EXTRACTION	Extracción de Odds WPlay	Solo Odds
PROCESS_CALENDAR_EXTRACTION	Extracción de Calendarios	Solo Calendar
🔄 Ejecución Automática (Scheduler)
El scheduler ejecuta automáticamente el orquestador general según la configuración en scheduler_process_config:

Proceso: SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS
Cron: * * * * * (cada minuto)
Estado: Habilitado (enabled = true)

## 📝 Notas Importantes

1. __El orquestador general__ (`SCHEDULER_PROCESS_EXTRACT_DATA_FUENTES_DEPORTIVAS`) ejecuta TODOS los trabajos sin filtrar por `process_id`.

2. __Los procesos específicos__ ejecutan solo los trabajos cuyo `process_id` coincida con el proceso seleccionado.

3. __Cada ejecución__ crea un `ProcessRun` independiente con su propio `run_id` único.

4. __No hay conflictos__ entre ejecuciones manuales y el scheduler, ya que cada una tiene su propio registro.

---

## Comandos Adicionales Útiles

### Gestión de Base de Datos SQL

```bash
# Ver estado de migraciones
python manage.py sql state status

# Crear backup
python manage.py sql state backup

# Restaurar backup
python manage.py sql state restore

# Resetear base de datos (peligroso)
python manage.py sql state reset --hard
```

### Gestión de Base de Datos NoSQL

```bash
# Ver estado
python manage.py nosql state status

# Crear backup
python manage.py nosql state backup

# Limpiar documentos
python manage.py nosql state clear
```

### Gestión de Secretos

```bash
# Generar clave Fernet
python manage.py secrets generate

# Verificar estado
python manage.py secrets show

# Cifrar valor
python manage.py secrets encrypt "mi_valor_secreto"

# Descifrar token
python manage.py secrets decrypt "gAAAAA..."
```

### Scheduler y Procesos

```bash
# Ver procesos programados
python manage.py scheduler status

# Pausar todos los jobs
python manage.py scheduler pause-all

# Reanudar todos los jobs
python manage.py scheduler resume-all
```

---

## 🧹 Refrescar Cache del Proyecto

El menú `python manage.py project status` incluye una opción para limpiar la cache de Python:

```bash
cd backend
python manage.py project status
# Seleccionar opción 3: 🧹 Refrescar Cache (limpiar __pycache__)
```

**¿Qué hace?**
- Busca todos los directorios `__pycache__` en el proyecto
- Pide confirmación antes de eliminarlos
- Elimina los archivos `.pyc` compilados

**¿Cuándo usarlo?**
- Después de actualizar dependencias
- Cuando hay errores extraños de importación
- Después de cambiar entre ramas de Git
- Para liberar espacio en disco

---

## 📚 Referencias Rápidas

| Comando                                        | Descripción                      |
| ---------------------------------------------- | -------------------------------- |
| `python manage.py project status`              | Ver estado completo del proyecto |
| `python manage.py server run`                  | Iniciar servidor web             |
| `python main_init_scripts.py --process <CODE>` | Ejecutar tarea manual            |
| `python manage.py seed-sql`                    | Ejecutar seeders SQL             |
| `python manage.py nosql init-schema`           | Inicializar MongoDB              |
| `docker-compose up -d`                         | Levantar bases de datos          |
| Opción 3 en `project status`                   | Refrescar cache (__pycache__)    |

---

## 🔧 Solución de Problemas

### Error: "No se encontró el proceso"
Verifica que el código del proceso esté en `AVAILABLE_PROCESSES` en `main_init_scripts.py`.

### Error: "No se pudo conectar a la base de datos"
Verifica que Docker esté corriendo: `docker-compose ps`

### Error: "Tablas no encontradas"
Ejecuta las migraciones: `python manage.py sql migrate`

### Error: "Clave Fernet no encontrada"
Genera la clave: `python manage.py secrets generate`

---

**Última actualización:** 2026-03-20