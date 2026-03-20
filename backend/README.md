# START

## Configuración Inicial del Entorno

Sigue estos pasos **desde la carpeta `backend`**.

1.  **Crear el entorno virtual:**
    *   Asegúrate de estar en la carpeta `backend`. El siguiente comando creará una carpeta `.venv` dentro de `backend`.

    ```bash
    # Reemplaza la ruta si tu instalación de Python está en otro lugar
    "C:\Users\jdiaz\AppData\Local\Python\Python311\python.exe" -m venv .venv
    ```

2.  **Activar el entorno virtual:**

    *   **En PowerShell o CMD de Windows:**
        ```powershell
        .\.venv\Scripts\activate
        ```

    *   **En Git Bash o WSL (terminales tipo Linux):**
        ```bash
        source .venv/Scripts/activate
        ```
    *Una vez activo, tu terminal debería mostrar `(.venv)` al principio de la línea.*

3.  **Instalar las dependencias del proyecto:**
    ```bash
    pip install -r requirements.txt
    ```

---



### (n). Verificar Estado y Seguir Instrucciones

Este proyecto incluye un comando inteligente que te guía en cada paso. **Úsalo después de completar cada acción para saber qué hacer a continuación.**

```bash
python manage.py project status
```

### Flujo de Comandos Guiado

El comando `project status` te pedirá que ejecutes lo siguiente, en este orden:

1.  **Levantar las Bases de Datos (si no están activas):**
    *   *El comando te lo indicará si es necesario.*
    ```bash
    # Desde la raíz del proyecto (fuera de 'backend/')
    docker-compose up -d
    ```

2.  **Crear las Tablas en PostgreSQL (si no existen):**
    *   *El comando te lo indicará si es necesario.*
    ```bash
    # Desde la carpeta 'backend/'
    python manage.py sql migrate
    ```

3.  **Poblar la Base de Datos SQL con datos iniciales:**
    *   *El comando te lo indicará si es necesario.*
    ```bash
    # Desde la carpeta 'backend/'
    python manage.py seed-sql
    ```

4.  **Inicializar el Esquema de MongoDB:**
    *   *El comando te lo indicará si es necesario.*
    ```bash
    # Desde la carpeta 'backend/'
    python manage.py nosql init-schema
    ```

### 3. Iniciar el Servidor

Una vez que `python manage.py project status` te confirme que todo está listo, puedes iniciar el servidor de desarrollo:

```bash
python manage.py server run
```

## Ejecutar migraciones mediante el asistente:
```bash
python manage.py project status
```
- seleccionar opción #1, luego ejecutar los seeders sql


## Desactivar el entorno virtual

Para salir del entorno virtual en la terminal actual, simplemente ejecuta:
```bash
deactivate
```

## Eliminar el entorno virtual (si es necesario)

Si necesitas empezar de cero, puedes eliminar la carpeta del entorno. **Asegúrate de que el entorno esté desactivado primero.**
```bash
# Desde la carpeta 'backend'
rm -rf .venv
```




Esto solo desactiva el entorno virtual para la sesión actual de la terminal; no elimina ningún archivo ni afecta el entorno virtual en disco. Si cierras la terminal o abres una nueva, el entorno virtual ya no estará activo hasta que lo actives de nuevo.

> **Nota:**  
> El comando `rm -rf env` (o similar) elimina completamente la carpeta del entorno virtual y todo su contenido. Esto borra el entorno virtual del proyecto, por lo que tendrías que crearlo e instalar las dependencias nuevamente si lo necesitas más adelante.

## Verificar que el entorno virtual esté activo

where python

## Verificar si el archivo .env existe

python -c "from pathlib import Path; print('✅' if Path('.env').exists() else '❌', Path('.env').resolve())"

## Verificar servicios/puertos inciados en el sistema operativo en cuestión



## Ejecutar manualmente procesos - tareas - tasks
- Nos ubicamos en la raíz de backend del proyecto y ejecutamos el comando:
```bash
python main_init_scripts.py --process scheduler_proceso_rastreo_data_fuentes_deportivas
```

## Instalar dependencias requirements
```bash
pip install -r requirements.txt
```




##  Formatting and Linting

