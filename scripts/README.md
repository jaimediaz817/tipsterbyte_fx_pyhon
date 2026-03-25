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