# 🚀 TipsterByte FX - Raíz del Proyecto

> **Nota importante**: Actualmente el código fuente se encuentra en `/backend`, pero próximamente será renombrado a `/src` para eliminar ambigüedades, ya que **TODO** lo que hay en esta raíz forma parte del Backend del proyecto.

---

## 🏗️ Arquitectura del Proyecto

### ✅ Principios Aplicados
- **Domain-Driven Design (DDD)**
- **Clean Architecture**
- **Separación de Responsabilidades**
- **Principios SOLID**

### ❓ ¿Por qué 2 Bases de Datos?
Este proyecto utiliza una arquitectura híbrida con **PostgreSQL + MongoDB** trabajando en conjunto, no es un error ni una arbitrariedad:

| **PostgreSQL (Relacional)**   | **MongoDB (No Relacional)**  |
| ----------------------------- | ---------------------------- |
| ✅ Datos transaccionales       | ✅ Logs, auditoría y eventos  |
| ✅ Entidades estructuradas     | ✅ Datos de alta volumen      |
| ✅ Integridad referencial      | ✅ Escrituras masivas rápidas |
| ✅ Consultas complejas         | ✅ Esquemas flexibles         |
| ✅ Configuraciones del sistema | ✅ Historiales y tracking     |

> **Regla de Oro**: Si necesitas `JOIN` va a PostgreSQL. Si insertas 1000 registros por minuto va a MongoDB.

Nunca se hace JOIN entre las dos bases de datos. Cada una cumple su función especifica y se comunican a traves de la capa de dominio.

---

## 📋 Índice de Artefactos en la Raíz

Todos los archivos que encuentras aquí NO son basura, cada uno tiene un propósito específico y definido:

