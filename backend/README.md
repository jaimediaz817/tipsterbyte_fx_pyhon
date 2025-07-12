# START

## Configuración inicial

Crear entorno virtual:
python -m venv venv

## Activar entorno virtual

En PowerShell o CMD:

bash linux:
.\venv\Scripts\activate
En Git Bash (o WSL):

bash windows
source venv/Scripts/activate
source ./venv/Scripts/activate
backend

## Desactivar el entorno virtual

desactivate
rm -rf env

## Verificar que el entorno virtual esté activo

where python

## desactivar el entorno virtual

deactivate

## DDOCKER

docker-compose up -d
Esto te levanta:

PostgreSQL en localhost:5432
MongoDB en localhost:27017

docker-compose up -d postgres_tipsterbyte

## ORM

pip install sqlalchemy[asyncio] asyncpg alembic
pip install motor

- Inicializar Alembic:
alembic init alembic

- Logger
pip install loguru
pip install cryptography
pip install pydantic-settings

python -c "from app.core.secrets import generate_key; generate_key()"

## MIGRACIONES

- Crear migración
alembic revision --autogenerate -m "initial auth tables"

- Aplicar migración
alembic upgrade head

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
