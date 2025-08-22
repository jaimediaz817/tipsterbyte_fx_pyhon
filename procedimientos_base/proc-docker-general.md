
# Docker General Procedures

## FEATURES: BACKUPS

backend/
└── backups/
    ├── postgresql_backups/
    │   └── backup_postgres_...
    └── mongo_backups/
        └── backup_mongo_...

## Finalmente, para que los cambios en docker-compose.yml surtan efecto, debes reiniciar tus contenedores

- [INIT]: TENER EN CUENTA ESTAR UBICADOS EN: `RAÍZ DEL PROYECTO/docker-compose.yml`
Detén los servicios:


Verifica la consistencia: Asegúrate una última vez de que el usuario y la contraseña en tu docker-compose.yml y en la MONGO_URI de tu archivo .env son idénticos.
Detén y elimina todo (incluido el volumen): En la terminal, desde la carpeta raíz del proyecto (donde está docker-compose.yml), ejecuta el siguiente comando:
```bash
docker-compose down -v
docker-compose down

Vuelve a levantarlos:
```bash
docker-compose up -d

- COMO DEBE QUEDAR EL DOCKER-COMPOSE.YML

```yaml
services:
  postgres_tipsterbyte:
    image: postgres:13-alpine
    restart: always
    container_name: db_pg_tipsterbyte_fx
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5433:5432"
    volumes:
      - postgresdata:/var/lib/postgresql/data
      # --- CAMBIO CLAVE: Apuntamos a la nueva subcarpeta de backups de SQL ---
      - ./backend/backups/postgresql_backups:/backups
    networks:
      - tipsterbyte_net

  mongo_tipsterbyte:
    image: mongo:4.4
    restart: always
    container_name: db_mongo_tipsterbyte_fx
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
      # --- CAMBIO CLAVE: Apuntamos a la nueva subcarpeta de backups de Mongo ---
      - ./backend/backups/mongo_backups:/backups
    networks:
      - tipsterbyte_net

volumes:
  postgresdata:
  mongodata:

networks:
  tipsterbyte_net:
    driver: bridge
```

## Borrar carpetas:

- con powershell
 Remove-Item -Recurse -Force -Path .\venv
- con gitbash
rm -rf venv


## Tumbar/detener el servicio de mongodb en el sistema operativo (NO DOCKER)

PASO 1: detenemos el contenedor
docker-compose down

PASOS:DETENER_SERVICIO
PASO 2: Seguir estos pasos:
- Presiona Win + R, escribe services.msc y presiona Enter.
- En la ventana de Servicios, busca en la lista un servicio llamado MongoDB Server (el nombre puede variar ligeramente).
- Haz clic derecho sobre él y selecciona "Detener".
- Una vez detenido, haz clic derecho de nuevo, selecciona "Propiedades".- En "Tipo de inicio", cámbialo de "Automático" a "Manual" o "Deshabilitado". Esto evitará que se inicie de nuevo cuando reinicies tu PC.
Haz clic en "Aceptar".

- La Solución Definitiva: Desactivar los Alias de Microsoft
- La solución es decirle a Windows que deje de usar esos atajos molestos. No los borres, simplemente desactívalos desde la configuración de Windows.

Sigue estos pasos exactos:

Abre el Menú Inicio de Windows.

Escribe la frase: Administrar alias de ejecución de aplicaciones y presiona Enter. (En inglés, es "Manage app execution aliases").

Se abrirá una ventana de configuración. Verás una lista de aplicaciones. Busca las dos entradas para Python:

Instalador de aplicación (python.exe)
Instalador de aplicación (python3.exe)
Desactiva los dos interruptores que están a la derecha de python.exe y python3.exe.