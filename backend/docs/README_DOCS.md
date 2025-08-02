
# 🚀 Proyecto Backend: Cruce Cartera Sura

Sistema backend con estructura por capas y procesos para la automatización de cruce de cartera con Sura.  
Incluye ejecución programada vía scheduler, ejecución manual vía API y trazabilidad por cliente y proceso.

---

## 📁 Estructura del Proyecto

- `apps/` — Lógica de dominio por procesos (ej: `cartera_sura`)
- `core/` — Configuración central, scheduler, logging, encriptación, etc.
- `shared/` — Repositorios comunes, utilidades y constantes compartidas
- `db/` — Conexión, modelos, y migraciones de base de datos

---

## 🔧 Configuración Inicial

### 1. Crear entorno virtual (opcional si no usas Docker)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
source venv/Scripts/activate  # Windows
```

### 2. Instalar dependencias
acceder a: cd `backend/`
```bash
pip install -r requirements.txt
```

---

## 🔐 Encriptación de valores sensibles

### Generar clave de cifrado

```bash
python -c "from app.core.secrets import generate_key; generate_key()"
```

Esto crea el archivo `.fernet.key` en `core/`.

### Encriptar valor

Desde la raíz de `backend/`:

```bash
python -c "from core.secrets import encrypt; print(encrypt('valor_a_encriptar'))"
```

---

## 🐳 Uso con Docker

### Levantar solo la base de datos

```bash
docker-compose up -d db
```

### Levantar todo el sistema

```bash
docker-compose up --build
```

### Levantar servicios individuales

```bash
docker-compose up -d selenium_hub
docker-compose up -d chrome_node
```

---

## 🗃️ Migraciones de Base de Datos

### Crear migración (luego de modificar modelos)

Desde la raíz de `backend/`:

```bash
alembic revision --autogenerate -m "Mensaje descriptivo"
```

### Aplicar migraciones

```bash
alembic upgrade head
```

---

## 📡 API & Documentación

Los endpoints están documentados automáticamente mediante OpenAPI. Puedes acceder a ellos en tiempo de ejecución:

- **Documentación interactiva (Swagger):** [http://localhost:8010/docs](http://localhost:8010/docs)
- **Redoc (alternativa):** [http://localhost:8010/redoc](http://localhost:8010/redoc)
- **Health check:** [http://localhost:8010/health](http://localhost:8010/health)

---

## 🧪 Pruebas Unitarias

### Instalar pytest (si aún no lo tienes)

```bash
pip install pytest
```

### Ejecutar pruebas

Desde la raíz del proyecto:

```bash
pytest backend/apps/cartera_sura/domain/tests/test_cruce_cartera.py
```

---

## 🧭 Ejecutar manualmente un proceso

```bash
python backend/main_init_scripts.py --process cruce_cartera_sura
```

---

## 🧾 Notas y ejemplos útiles

### Ejemplo de criterio para uso en Zoho

```python
criteria = {
    "and": [
        {"field": status_apiname, "comparator": "equal", "value": "Pendiente"},
        {
            "field": insurance_apiname,
            "comparator": "in",
            "value": [
                "Seguros de Vida Suramericana S.A.",
                "Seguros Generales Suramericana S.A",
                "SURA",
            ]
        }
    ]
}
```

---

## 📌 Recursos adicionales de monitoreo

Accesos cuando se levanta todo con Docker:

- 📊 **Grafana:** http://localhost:3000  
- 📈 **Prometheus:** http://localhost:9090  
- 🪵 **Loki:** http://localhost:3100  
- 📁 **Portainer:** https://localhost:9443  
- 🧾 **cAdvisor:** http://localhost:8080  

---

## 🧠 Preguntas frecuentes

- ¿Dónde configuro los jobs programados?
  > En la tabla `scheduled_process_config` o vía el archivo `core/scheduler_job_loader.py`.

- ¿Puedo lanzar manualmente procesos fallidos?
  > Sí, mediante el endpoint `/cruce-cartera-sura/retry`.

---

© Cider — 2025
