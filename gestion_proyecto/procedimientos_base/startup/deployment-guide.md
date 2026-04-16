# 🚀 GUÍA DE DESPLIEGUE - TipsterByte FX

**Fecha:** 2026-03-22
**Versión:** 1.0
**Estado:** LISTO PARA PRODUCCIÓN

---

## 📋 **RESUMEN EJECUTIVO**

Esta guía cubre el despliegue de TipsterByte FX en:
- ✅ **Desarrollo Local** (tu máquina)
- ✅ **Pre-producción** (VPS Digital Ocean)
- ✅ **Producción** (VPS Digital Ocean)

---

## 🏗️ **ARQUITECTURA DE BASE DE DATOS**

### **Recomendación del Arquitecto: NO Múltiples BD**

**¿Por qué?**
1. **Overkill**: TipsterByte no es una aplicación enterprise masiva
2. **Complejidad**: Múltiples BD = múltiples backups, migraciones, monitoreo
3. **Costo**: Digital Ocean cobra por cada BD separada
4. **Tu arquitectura actual es correcta**: PostgreSQL + MongoDB es el estándar

### **Arquitectura Recomendada:**
```
✅ PostgreSQL: Datos estructurados (ligas, torneos, procesos, usuarios)
✅ MongoDB: Datos no estructurados (logs, scraping results, cache)
✅ Una instancia de cada, separadas por ambiente (dev/prod)
```

---

## 🔍 **COMANDOS DE DIAGNÓSTICO**

### **Verificar Conexión a BD:**
```bash
# Desde el directorio backend
python -m commands.db.admin.diagnose_db
```

**Salida esperada:**
```
🔍 DIAGNÓSTICO DE BASES DE DATOS
================================================================================

📋 CONFIGURACIÓN ACTUAL:
   🌍 Entorno: development
   🐛 Debug: True

================================================================================
🐘 POSTGRESQL
================================================================================
   ✅ CONEXIÓN EXITOSA:
      Versión PostgreSQL: PostgreSQL 17.9
      Base de Datos Actual: tipsterbyte_fx_db
      Usuario Conectado: postgres
      Tablas en BD: 16

================================================================================
🍃 MONGODB
================================================================================
   ✅ CONEXIÓN EXITOSA:
      Versión MongoDB: 5.0.32
      Base de Datos Actual: tipsterbyte_fx_nosql_db
      Colecciones: 1
```

---

## 🐳 **DOCKER COMPOSE - CONFIGURACIÓN CON PERFILES**

### **Estructura de Archivos:**
```
tipsterByte_fx/
├── docker-compose.yml          # Configuración con perfiles dev/prod
├── backend/
│   ├── .env                    # Configuración actual (desarrollo)
│   ├── .env.dev               # Configuración desarrollo
│   └── .env.prod              # Configuración producción
```

### **Características de la Configuración:**
- ✅ **Perfiles separados**: `dev` y `prod` para aislar ambientes
- ✅ **MongoDB con valores directos**: Credenciales hardcodeadas para evitar problemas de expansión de variables
- ✅ **Volúmenes separados**: `database_data_dev`, `database_data_prod`, `mongodata_dev`, `mongodata_prod`
- ✅ **Health checks**: PostgreSQL incluye verificación de salud
- ✅ **Recursos limitados**: Producción tiene límites de CPU y memoria

### **Comandos Docker Compose:**

#### **Desarrollo:**
```bash
# Iniciar servicios de desarrollo
docker-compose --profile dev up -d

# Verificar servicios (contenedores: db_pg_tipsterbyte_fx_dev, db_mongo_tipsterbyte_fx_dev)
docker-compose --profile dev ps

# Ver logs
docker-compose --profile dev logs -f

# Detener servicios
docker-compose --profile dev down
```

#### **Producción:**
```bash
# Iniciar servicios de producción
docker-compose --profile prod up -d

# Verificar servicios (contenedores: db_pg_tipsterbyte_fx_prod, db_mongo_tipsterbyte_fx_prod)
docker-compose --profile prod ps

# Ver logs
docker-compose --profile prod logs -f

# Detener servicios
docker-compose --profile prod down
```

