# Procedimiento de Migración Docker - Configuración Nueva

## RESUMEN
Procedimiento para migrar de la configuración Docker anterior a la nueva configuración con perfiles (dev/prod).

**Fecha:** 23/03/2026  
**Estado:** Configuración actualizada con perfiles dev/prod

---

## FASE 1: LIMPIEZA DE CONFIGURACIÓN ANTERIOR

### CASO ESPECIAL: Usar docker-compose ANTIGUO para down -v

**PROBLEMA:** El docker-compose nuevo usa `${MONGO_USER}` y `${MONGO_PASSWORD}` que se expanden desde el `.env` de la raíz, pero ese archivo no tiene esas variables.

**SOLUCIÓN:** Usar el docker-compose ANTIGUO (que apunta a `./backend/.env`) para hacer el down -v:

```bash
# 1. Detener y eliminar contenedores antiguos + volúmenes
# CUIDADO: esto borra datos de las BD
# USA EL DOCKER-COMPOSE ANTIGUO para este paso
docker-compose down -v

# 2. Verificar que no quedan contenedores corriendo
docker ps -a

# 3. (OPCIONAL) Eliminar imágenes antiguas si las tienes
docker images | grep postgres
docker images | grep mongo
# Si ves imágenes viejas (postgres:13-alpine, mongo:4.4), elimínalas:
docker rmi postgres:13-alpine mongo:4.4
```

**NOTA:** Después de este paso, puedes usar el docker-compose nuevo con perfiles para levantar los servicios.

---

## FASE 2: CONFIGURACIÓN DE ARCHIVOS .ENV

### IMPORTANTE: Entender cómo funcionan los .env

| Escenario         | Archivo que lee     | Quién lo usa                  |
| ----------------- | ------------------- | ----------------------------- |
| App local (tu PC) | `backend/.env`      | Python directamente           |
| Docker Dev        | `backend/.env.dev`  | docker-compose --profile dev  |
| Docker Prod       | `backend/.env.prod` | docker-compose --profile prod |

**El sistema (backend/core/config.py) SOLO lee `backend/.env` cuando corres la app localmente.**

### PASO CRÍTICO: Copiar variables de .env.dev a .env

```bash
# 6. Copiar contenido de .env.dev a .env para uso local
# OPCIÓN A: Copiar archivo completo (reemplaza .env existente)
cp backend/.env.dev backend/.env

# OPCIÓN B: Copiar manualmente solo las variables necesarias
# Abre ambos archivos y copia las variables que falten
cat backend/.env.dev
cat backend/.env
```

**Variables que DEBEN existir en backend/.env:**
- ENV=development
- DEBUG=True
- POSTGRES_USER=postgres
- POSTGRES_PASSWORD=postgres
- POSTGRES_DB=tipsterbyte_fx_db
- POSTGRES_HOST=localhost
- POSTGRES_PORT=5433
- DATABASE_URL=postgresql://...
- MONGO_USER=tipster_admin
- MONGO_PASSWORD=tipster_mongo_pass
- MONGO_HOST=localhost
- MONGO_PORT=27017
- MONGO_DB=tipsterbyte_fx_nosql_db
- MONGO_URI=mongodb://...

---

## FASE 3: VERIFICAR CONFIGURACIÓN NUEVA

```bash
# 7. Verificar que docker-compose.yml tiene la estructura correcta
cat docker-compose.yml

# 8. Verificar que los .env están correctos
cat backend/.env.dev
cat backend/.env.prod
cat backend/.env
```

**Puntos a verificar:**
- docker-compose.yml tiene profiles: ["dev"] y profiles: ["prod"]
- backend/.env.dev tiene credenciales de desarrollo
- backend/.env.prod tiene credenciales de producción
- backend/.env tiene las mismas variables que .env.dev (para uso local)

---

## FASE 4: LEVANTAR CON NUEVA CONFIGURACIÓN

### Para DESARROLLO (tu caso actual):
```bash
docker-compose --profile dev up -d
```

### Para PRODUCCIÓN:
```bash
docker-compose --profile prod up -d
```

### Verificar que los contenedores están corriendo:
```bash
docker ps
```

**Resultado esperado (DEV):**
- db_pg_tipsterbyte_fx_dev (puerto 5433)
- db_mongo_tipsterbyte_fx_dev (puerto 27017)

