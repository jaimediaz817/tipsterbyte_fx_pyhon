# 📜 Scripts del Proyecto - TipsterByte FX

**Última actualización**: 25 de marzo de 2026

---

## 📋 Índice

- [Scripts Windows (.bat)](#scripts-windows-bat)
- [Scripts Linux/Mac (.sh)](#scripts-linuxmac-sh)
- [Scripts PowerShell (.ps1)](#scripts-powershell-ps1)
- [Scripts Python](#scripts-python)

---

## Scripts Windows (.bat)

### `run_full_analysis.bat`
**Descripción**: Ejecuta análisis completo de SonarQube (tests + coverage + análisis estático)

**Uso**:
```batch
.\scripts\bat\run_full_analysis.bat
```

**Requisitos**:
- Docker Desktop corriendo (SonarQube)
- Variables de entorno configuradas

---

### `run_sonar_analysis.bat`
**Descripción**: Ejecuta solo análisis de SonarQube (sin tests)

**Uso**:
```batch
.\scripts\bat\run_sonar_analysis.bat
```

**Requisitos**:
- Docker Desktop corriendo
- `SONAR_TOKEN` configurado

---

### `coverage_report.bat`
**Descripción**: Genera reporte de cobertura de código

**Uso**:
```batch
.\scripts\bat\coverage_report.bat
```

**Salida**: Archivo `coverage.xml` en raíz del proyecto

---

### `install_sonar_scanner.bat`
**Descripción**: Instala SonarQube Scanner en el sistema

**Uso**:
```batch
.\scripts\bat\install_sonar_scanner.bat
```

---

### `clean_sonarqube.bat`
**Descripción**: Limpia configuración y datos de SonarQube

**Uso**:
```batch
.\scripts\bat\clean_sonarqube.bat
```

---

## Scripts Linux/Mac (.sh)

### `run_sonar_analysis.sh`
**Descripción**: Ejecuta análisis de SonarQube en Linux/Mac

**Uso**:
```bash
chmod +x scripts/sh/run_sonar_analysis.sh
./scripts/sh/run_sonar_analysis.sh
```

---

### `install_sonar_scanner.sh`
**Descripción**: Instala SonarQube Scanner en Linux/Mac

**Uso**:
```bash
chmod +x scripts/sh/install_sonar_scanner.sh
./scripts/sh/install_sonar_scanner.sh
```

---

### `vps_health_check.sh`
**Descripción**: Agente de Health Check STANDALONE para VPS. ✅ SIN DEPENDENCIAS, NO NECESITA NADA INSTALADO. Funciona en cualquier Ubuntu/Debian. Verifica recursos basicos del servidor: SO, RAM, CPU, Disco, Red.

**Caracteristicas**:
- No requiere Python ni librerias
- No modifica nada en el servidor
- Solo lectura, no deja rastro ni logs
- Codigos de color por nivel de riesgo

**Uso**:
```bash
# Subir al servidor
scp scripts/linux/vps_health_check.sh root@tu-ip-vps:/root/

# Dar permisos y ejecutar
chmod +x vps_health_check.sh
./vps_health_check.sh
```

**✅ Flujo completo de guardado**:
1.  Ejecuta el script en la VPS
2.  Copia TODO el texto de salida completo
3.  Envia el reporte al endpoint:
    ```http
    POST /api/v1/platform-config/vps/health-check
    Content-Type: text/plain

    [PEGAS AQUI TODO EL TEXTO DEL REPORTE]
    ```

✅ El sistema automaticamente:
- Parsea todos los valores del reporte
- Valida y normaliza las metricas
- Guarda el historial completo en MongoDB
- Genera alertas si hay valores criticos
- Calcula tendencias y estadisticas historicas

📊 Coleccion MongoDB: `vps_health_checks`

---

### `tipsterbyte_control_agent.py`
**Descripción**: Agente de Control y Diagnostico completo. Chequea conectividad a Bases de Datos, PostgreSQL, MongoDB, recursos del sistema y estado general de la instalacion.

**Caracteristicas**:
- Standalone o compilable a binario
- Carga automaticamente variables de entorno
- Verifica conexiones reales a las bases de datos
- Genera informe detallado con recomendaciones
- Indica acciones requeridas inmediatamente

---

### `run_control_agent.sh`
**Descripción**: Script wrapper de ejecucion automatica para el Control Agent. Busca automaticamente el archivo .env, detecta si hay Python instalado, y descarga el agente automaticamente si no existe.

**Uso**:
```bash
chmod +x scripts/linux/run_control_agent.sh
./run_control_agent.sh

# O especificando ruta al .env
./run_control_agent.sh /ruta/a/tu/.env
```

---

## Scripts PowerShell (.ps1)

### `download_sonar.ps1`
**Descripción**: Descarga SonarQube desde internet

**Uso**:
```powershell
.\scripts\ps1\download_sonar.ps1
```

---

## Scripts Python

### `generate_coverage_report.py`
**Descripción**: Genera reporte de cobertura de código con umbral configurable

**Uso**:
```bash
# Generar reporte con umbral del 100%
python scripts/python/generate_coverage_report.py --threshold 100

# Generar reporte con umbral del 80%
python scripts/python/generate_coverage_report.py --threshold 80
```

**Parámetros**:
- `--threshold`: Porcentaje mínimo de cobertura requerido (default: 100)

**Salida**: 
- Reporte en consola
- Archivo `coverage.xml` generado

**Requisitos**:
- `pytest` instalado
- `pytest-cov` instalado

---

## 🔧 Configuración Necesaria

### Variables de Entorno

```bash
# Windows CMD
set SONAR_TOKEN=sqa_183a7e93d35f73d4a5a66a49a851c39c87115604

# PowerShell
$env:SONAR_TOKEN="sqa_183a7e93d35f73d4a5a66a49a851c39c87115604"

# Linux/Mac
export SONAR_TOKEN="sqa_183a7e93d35f73d4a5a66a49a851c39c87115604"
```

### Docker

Asegúrate de que Docker Desktop esté corriendo antes de ejecutar scripts de SonarQube:
```bash
docker ps  # Verificar que Docker está activo
```

---

## 📊 Flujo Recomendado

1. **Instalar SonarQube Scanner** (solo primera vez)
   ```batch
   .\scripts\bat\install_sonar_scanner.bat
   ```

2. **Configurar token**
   ```batch
   set SONAR_TOKEN=sqa_183a7e93d35f73d4a5a66a49a851c39c87115604
   ```

3. **Ejecutar análisis completo**
   ```batch
   .\scripts\bat\run_full_analysis.bat
   ```

4. **Revisar resultados en** http://localhost:9000

---

## 🐛 Troubleshooting

### Error: "sonar-scanner no se reconoce"
**Solución**: Ejecutar `install_sonar_scanner.bat` primero

### Error: "Docker no está corriendo"
**Solución**: Iniciar Docker Desktop

### Error: "Token inválido"
**Solución**: Verificar que `SONAR_TOKEN` esté configurado correctamente

---

## 📞 Soporte

Para dudas o problemas, contactar al equipo de desarrollo.

---

*Documentación generada automáticamente*