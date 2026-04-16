## Análisis de Integración Grafana + Prometheus para TipsterByte FX

Basándome en la estructura de tu proyecto, aquí está mi recomendación:

---

### 📊 **Tu Stack Actual**
- **Framework:** FastAPI
- **Scheduler:** APScheduler (AsyncIO)
- **Bases de datos:** PostgreSQL + MongoDB
- **Docker:** Sí (docker-compose)
- **Monitoreo básico:** Endpoint `/system/status` con psutil

---

### 🎯 **Métricas Clave Recomendadas**

#### 1. **HTTP/API Metrics**
- Total de requests por endpoint
- Duración de requests (latencia)
- Status codes (2xx, 4xx, 5xx)
- Requests por segundo (throughput)

#### 2. **Scheduler/Job Metrics**
- Jobs ejecutados (total, exitosos, fallidos)
- Duración de cada job
- Jobs pendientes en cola
- Errores por tipo de job

#### 3. **Database Metrics**
- Conexiones activas PostgreSQL
- Queries por segundo
- Tiempo de respuesta de queries
- Conexiones MongoDB activas

#### 4. **Scraping/Robots Metrics**
- Procesos de extracción ejecutados
- Registros procesados por fuente
- Tasa de éxito/fallo por robot
- Duración de scraping por fuente deportiva

#### 5. **System Metrics**
- CPU, memoria, disco (ya los tienes con psutil)
- Uso de red
- File descriptors abiertos

---

### 🛠️ **Implementación Recomendada**

#### **Paso 1: Agregar dependencia `prometheus-fastapi-instrumentator`**

```bash
pip install prometheus-fastapi-instrumentator
```

#### **Paso 2: Exponer métricas en FastAPI**

```python
# backend/main_init_web_server.py
from prometheus_fastapi_instrumentator import Instrumentator

# Después de crear la app FastAPI
Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    excluded_handlers=["/docs", "/redoc", "/openapi.json", "/system/health"],
).instrument(app).expose(app, endpoint="/metrics")
```

Esto automáticamente expone:
- `http_requests_total` - Total de requests
- `http_request_duration_seconds` - Duración por endpoint
- `http_requests_in_progress` - Requests en progreso

#### **Paso 3: Métricas personalizadas para el Scheduler**

```python
# backend/core/scheduler/metrics.py
from prometheus_client import Counter, Histogram, Gauge

# Contador de jobs ejecutados
scheduler_jobs_total = Counter(
    'scheduler_jobs_total',
    'Total de jobs ejecutados',
    ['job_name', 'status']  # status: success, failed
)

# Duración de jobs
scheduler_job_duration_seconds = Histogram(
    'scheduler_job_duration_seconds',
    'Duración de ejecución de jobs',
    ['job_name'],
    buckets=[1, 5, 10, 30, 60, 120, 300, 600]  # segundos
)

# Jobs activos
scheduler_jobs_active = Gauge(
    'scheduler_jobs_active',
    'Jobs actualmente en ejecución'
)
```

#### **Paso 4: Métricas para Robots/Scraping**

```python
# backend/apps/leagues_manager/metrics.py
from prometheus_client import Counter, Histogram

# Registros procesados
records_processed_total = Counter(
    'scraping_records_processed_total',
    'Total de registros procesados',
    ['source', 'status']  # source: liga, equipo, etc.
)

# Duración de scraping
scraping_duration_seconds = Histogram(
    'scraping_duration_seconds',
    'Duración de procesos de scraping',
    ['source']
)
```

#### **Paso 5: Actualizar docker-compose.yml**

```yaml
services:
  # ... tus servicios existentes ...

  # ====================
  # Prometheus
  # ====================
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus_tipsterbyte
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - tipsterbyte_net
    restart: always
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'

  # ====================
  # Grafana
  # ====================
  grafana:
    image: grafana/grafana:latest
    container_name: grafana_tipsterbyte
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    networks:
      - tipsterbyte_net
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Cambiar en producción
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  database_data:
  mongodata:
  prometheus_data:    # NUEVO
  grafana_data:       # NUEVO
```

#### **Paso 6: Configuración de Prometheus**

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # FastAPI app
  - job_name: 'tipsterbyte-api'
    static_configs:
      - targets: ['host.docker.internal:8000']  # O el nombre del servicio
    metrics_path: '/metrics'

  # PostgreSQL (necesitas postgres_exporter)
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # MongoDB (necesitas mongodb_exporter)
  - job_name: 'mongodb'
    static_configs:
      - targets: ['mongodb-exporter:9216']

  # Node exporter (métricas del sistema)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

---

### 📈 **Dashboards Recomendados en Grafana**

1. **Dashboard General del Sistema**
   - CPU, memoria, disco
   - Uptime de la aplicación
   - Requests por segundo

2. **Dashboard de API**
   - Latencia por endpoint (p50, p95, p99)
   - Tasa de errores
   - Top endpoints más lentos

3. **Dashboard de Scheduler**
   - Jobs ejecutados por hora
   - Tasa de éxito/fallo
   - Duración promedio de jobs

4. **Dashboard de Scraping**
   - Registros procesados por fuente
   - Tasa de éxito por robot
   - Alertas de fallos

---

### 🚀 **Orden de Implementación Sugerido**

1. ✅ Agregar `prometheus-fastapi-instrumentator` (métricas HTTP automáticas)
2. ✅ Agregar Prometheus al docker-compose
3. ✅ Agregar Grafana al docker-compose
4. ✅ Crear dashboard básico en Grafana
5. ⬜ Agregar métricas personalizadas del scheduler
6. ⬜ Agregar métricas de scraping/robots
7. ⬜ Agregar exporters para PostgreSQL y MongoDB
8. ⬜ Configurar alertas en Grafana

---

### 💡 **Consejo**

Empieza con **Paso 1-4** (lo mínimo viable). Con solo `prometheus-fastapi-instrumentator` ya tendrás métricas HTTP valiosas en ~15 minutos de trabajo. Las métricas personalizadas del scheduler y scraping pueden ir después.

¿Quieres que te ayude a implementar alguno de estos pasos?