#### **Limpieza Completa (si es necesario):**
```bash
# Eliminar todo: contenedores, imágenes, volúmenes
docker-compose down -v --rmi all

# Luego volver a levantar
docker-compose --profile dev up -d
```

---

## 📁 **CONFIGURACIÓN POR AMBIENTE**

### **Desarrollo (`.env.dev`):**
```env
ENV=development
DEBUG=True
POSTGRES_PORT=5433
MONGO_PORT=27017
LOG_LEVEL=DEBUG
LOG_RETENTION_DAYS=3
AUTO_CLEANUP_ENABLED=false
```

### **Producción (`.env.prod`):**
```env
ENV=production
DEBUG=False
POSTGRES_PORT=5432
MONGO_PORT=27017
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=30
AUTO_CLEANUP_ENABLED=true
CLEANUP_CRON="0 2 * * *"
```

---

## 🔐 **SEGURIDAD EN PRODUCCIÓN**

### **⚠️ CRÍTICO: Cambiar Credenciales por Defecto**

**En `.env.prod`, cambiar:**
```env
# ❌ INSEGURO (por defecto)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# ✅ SEGURO (cambiar por valores fuertes)
POSTGRES_USER=tipsterbyte_admin
POSTGRES_PASSWORD=TU_PASSWORD_FUERTE_AQUI_32_CHARS
```

### **Generar Passwords Fuertes:**
```bash
# Generar password de 32 caracteres
openssl rand -base64 32

# O usar Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📊 **MONITOREO Y DIAGNÓSTICO**

### **Comandos Útiles:**

#### **1. Verificar Estado de BD:**
```bash
python -m commands.db.admin.diagnose_db
```

#### **2. Verificar Logs de Docker:**
```bash
# PostgreSQL (contenedor: db_pg_tipsterbyte_fx_dev)
docker-compose --profile dev logs postgres_tipsterbyte_dev

# MongoDB (contenedor: db_mongo_tipsterbyte_fx_dev)
docker-compose --profile dev logs mongo_tipsterbyte_dev
```

#### **3. Verificar Conexiones Activas:**
```bash
# PostgreSQL
docker exec -it db_pg_tipsterbyte_fx_dev psql -U postgres -d tipsterbyte_fx_db -c "SELECT count(*) FROM pg_stat_activity;"

# MongoDB
docker exec -it db_mongo_tipsterbyte_fx_dev mongosh -u tipster_admin -p tipster_mongo_pass --eval "db.serverStatus().connections"
```

#### **4. Backup de BD:**
```bash
# PostgreSQL
docker exec db_pg_tipsterbyte_fx_dev pg_dump -U postgres tipsterbyte_fx_db > backup_$(date +%Y%m%d).sql

# MongoDB
docker exec db_mongo_tipsterbyte_fx_dev mongodump -u tipster_admin -p tipster_mongo_pass --out /backups/$(date +%Y%m%d)
```

---

## 🚀 **PASOS PARA DESPLEGAR EN DIGITAL OCEAN**

### **Paso 1: Preparar VPS**
```bash
# Conectar a tu VPS
ssh root@tu_ip_vps

# Actualizar sistema
apt update && apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt install docker-compose -y

# Verificar instalación
docker --version
docker-compose --version
```

### **Paso 2: Clonar Proyecto**
```bash
# Clonar repositorio
cd /opt
git clone https://github.com/tu_usuario/tipsterbyte_fx.git
cd tipsterbyte_fx
```

### **Paso 3: Configurar Producción**
```bash
# Copiar archivo de producción
cp backend/.env.prod backend/.env

# ⚠️ CRÍTICO: Editar credenciales
nano backend/.env
# Cambiar POSTGRES_PASSWORD y MONGO_PASSWORD
```

### **Paso 4: Iniciar Servicios**
```bash
# Iniciar servicios de producción
docker-compose --profile prod up -d

# Verificar que todo está corriendo
docker-compose --profile prod ps

# Ver logs
docker-compose --profile prod logs -f
```

### **Paso 5: Verificar Conexión**
```bash
# Ejecutar diagnóstico
python -m commands.db.admin.diagnose_db

