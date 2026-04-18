# 🚀 MANUAL OFICIAL: Población de Tablas y Migraciones en Producción
> **TipsterByte FX** | Versión: 1.0 | Estado: Aprobado para Producción
>
> ✅ Este documento es el procedimiento oficial y el unico valido para operaciones de base de datos en entornos productivos.

---

## ⚠️ PRINCIPIO FUNDAMENTAL INVIOLABLE
> ❌ **NUNCA, BAJO NINGUN CONCEPTO, EJECUTAR:**
> ```bash
> python manage.py sql seed
> ```
> Este comando ejecuta TODOS los seeders incluyendo datos de prueba, duplica registros y puede corromper completamente la base de datos de producción.

---

## 📋 CLASIFICACION DE ESCENARIOS

| Escenario         | Descripcion                                        | Procedimiento a aplicar |
| ----------------- | -------------------------------------------------- | ----------------------- |
| 🟢 **ESCENARIO 1** | Primer despliegue absoluto, BD completamente vacia | Procedimiento A         |
| 🟡 **ESCENARIO 2** | Despliegue regular, BD ya tiene datos              | Procedimiento B         |
| 🔴 **ESCENARIO 3** | Correccion de datos maestros existentes            | Procedimiento C         |
| ⚫ **ESCENARIO 4** | Migracion de estructura de BD                      | Procedimiento D         |

---

---

## 🟢 PROCEDIMIENTO A: PRIMER DESPLIEGUE ABSOLUTO
> ✅ Aplicar UNICAMENTE cuando la base de datos esta 100% vacia y no tiene ningun registro.

### Paso a Paso:
```bash
# 🔹 1. Aplicar TODAS las migraciones de estructura
python manage.py sql migrate head

# 🔹 2. Inicializar esquema y indices MongoDB
python manage.py nosql init-schema

# 🔹 3. Ejecutar SEEDERS DE DATOS MAESTROS EN ORDEN EXACTO:
# ✅ PlatformConfig: Configuraciones base del sistema
python manage.py sql seed PlatformConfigSeeder --update

# ✅ Geografia: Continentes, Paises, Zonas horarias
python manage.py sql seed GeografiaSeeder --update

# ✅ Leagues Manager: Ligas, Torneos, Fuentes de extraccion
python manage.py sql seed LeaguesManagerSeeder --update

# ❌ FIN: NO EJECUTAR NINGUN OTRO SEEDER
```

### ✅ Verificacion post-ejecucion:
```bash
# Ejecutar diagnostico completo
python -m commands.db.admin.diagnose_db
```
✅ Debe mostrar:
- Tablas creadas: 16+
- Registros en `platform_config` > 0
- Registros en `continentes` = 6
- Registros en `paises` = 249

---

## 🟡 PROCEDIMIENTO B: DESPLIEGUE REGULAR (BD CON DATOS)
> ✅ Aplicar en todos los despliegues normales despues del primer lanzamiento.

### Reglas:
✅ **NUNCA ejecutas seeders completos**
✅ **Solo se ejecutan migraciones de Alembic**
✅ **Nunca se insertan datos maestros via seeders**

### Paso a Paso:
```bash
# 🔹 1. Ver estado actual de migraciones
python manage.py sql status

# 🔹 2. Ver que migraciones se van a aplicar
python manage.py sql migrate

# 🔹 3. Aplicar migraciones pendientes
python manage.py sql migrate head

# 🔹 4. Verificar nuevamente el estado
python manage.py sql status

# 🔹 5. Actualizar esquema MongoDB si es necesario
python manage.py nosql init-schema
```

---

## 🔴 PROCEDIMIENTO C: ACTUALIZACION DE DATOS MAESTROS
> ✅ Aplicar cuando se necesita agregar o actualizar registros maestros existentes.

### Opcion 1: ✅ RECOMENDADA (Segura para Prod)
1. Crea un **archivo de migracion Alembic dedicado**
2. Escribe la logica de insercion/actualizacion dentro de la migracion
3. Aplica la migracion normalmente
4. Queda registrado en el historial de migraciones

### Opcion 2: Seeder especifico (Permitido)
```bash
# ✅ Solo el seeder concreto que necesites, NUNCA TODOS
python manage.py sql seed NombreDelSeeder --update
```

✅ El flag `--update` activa modo UPSERT:
- Si el registro no existe: lo crea
- Si el registro ya existe: lo actualiza con los valores nuevos
- Es seguro ejecutar multiples veces
- No duplica datos

---

## ⚫ PROCEDIMIENTO D: MIGRACIONES DE ESTRUCTURA
> ✅ Protocolo oficial para cambios en la estructura de tablas.

