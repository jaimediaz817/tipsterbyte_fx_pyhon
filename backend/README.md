# START

## Configuración inicial

Crear entorno virtual:
python -m venv venv

## Eliminar carpeta y contenido

rm -rf .venv

## Activar entorno virtual

En PowerShell o CMD:

**En PowerShell o CMD de Windows:**

```powershell
.\venv\Scripts\activate
```

bash linux:
.\venv\Scripts\activate
En Git Bash (o WSL):

**En Git Bash o WSL (terminales tipo Linux en Windows):**

```bash
source venv/Scripts/activate
source .venv/Scripts/activate
```

source venv/Scripts/activate
source ./venv/Scripts/activate
source .venv/Scripts/activate
backend

## Desactivar el entorno virtual

Para desactivar el entorno virtual en la terminal actual, ejecuta:

```bash
deactivate
```

Esto solo desactiva el entorno virtual para la sesión actual de la terminal; no elimina ningún archivo ni afecta el entorno virtual en disco. Si cierras la terminal o abres una nueva, el entorno virtual ya no estará activo hasta que lo actives de nuevo.

> **Nota:**  
> El comando `rm -rf env` (o similar) elimina completamente la carpeta del entorno virtual y todo su contenido. Esto borra el entorno virtual del proyecto, por lo que tendrías que crearlo e instalar las dependencias nuevamente si lo necesitas más adelante.

## Verificar que el entorno virtual esté activo

where python

## Verificar si el archivo .env existe

python -c "from pathlib import Path; print('✅' if Path('.env').exists() else '❌', Path('.env').resolve())"

## desactivar el entorno virtual

deactivate

## DOCKER

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

## Estado de la Base de Datos (Backups, Restore, Reset)

- **Crear un backup de la base de datos:**

  ```bash
  python manage.py db state backup
  ```

- **Restaurar desde el último backup:**

  ```bash
  python manage.py db state restore
  ```

- **Restaurar desde un archivo específico:**

  ```bash
  python manage.py db state restore --file backups/nombre_del_archivo.sql
  ```

- **Resetear la BD (MODO PELIGROSO - Borra y recrea la BD vacía):**

  ```bash
  python manage.py db state reset --hard
  ```

- **Resetear la BD (MODO SEGURO - Preserva los datos mediante backup/restore):**

  ```bash
  python manage.py db state reset --with-backup
  ```


## mongo

## Para inicializar la base de datos NoSQL (MongoDB) y cargar los modelos

- Con tu entorno virtual activo, ejecuta:

```bash
python backend/scripts/db/seeders/seed_access_log.py