# Deberías ver:
# ✅ CONEXIÓN EXITOSA para PostgreSQL
# ✅ CONEXIÓN EXITOSA para MongoDB
```

### **Paso 6: Ejecutar Seeders**
```bash
# Ejecutar seeders para crear tablas y datos iniciales
python -m scripts.db.seeders.run_all_seeders
```

### **Paso 7: Iniciar Aplicación**
```bash
# Iniciar servidor web
python main_init_web_server.py

# O usar gunicorn para producción
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main_init_web_server:app
```

---

## 🔧 **SOLUCIÓN DE PROBLEMAS**

### **Problema 1: No puedo conectar a PostgreSQL**
```bash
# Verificar que el contenedor está corriendo
docker-compose --profile dev ps

# Ver logs de PostgreSQL (contenedor: db_pg_tipsterbyte_fx_dev)
docker-compose --profile dev logs postgres_tipsterbyte_dev

# Verificar puerto
netstat -tuln | grep 5433

# Verificar salud del contenedor
docker exec db_pg_tipsterbyte_fx_dev pg_isready -U postgres
```

### **Problema 2: No puedo conectar a MongoDB**
```bash
# Verificar que el contenedor está corriendo
docker-compose --profile dev ps

# Ver logs de MongoDB (contenedor: db_mongo_tipsterbyte_fx_dev)
docker-compose --profile dev logs mongo_tipsterbyte_dev

# Verificar puerto
netstat -tuln | grep 27017

# Verificar conexión MongoDB
docker exec db_mongo_tipsterbyte_fx_dev mongosh -u tipster_admin -p tipster_mongo_pass --eval "db.adminCommand('ping')"
```

### **Problema 3: Error de credenciales**
```bash
# Verificar variables de entorno
cat backend/.env | grep POSTGRES
cat backend/.env | grep MONGO

# Reiniciar contenedores con nuevas credenciales
docker-compose --profile dev down
docker-compose --profile dev up -d
```

---

## 📝 **CHECKLIST DE DESPLIEGUE**

### **Antes de Desplegar:**
- [ ] Cambiar credenciales en `.env.prod`
- [ ] Verificar que los puertos no estén en uso
- [ ] Hacer backup de BD existente (si hay)
- [ ] Verificar que Docker está instalado

### **Durante el Despliegue:**
- [ ] Iniciar servicios con `docker-compose --profile prod up -d`
- [ ] Verificar que los contenedores están corriendo
- [ ] Ejecutar diagnóstico de BD
- [ ] Ejecutar seeders
- [ ] Verificar logs sin errores

### **Después del Despliegue:**
- [ ] Verificar que la aplicación responde
- [ ] Monitorear logs por 24 horas
- [ ] Configurar backups automáticos
- [ ] Documentar credenciales de forma segura

---

## 🎯 **RESUMEN DE CAMBIOS REALIZADOS**

### **Archivos Creados:**
1. ✅ `backend/commands/db/admin/diagnose_db.py` - Comando de diagnóstico
2. ✅ `docker-compose.yml` - Configuración con perfiles dev/prod
3. ✅ `backend/.env.dev` - Configuración desarrollo
4. ✅ `backend/.env.prod` - Configuración producción
5. ✅ `procedimientos_base/startup/deployment-guide.md` - Esta guía

### **Archivos Modificados:**
1. ✅ `backend/commands/db/admin/diagnose_db.py` - Corregido para SQLAlchemy 2.0

### **Comandos Disponibles:**
```bash
# Diagnóstico de BD
python -m commands.db.admin.diagnose_db

# Docker Compose
docker-compose --profile dev up -d    # Desarrollo
docker-compose --profile prod up -d   # Producción
```

---

## 🚀 **PRÓXIMOS PASOS**

1. **Probar en local**: Ejecutar `docker-compose --profile dev up -d`
2. **Verificar diagnóstico**: Ejecutar `python -m commands.db.admin.diagnose_db`
3. **Desplegar en Digital Ocean**: Seguir los pasos de esta guía
4. **Monitorear**: Verificar logs y rendimiento

---

## 📞 **SOPORTE**

Si tienes problemas:
1. Ejecutar `python -m commands.db.admin.diagnose_db`
2. Revisar logs: `docker-compose logs`
3. Verificar credenciales en `.env`
4. Contactar: jdsolutions817@gmail.com

---

**¡Listo para producción! 🚀**