| Archivo / Directorio                                    | Tipo            | Propósito                               |
| ------------------------------------------------------- | --------------- | --------------------------------------- |
| [`.flake8`](#-flake8)                                   | Configuración   | Linter de código Python                 |
| [`pyproject.toml`](#-pyprojecttoml)                     | Configuración   | Definición de proyecto y dependencias   |
| [`sonar-project.properties`](#-sonar-projectproperties) | Configuración   | Análisis de calidad SonarQube           |
| [`.coveragerc`](#-coveragerc)                           | Configuración   | Cobertura de tests                      |
| [`docker-compose.yml`](#-docker-composeyml)             | Infraestructura | Servicios y base de datos               |
| [`.env`](#-env)                                         | Configuración   | Variables de entorno                    |
| [`conftest_root.py`](#-conftest_rootpy)                 | Testing         | Configuración global de pytest          |
| [`scripts/`](#-scripts)                                 | Utilidades      | Scripts automatizados                   |
| [`procedimientos_base/`](#-procedimientos_base)         | Documentación   | Procedimientos oficiales del proyecto   |
| [`gestion_proyecto/`](#-gestion_proyecto)               | Gestión         | Documentos de planeación y diagnósticos |
| [`.clinerules`](#-clinerules)                           | Configuración   | Reglas para asistente IA Cline          |

---

## 🔧 Detalle por cada Artefacto

---

### ✅ `.flake8`
**Herramienta**: Flake8 - Linter de calidad de código Python

#### ¿Qué hace?
Verifica que el código cumpla con las convenciones PEP8, detecta errores sintácticos, complejidad ciclomática y código muerto.

#### Configuración actual:
```ini
max-line-length = 88
extend-ignore = E501
```

#### Uso:
```bash
# Ejecutar linter en todo el proyecto
flake8 backend/

# Ver solo errores (sin warnings)
flake8 backend/ --quiet
```

#### Referencias internas:
- 📄 `procedimientos_base/startup/architecture-analysis.md`
- 📄 `backend/docs/TESTING_GUIDE.md`

---

### ✅ `pyproject.toml`
**Estándar**: PEP 621 - Archivo oficial de definición de proyecto Python

#### ¿Qué contiene?
- Metadatos del proyecto
- Dependencias de desarrollo y producción
- Configuración de pytest
- Configuración de black (formateador)
- Configuración de isort (ordenado de imports)

#### Comandos útiles:
```bash
# Instalar todas las dependencias
pip install -e .

# Instalar solo dependencias de desarrollo
pip install -e .[dev]

# Actualizar dependencias
pip-compile pyproject.toml
```

#### Generado automáticamente, no editar manualmente sin consulta.

---

### ✅ `sonar-project.properties`
**Herramienta**: SonarQube - Análisis estático de calidad de código

#### ¿Qué hace?
Configuración para el escáner SonarQube, define que analizar, que excluir y como reportar los resultados.

#### Como ejecutar análisis:
1. Iniciar SonarQube:
```bash
docker-compose up -d sonarqube
```

2. Ejecutar escáner:
```bash
# Windows CMD
set SONAR_TOKEN=sqa_183a7e93d35f73d4a5a66a49a851c39c87115604
.\scripts\bat\run_full_analysis.bat

# PowerShell
$env:SONAR_TOKEN="sqa_183a7e93d35f73d4a5a66a49a851c39c87115604"
.\scripts\bat\run_full_analysis.bat
```

3. Acceder al dashboard: `http://localhost:9000`
   - Usuario: `admin`
   - Contraseña: `admin`

#### Referencias internas:
- 📄 `procedimientos_base/sonar/sonar-procedure.md` (GUÍA COMPLETA)
- 📄 `procedimientos_base/sonarqube-setup.md`

---

### ✅ `.coveragerc`
**Herramienta**: Coverage.py - Medición de cobertura de tests

#### ¿Qué hace?
Define que código medir, que excluir y como generar reportes de cobertura.

#### Generar reportes:
```bash
# Ejecutar tests con cobertura
pytest backend/ --cov=backend

# Generar reporte HTML
pytest backend/ --cov=backend --cov-report=html

# Generar reporte XML para SonarQube
pytest backend/ --cov=backend --cov-report=xml
```

> El reporte HTML se genera en `/htmlcov` y se puede abrir directamente en el navegador.

---

### ✅ `docker-compose.yml`
**Herramienta**: Docker Compose - Orquestación de servicios

#### Servicios definidos:
- PostgreSQL 15 (Base de datos principal)
- MongoDB 6 (Logs y datos no relacionales)
- SonarQube 9.9 (Análisis de calidad)
- Redis (Cache y cola de trabajos)
- pgAdmin (Gestor web PostgreSQL)

#### Comandos:
```bash
# Iniciar solo bases de datos
docker-compose up -d postgres mongodb redis

# Iniciar todo el stack
docker-compose up -d

# Ver logs
docker-compose logs -f sonarqube
```

---

### ✅ `.env`
**Archivo de variables de entorno**

> ⚠️ **NUNCA COMMITEAR ESTE ARCHIVO** - Contiene secretos y credenciales.

Contiene:
- URLs de conexión a bases de datos
- Claves JWT
- API Keys de servicios externos
- Niveles de logging
- Configuraciones de entorno

#### Archivos relacionados:
- `backend/.env` - Entorno desarrollo
- `backend/.env.dev` - Entorno desarrollo alternativo
- `backend/.env.prod` - Entorno producción

---

### ✅ `conftest_root.py`
**Configuración global de pytest**

Define fixtures, hooks y configuración que se aplica a TODOS los tests del proyecto, sin importar el módulo.

---

### ✅ `scripts/`
**Directorio de scripts automatizados**

```
scripts/
├── bat/          # Scripts Windows (.bat)
├── bash/         # Scripts Linux/Mac (.sh)
└── README.md     # Documentación de cada script
```

#### Script principal:
`run_full_analysis.bat` - Ejecuta en secuencia:
1. Linter flake8
2. Todos los tests
3. Cobertura de código
4. Análisis SonarQube

---

### ✅ `procedimientos_base/`
**📚 Documentación oficial y procedimientos aprobados**

> Este es el lugar de verdad. Cualquier procedimiento aquí es el único válido.

```
procedimientos_base/
├── startup/          # Guías de inicio y arquitectura
├── sonar/            # Procedimiento SonarQube
├── db/               # Migraciones y seeders
└── tests/            # Guías de testing
```

---

### ✅ `gestion_proyecto/`
**📊 Gestión del proyecto**

Contiene:
- Diagnósticos técnicos
- Planes de desarrollo
- Decisiones técnicas registradas
- Análisis de impacto
- Roadmaps por fase

---

### ✅ `.clinerules`
**🤖 Reglas para asistente Cline**

Archivo de configuración que define las reglas, convenciones y estructura del proyecto para el asistente de desarrollo inteligente.

---

## 🎯 Comandos Rápidos

| Acción                      | Comando                                               |
| --------------------------- | ----------------------------------------------------- |
| Iniciar servidor desarrollo | `uvicorn backend.main:app --reload`                   |
| Ejecutar todos los tests    | `pytest backend/ -v`                                  |
| Ejecutar análisis completo  | `.\scripts\bat\run_full_analysis.bat`                 |
| Iniciar bases de datos      | `docker-compose up -d postgres mongodb`               |
| Diagnóstico del sistema     | `python backend/scripts/diagnose_processes_visual.py` |

---

## 🔗 Navegación entre Documentación Markdown

✅ **Funciona DIRECTAMENTE en el codigo fuente, NO necesitas vista previa**:

```markdown
✅ Formato correcto:
[Texto visible](./ruta/relativa/al/archivo.md)
```

#### 🖱️ **Como navegar SIN renderizar el MD**:
1. Simplemente estas viendo el codigo fuente crudo del markdown
2. Mantén presionada la tecla `Ctrl` (Windows) o `Cmd` (Mac)
3. Veras que el texto se vuelve **AZUL y subrayado automaticamente**
4. Haz CLICK IZQUIERDO
5. ✅ SE ABRE INMEDIATAMENTE el archivo destino en nueva pestaña

> 🎯 Esto funciona incluso si estas viendo el archivo en modo edicion, sin ningun preview ni renderizado. VS Code detecta los links automaticamente en el texto plano.

#### 📌 Extensiones recomendadas para mejor experiencia:
| Extensión               | Uso                                                    |
| ----------------------- | ------------------------------------------------------ |
| **Markdown All in One** | Tabla de contenidos auto generada, atajos              |
| **Path Intellisense**   | Autocompletado de rutas 100% preciso al escribir       |
| **Foam**                | Wikilinks, backlinks y grafo completo de documentacion |

> 💡 Truco profesional: Escribe `./` y luego presiona `Ctrl + Espacio` - VS Code te mostrara un menu con todos los archivos y carpetas existentes para seleccionar.

---

## 📌 Importante

✅ **Todo lo que hay en esta raíz es parte integral del backend**

❌ No borres ni modifiques ninguno de estos archivos sin conocer exactamente su propósito

📖 Si tienes dudas de algun archivo, primero revisa esta documentación, luego busca en `procedimientos_base/`

---

> Última actualización: Octubre 2026
> Proyecto: TipsterByte FX - Backend Python FastAPI