This project uses **Black** to ensure a consistent code style.

### Configuration

1.  **Install the VS Code Extension**: Search for and install the `ms-python.black-formatter` extension from the Marketplace.
2.  **Install Black**: Make sure your virtual environment is activated and run `pip install black`.
3.  **Enable Format on Save**: VS Code is configured via `.vscode/settings.json` to automatically format Python files on save using Black.

Code style rules, like line length, are defined in the `pyproject.toml` file at the root of the project.








## DOCKER

- NOTE: Procedimiento urgente: determinar status de servicio de mongo: PASOS:
[Detener servicio de MongoDB (Windows)](/procedimientos_base/proc-docker-general.md#detener-servicio-mongodb-windows)

docker-compose up -d
Esto te levanta:

PostgreSQL en localhost:5432
MongoDB en localhost:27017

docker-compose up -d postgres_tipsterbyte
docker-compose up -d mongo_tipsterbyte

## ORM

pip install sqlalchemy[asyncio] asyncpg alembic
pip install motor

- Inicializar Alembic:
alembic init alembic

- Logger
pip install loguru
pip install cryptography
pip install pydantic-settings

python -c "from core.secrets import generate_key; generate_key()"

## MIGRACIONES

- Crear migración
alembic revision --autogenerate -m "initial auth tables"

- Aplicar migración
Escaneo completado. Se cargaron 0 modelos SQL.Escaneo completado. Se cargaron 0 modelos SQL.

- Luego de activar el entorno virtual, instalar las dependencias:
pip install -r requirements.txt

- Si no funciona lo anterior aún habiendo hecho lo anterior para env:
Abre la Paleta de Comandos (Ctrl+Shift+P).
Busca y selecciona: Python: Restart Language Server, por lo general se navega hacia
la carpeta env/Scripts/ y se selecciona el ejecutable de Python (python.exe).

## Db comandos

alembic upgrade head

## FLAKE

pip install flake8

## ----------------------------------------------------

## MONGO

pip install beanie motor pydantic

## API

- Detener el servidor si está corriendo:

taskkill /F /IM python.exe
netstat -ano | findstr :8010

## ---------------------------------------------------

SCRIPTS

backend/
├── alembic/
├── apps/
├── core/
├── scripts/
│   ├── __init__.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── reset_database.py  <-- Para borrar y recrear todo (¡peligroso!)
│   │   ├── backup_database.py <-- Para hacer copias de seguridad
│   │   └── restore_database.py <-- Para restaurar desde una copia
│   └── seed_database.py       <-- El seeder que ya creamos
└── venv/

backend/
├── alembic/
├── apps/
├── core/
├── scripts/          <-- NUEVA CARPETA
│   ├── db/           <-- NUEVA CARPETA
│   └── ...
└── venv/

pip install "typer[all]" psycopg2-binary










## Gestión del Proyecto (manage.py)

Este proyecto utiliza un script de gestión centralizado, `manage.py`, para todas las tareas de desarrollo y mantenimiento. Asegúrate de tener tu entorno virtual activado antes de ejecutar cualquier comando.

## Ayuda

- Para ver una lista completa de comandos y subcomandos disponibles

```bash
python manage.py --help
python manage.py sql --help
python manage.py sql state --help
python manage.py nosql --help
python manage.py nosql state --help
```

## Servidor Web

- Para iniciar el servidor de desarrollo con recarga automática:

```bash
python manage.py server run
```

## Migraciones de Base de Datos (Alembic)

- **Crear un nuevo archivo de migración después de cambiar un modelo:**

  ```bash
  python manage.py db create-migration "Tu mensaje descriptivo"
  ```

- **Aplicar todas las migraciones pendientes a la base de datos:**

  ```bash
  python manage.py db migrate
  ```

## COMANDOS CLI PERSONALIZADOS: Estado de la Base de Datos (Backups, Restore, Reset)

# ... (cualquier contenido anterior que desees conservar) ...

## 🚀 Gestión del Proyecto (`manage.py`)

Este proyecto utiliza un script de gestión centralizado, `manage.py`, para todas las tareas de desarrollo y mantenimiento. Asegúrate de tener tu entorno virtual activado (`source venv/Scripts/activate`) antes de ejecutar cualquier comando.

### 💡 Ayuda General

Para obtener una lista completa de los grupos de comandos y sus descripciones, ejecuta:

```bash
python manage.py --help
```

Esto te mostrará los grupos principales: `sql`, `nosql`, y `server`.

---

### 🏁 Flujo de Trabajo para Configuración Inicial

Sigue estos pasos en orden para levantar el proyecto desde cero:

1.  **Levantar Contenedores de Docker:** Inicia las bases de datos.
    ```bash
    # Desde la raíz del proyecto (fuera de 'backend/')
    docker-compose up -d
    ```

════════════════════════════════ ✦ ════════════════════════════════

## Comandos personalizados

-  **Aplicar Migraciones SQL:** Crea la estructura de tablas en PostgreSQL.
    ```bash
    # Desde la carpeta 'backend/'
    python manage.py sql migrate
    ```

#### 💿 Poblado de Datos (Seeders)

Para insertar los datos iniciales en las bases de datos (roles, usuarios administradores, configuraciones por defecto, etc.), utiliza los siguientes comandos.

-   **Poblar la Base de Datos SQL:**
    *Este comando ejecuta los "seeders" ubicados en `scripts/db/seeders/sql/`.*

    ```bash
    # Ejecutar TODOS los seeders SQL en modo seguro (solo crea si no existe)
    python manage.py seed-sql

    # Ejecutar un seeder específico por su nombre de clase
    python manage.py seed-sql AuthSeeder

    # Ejecutar un seeder específico y FORZAR la actualización de registros existentes
    python manage.py seed-sql AuthSeeder --update
    ```

-   **Poblar la Base de Datos NoSQL (MongoDB):**
    *(Nota: La funcionalidad de actualización y especificidad aún no se ha implementado para NoSQL en este ejemplo, pero se podría seguir el mismo patrón).*

    ```bash
    # Ejecutar todos los seeders de MongoDB
    python manage.py seed-nosql
    ```
---

### 🗃️ Gestión de PostgreSQL (`sql`)

Comandos para administrar la base de datos relacional. Para ver todas las opciones, ejecuta `python manage.py sql --help`.

#### Migraciones (Alembic)

-   **Crear un nuevo archivo de migración** (después de cambiar un modelo de SQLAlchemy):
    ```bash
    python manage.py sql create-migration "Tu mensaje descriptivo aquí"
    ```
-   **Creqar un archivo de migración sin mensaje** (se generará uno automático):
    ```bash
    python manage.py sql create-migration
    ```
-   **Aplicar todas las migraciones pendientes** a la base de datos:
    ```bash
    python manage.py sql migrate
    ```

#### Gestión de Estado (`sql state`)

Para ver todas las opciones de estado, ejecuta `python manage.py sql state --help`.

-   **Crear un backup:**
    *Se guardará en `backend/backups/postgresql_backups/`*
    ```bash
    python manage.py sql state backup
    ```
-   **Restaurar desde el último backup disponible:**
    ```bash
    python manage.py sql state restore
    ```
-   **Restaurar desde un archivo específico:**
    ```bash
    python manage.py sql state restore --file backups/postgresql_backups/nombre_del_archivo.sql
    ```
-   **Resetear la BD (MODO SEGURO):** Preserva los datos haciendo un backup y restaurándolo después de recrear la BD.
    ```bash
    python manage.py sql state reset --with-backup
    ```
-   **Resetear la BD (MODO DESTRUCTIVO):** Borra la BD, la recrea y aplica migraciones. **TODOS LOS DATOS SE PIERDEN.**
    ```bash
    python manage.py sql state reset --hard
    ```

---

### 🍃 Gestión de MongoDB (`nosql`)

Comandos para administrar la base de datos NoSQL. Para ver todas las opciones, ejecuta `python manage.py nosql --help`.

#### Gestión de Estado (`nosql state`)

Para ver todas las opciones de estado, ejecuta `python manage.py nosql state --help`.

-   **Crear un backup:**
    *Se guardará en `backend/backups/mongo_backups/`*
    ```bash
    python manage.py nosql state backup
    ```
-   **Restaurar desde el último backup disponible:**
    ```bash
    python manage.py nosql state restore
    ```
-   **Restaurar desde un archivo específico:**
    ```bash
    python manage.py nosql state restore --file backups/mongo_backups/nombre_del_archivo.gz
    ```
-   **Resetear la BD (MODO DESTRUCTIVO):** Borra (drop) la base de datos completa. **TODOS LOS DATOS SE PIERDEN.**
    ```bash
    python manage.py nosql state reset
    ```
-   **Limpiar la BD (MODO NO DESTRUCTIVO):** Borra todos los documentos de todas las colecciones, pero mantiene la estructura de la base de datos (colecciones e índices).
    ```bash
    python manage.py nosql state clear
    ```

-   **Limpiar la BD (MODO NO DESTRUCTIVO):** Borra todas las tablas de la base de datos, pero mantiene la base de datos en sí. Ideal para limpiar antes de volver a migrar.
    ```bash
    python manage.py sql clear-all-tables
    ```
-   **Aplicar migraciones de MongoDB:** Ejecuta las migraciones pendientes en la base de datos NoSQL.
    ```bash
    python manage.py nosql-migrate run      
    ```

---

---

### 🔐 Gestión de Claves y Cifrado (`secrets`)

Este grupo de comandos te permite gestionar la clave de cifrado Fernet del proyecto. Para ver todas las opciones, ejecuta `python manage.py secrets --help`.

-   **Generar una nueva clave de cifrado:**
    *Si la clave ya existe, no la sobrescribirá por seguridad.*
    ```bash
    python manage.py secrets generate
    ```

-   **Rotar la clave (forzar sobreescritura):**
    *¡CUIDADO! Esto invalidará todos los datos cifrados con la clave anterior.*
    ```bash
    python manage.py secrets generate --force
    ```

-   **Verificar el estado de la clave:**
    *No muestra la clave, solo confirma si existe y dónde.*
    ```bash
    python manage.py secrets show
    ```

-   **Cifrar un valor:**
    ```bash
    python manage.py secrets encrypt "mi_valor_secreto"
    ```

-   **Descifrar un token:**
    ```bash
    python manage.py secrets decrypt "gAAAAABomoCzdDjXZpN05XrYd7u-v3DvprLyEjX0zjIhXOtfZB9zfpVKa4IlixZ6VRiSCQRS-DFyErhvPIaC1Nsa8aYoMmIVGWIWyzeDTeqFsA1CfOr5jVE="
    ```

> **Nota:** El sistema priorizará la variable de entorno `FERNET_KEY` si está definida. De lo contrario, usará el archivo `.fernet.key` ubicado (por defecto) en la carpeta `core/`.

### 🌐 Gestión del Servidor Web (`server`)

-   **Iniciar el servidor de desarrollo** con recarga automática:
    ```bash
    python manage.py server run


#LINK - 
pip install coverage

1. Ejecutar Pruebas con Cobertura
Para ejecutar tus pruebas de pytest y recolectar datos de cobertura, usa el siguiente comando. Es crucial especificar la ruta de los módulos que quieres cubrir (ej. apps/, shared/, core/) para obtener un reporte preciso.

# Desde la carpeta 'backend/'
coverage run -m pytest

2. Generar Reporte en la Terminal
Una vez que hayas ejecutado las pruebas con coverage run, puedes ver un resumen de la cobertura directamente en tu terminal:

# Desde la carpeta 'backend/'
coverage report -m

3. Generar Reporte HTML Detallado
Para una visualización interactiva y detallada de la cobertura (ideal para identificar exactamente qué líneas de código no están cubiertas), genera un reporte HTML:
# Desde la carpeta 'backend/'
coverage html

4. Ver el Reporte HTML
Para abrir el reporte HTML en tu navegador web:

Desde VS Code: Haz clic derecho en la carpeta htmlcov/ en el explorador de archivos y selecciona "Reveal in File Explorer" (Windows) o "Open in Integrated Terminal" y luego navega a la carpeta. Una vez allí, busca el archivo index.html y ábrelo con tu navegador.

Desde la Terminal (Windows PowerShell/CMD):
# Después de generar el reporte HTML, navega a la carpeta 'backend/'
start htmlcov\index.html