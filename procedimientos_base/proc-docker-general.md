
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

```bash
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