### Reglas inviolables:
1. ❌ Nunca creas migraciones en producción
2. ❌ Nunca borras archivos de migración
3. ✅ Todas las migraciones se crean en desarrollo
4. ✅ Todas las migraciones se prueban en Staging
5. ✅ Solo se aplican en Produccion una vez validadas

### Paso a Paso seguro:
```bash
# EN DESARROLLO:
python manage.py sql create-migration -m "descripcion del cambio"

# EN STAGING:
python manage.py sql migrate head

# EN PRODUCCION:
python manage.py sql status
python manage.py sql migrate head
```

---

## 🛡️ CARACTERISTICAS DE SEGURIDAD IMPLEMENTADAS

| Funcionalidad                              | Estado         | Ubicacion                   |
| ------------------------------------------ | -------------- | --------------------------- |
| ✅ Transacciones atomicas por seeder        | ✅ Implementado | BaseSeeder                  |
| ✅ Modo UPSERT con flag --update            | ✅ Implementado | BaseSeeder.run()            |
| ✅ Orden de prioridad automatico de seeders | ✅ Implementado | sql_seeder_orchestrator.py  |
| ✅ Deteccion de migraciones desincronizadas | ✅ Implementado | manage.py linea 248         |
| ✅ Stamp automatico si tablas ya existen    | ✅ Implementado | manage.py linea 163         |
| ✅ Rollback automatico en caso de error     | ✅ Implementado | get_db_context              |
| ✅ No se duplican datos maestros            | ✅ Implementado | Todos los seeders oficiales |

---

## ✅ CHECKLIST OPERACIONAL PRODUCCION

### 🟢 ANTES DE EMPEZAR:
- [ ] Hacer backup completo de base de datos
- [ ] Verificar que `ENV=production` y `DEBUG=False`
- [ ] Verificar que no hay transacciones abiertas
- [ ] Parar la aplicacion y el scheduler

### 🟢 DURANTE OPERACION:
- [ ] Ejecutar comandos en el orden establecido
- [ ] Verificar salida de cada comando antes de seguir
- [ ] No ejecutar ningun comando no documentado
- [ ] Monitorear logs de base de datos

### 🟢 DESPUES DE FINALIZAR:
- [ ] Ejecutar diagnostico de BD
- [ ] Verificar conteo de registros
- [ ] Iniciar aplicacion
- [ ] Monitorear por 1 hora
- [ ] Registrar operacion en el log de despliegues

---

## ❌ COMANDOS PROHIBIDOS EN PRODUCCION
> ⚠️ La ejecucion de cualquiera de estos comandos constituye una violacion del protocolo de seguridad:

| Comando                                 | Motivo prohibicion                                   |
| --------------------------------------- | ---------------------------------------------------- |
| `python manage.py sql seed`             | Ejecuta todos los seeders incluyendo datos de prueba |
| `python manage.py sql truncate *`       | Elimina todo el contenido de las tablas              |
| `python manage.py sql create-migration` | Crea migraciones directamente en prod                |
| `python manage.py sql state reset`      | Resetea completamente el historial de migraciones    |
| `python manage.py nosql seed`           | Inyecta datos de prueba en MongoDB                   |

---

## 🆘 SOLUCION DE PROBLEMAS

### ❌ Error: "Migracion desincronizada"
✅ Solucion:
```bash
python manage.py sql state clear-migrations
python manage.py sql stamp head
```

### ❌ Error: "Ya existe el registro" al ejecutar seeder
✅ Solucion:
```bash
# Siempre agrega --update
python manage.py sql seed NombreSeeder --update
```

### ❌ Error: Migracion falla a mitad
✅ Solucion:
- Alembic automaticamente hace rollback
- Corrige el error en el archivo de migracion
- Vuelve a ejecutar

---

## 📌 REFERENCIAS
- [Guia de Despliegue General](./startup/deployment-guide.md)
- [Procedimiento de Migraciones Docker](./startup/docker-migration-procedure.md)
- [Estandares de Base de Datos](./db-standards.md)

---

> ✅ **Documento aprobado y vigente desde: 17/04/2026**
> Cualquier desviacion de este procedimiento debe ser autorizada previamente.




perfecto! podríamos complemetnar al manula como es el procdimiento en entorno de dsarolo? teniendo en cuenta comadnos y tal definido! 
lo que recuerdo que siempre hago es:
ejecuto el comando custom de manage.py para borrar primero todo! base de datos y tablas, luego creo la estructura, lyuego ejecuto el comando python manage.py project status
, vierifico con la opcion 1, y luego me adebería aparecer un mensaje que si quiero ejecutar los seeders