---

## FASE 5: VERIFICACIÓN DE CONEXIONES

```bash
# 8. Probar conexión PostgreSQL
docker exec -it db_pg_tipsterbyte_fx_dev psql -U postgres -d tipsterbyte_fx_db -c "\dt"

# 9. Probar conexión MongoDB
docker exec -it db_mongo_tipsterbyte_fx_dev mongosh -u tipster_admin -p tipster_mongo_pass --authenticationDatabase admin

# 10. Verificar logs por si hay errores
docker logs db_pg_tipsterbyte_fx_dev
docker logs db_mongo_tipsterbyte_fx_dev
```

---

## FASE 6: VERIFICAR APLICACIÓN

```bash
# 11. Desde tu backend, probar conexión a BD
cd backend
python -c "from core.db.sql.database_sql import engine; print(engine.connect())"

# 12. EJECUTAR MIGRACIONES (OBLIGATORIO antes de seeders)
# Las migraciones crean las tablas que los seeders necesitan
python manage.py sql migrate

# 13. EJECUTAR SEEDERS (después de migraciones)
# Los seeders necesitan que las tablas existan
python manage.py seed-sql AuthSeeder --update
```

**ORDEN CRÍTICO:**
1. **PRIMERO:** Ejecutar migraciones (`python manage.py sql migrate`)
2. **DESPUÉS:** Ejecutar seeders (`python manage.py seed-sql AuthSeeder --update`)

**Si ejecutas seeders sin migraciones primero, FALLARÁN porque las tablas no existen.**

---

## PUNTOS CRÍTICOS A VERIFICAR

| Item              | Desarrollo (dev)                 | Producción (prod)                  |
| ----------------- | -------------------------------- | ---------------------------------- |
| Puerto PostgreSQL | 5433                             | 5432                               |
| Puerto MongoDB    | 27017                            | 27017                              |
| Usuario Postgres  | postgres                         | tipsterbyte_admin                  |
| Usuario Mongo     | tipster_admin                    | tipsterbyte_admin                  |
| Contenedor PG     | db_pg_tipsterbyte_fx_dev         | db_pg_tipsterbyte_fx_prod          |
| Contenedor Mongo  | db_mongo_tipsterbyte_fx_dev      | db_mongo_tipsterbyte_fx_prod       |
| Volúmenes         | database_data_dev, mongodata_dev | database_data_prod, mongodata_prod |
| Red               | tipsterbyte_net                  | tipsterbyte_net                    |

---

## COMANDOS RÁPIDOS (RESUMEN)

```bash
# LIMPIEZA TOTAL
docker-compose down -v

# LEVANTAR DEV
docker-compose --profile dev up -d

# LEVANTAR PROD
docker-compose --profile prod up -d

# VERIFICAR
docker ps
docker logs db_pg_tipsterbyte_fx_dev
docker logs db_mongo_tipsterbyte_fx_dev

# SI ALGO FALLA, REINICIAR
docker-compose --profile dev restart

# ENTRAR A CONTENEDOR POSTGRES
docker exec -it db_pg_tipsterbyte_fx_dev bash

# ENTRAR A CONTENEDOR MONGO
docker exec -it db_mongo_tipsterbyte_fx_dev bash
```

---

## TROUBLESHOOTING

### Error: "container name is already in use"
```bash
docker-compose down -v
docker rm -f db_pg_tipsterbyte_fx_dev db_mongo_tipsterbyte_fx_dev
docker-compose --profile dev up -d
```

### Error: "port is already allocated"
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :5433
netstat -ano | findstr :27017
# Matar el proceso o cambiar puerto en docker-compose.yml
```

### Error: "connection refused"
```bash
# Verificar que el contenedor está corriendo
docker ps
# Ver logs
docker logs db_pg_tipsterbyte_fx_dev
# Reiniciar
docker-compose --profile dev restart
```

---

## NOTAS IMPORTANTES

1. **Volúmenes:** Los datos se guardan en volúmenes Docker. Al hacer down -v se borran.
2. **Perfiles:** Usa --profile dev o --profile prod según el entorno.
3. **Backups:** Los backups se guardan en ./backend/backups/
4. **Red:** Todos los contenedores comparten la red tipsterbyte_net

---

**Última actualización:** 23/03/2026