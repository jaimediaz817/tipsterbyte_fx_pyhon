# TipsterByte FX - Backend
# TODO: pendiente refactorizar con cline!
---

## 🏁 Introducción y Contexto

Bienvenido al backend de TipsterByte FX. Este documento te guiará paso a paso para configurar el entorno, gestionar las bases de datos, levantar los servicios y ejecutar los comandos principales del proyecto.

---

## ⚙️ Entorno Virtual

### Crear entorno virtual

```bash
python -m venv venv
```

### Activar entorno virtual

**En PowerShell o CMD de Windows:**
```powershell
.\venv\Scripts\activate
```

**En Git Bash o WSL:**
```bash
source venv/Scripts/activate
```

### Desactivar entorno virtual

```bash
deactivate
```

### Verificar entorno virtual activo

```bash
where python
```

---

## 🗂️ Archivos y Carpetas Importantes

- Verificar si el archivo `.env` existe:
  ```bash
  python -c "from pathlib import Path; print('✅' if Path('.env').exists() else '❌', Path('.env').resolve())"
  ```

- Eliminar carpeta y contenido del entorno virtual:
  ```bash
  rm -rf .venv
  ```

---

## 🐳 Docker

### Levantar servicios con Docker

```bash
docker-compose up -d
```
Esto inicia:
- PostgreSQL en `localhost:5432`
- MongoDB en `localhost:27017`

También puedes levantar servicios individuales:
```bash
docker-compose up -d postgres_tipsterbyte
docker-compose up -d mongo_tipsterbyte
```

---

## 📦 Instalación de Dependencias

### Instalar dependencias principales

```bash
pip install -r requirements.txt
```

### Instalar dependencias específicas

- SQLAlchemy, Alembic, asyncpg:
  ```bash
  pip install sqlalchemy[asyncio] asyncpg alembic
  ```
- Motor (MongoDB):
  ```bash
  pip install motor
  ```
- Logger:
  ```bash
  pip install loguru
  ```
- Cryptography:
  ```bash
  pip install cryptography
  ```
- Pydantic Settings:
  ```bash
  pip install pydantic-settings
  ```
- Beanie (ODM para MongoDB):
  ```bash
  pip install beanie motor pydantic
  ```
- Flake8 (linter):
  ```bash
  pip install flake8
  ```
- Typer (CLI):
  ```bash
  pip install "typer[all]" psycopg2-binary
  ```

---

## 🗃️ Estructura de Carpetas

```
backend/
├── alembic/
├── apps/
├── core/
├── scripts/
│   ├── db/
│   │   ├── reset_database.py
│   │   ├── backup_database.py
│   │   └── restore_database.py
│   └── seed_database.py
└── venv/
```

---

## 🛠️ Alembic y Migraciones

### Inicializar Alembic

```bash
alembic init alembic
```

### Crear migración

```bash
alembic revision --autogenerate -m "initial auth tables"
```

### Aplicar migración

```bash
alembic upgrade head
```

### Comandos personalizados con manage.py

- Crear migración con mensaje:
  ```bash
  python manage.py sql create-migration "Tu mensaje descriptivo"
  ```
- Crear migración automática:
  ```bash
  python manage.py sql create-migration
  ```
- Aplicar migraciones:
  ```bash
  python manage.py sql migrate
  ```

---

## 🗄️ Gestión de Bases de Datos

### PostgreSQL (SQL)

- Crear backup:
  ```bash
  python manage.py sql state backup
  ```
- Restaurar backup:
  ```bash
  python manage.py sql state restore
  ```
- Restaurar desde archivo específico:
  ```bash
  python manage.py sql state restore --file backups/postgresql_backups/nombre_del_archivo.sql
  ```
- Resetear BD (seguro):
  ```bash
  python manage.py sql state reset --with-backup
  ```
- Resetear BD (destructivo):
  ```bash
  python manage.py sql state reset --hard
  ```

### MongoDB (NoSQL)

- Crear backup:
  ```bash
  python manage.py nosql state backup
  ```
- Restaurar backup:
  ```bash
  python manage.py nosql state restore
  ```
- Restaurar desde archivo específico:
  ```bash
  python manage.py nosql state restore --file backups/mongo_backups/nombre_del_archivo.gz
  ```
- Resetear BD:
  ```bash
  python manage.py nosql state reset
  ```
- Aplicar migraciones de MongoDB:
  ```bash
  python manage.py nosql-migrate run
  ```

---

## 🧬 Seeders (Población de Datos Iniciales)

- Poblar base de datos SQL:
  ```bash
  python manage.py sql seed
  ```
- Poblar base de datos NoSQL:
  ```bash
  python manage.py nosql seed
  ```

---

## 🌐 Servidor Web

- Iniciar el servidor de desarrollo:
  ```bash
  python manage.py server run
  ```

- Detener el servidor si está corriendo:
  ```bash
  taskkill /F /IM python.exe
  netstat -ano | findstr :8010
  ```

---

## 🧩 Otros Comandos Útiles

- Ver ayuda general:
  ```bash
  python manage.py --help
  python manage.py sql --help
  python manage.py sql state --help
  python manage.py nosql --help
  python manage.py nosql state --help
  ```

---

## 📝 Notas y Consejos

- Si tienes problemas con el entorno virtual, reinicia el Language Server de Python en VS Code.
- El comando `deactivate` solo afecta la terminal actual.
- El comando `rm -rf env` elimina el entorno virtual por completo.
- El archivo `.env` debe existir en la raíz del proyecto.

---

## 🚀 Flujo de Trabajo Recomendado

1. Levanta los contenedores de Docker.
2. Activa el entorno virtual.
3. Instala las dependencias.
4. Aplica migraciones SQL.
5. Pobla las bases de datos (SQL y NoSQL).
6. Inicia el servidor web.

---

**¡Listo! Ahora tu README está ordenado y segmentado para que cualquier nuevo miembro pueda entender el contexto y los procedimientos del proyecto de forma clara y





hacer testpath:

Test-Path core/.fernet.key
Test-Path ./.fernet.key