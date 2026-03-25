# SonarQube - Guía de Configuración y Uso

## 📋 **RESUMEN**

Este documento describe cómo configurar y usar SonarQube para análisis de calidad de código en el proyecto **TipsterByte FX**.

---

## 🎯 **¿QUÉ ES SONARQUBE?**

SonarQube es una plataforma de análisis de código que detecta:
- **Bugs**: Errores potenciales en el código
- **Vulnerabilidades**: Problemas de seguridad
- **Code Smells**: Código difícil de mantener
- **Duplicaciones**: Código repetido
- **Coverage**: Porcentaje de código cubierto por tests

---

## 🏗️ **ARQUITECTURA**

```
┌─────────────────────────────────────────────────────────┐
│                    TIPSTERBYTE FX                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Backend    │      │   SonarQube  │                │
│  │   (Python)   │─────▶│   (Docker)   │                │
│  └──────────────┘      └──────────────┘                │
│         │                      │                        │
│         │                      │                        │
│         ▼                      ▼                        │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   pytest     │      │   Dashboard  │                │
│  │   + coverage │      │   :9000      │                │
│  └──────────────┘      └──────────────┘                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 **INSTALACIÓN RÁPIDA**

### **Paso 1: Iniciar SonarQube**

```bash
# Desde la raíz del proyecto
docker-compose up -d sonarqube
```

**Verificar que está corriendo:**
```bash
docker ps | grep sonarqube
```

**Acceder al dashboard:**
- URL: http://localhost:9000
- Usuario: `admin`
- Contraseña: `admin` (te pedirá cambiarla)

---

### **Paso 2: Configurar Proyecto en SonarQube**

1. Accede a http://localhost:9000
2. Haz clic en **"Create local project"**
3. Configura:
   - **Project key**: `tipsterbyte_fx`
   - **Display name**: `TipsterByte FX`
   - **Visibility**: Public

4. Ve a **My Account** → **Security** → **Generate Token**
5. Copia el token generado

---

### **Paso 3: Configurar Variables de Entorno**

**Windows (PowerShell):**
```powershell
$env:SONAR_TOKEN="tu_token_aquí"
```

**Windows (CMD):**
```cmd
set SONAR_TOKEN=tu_token_aquí
```

**Linux/Mac:**
```bash
export SONAR_TOKEN=tu_token_aquí
```

---

### **Paso 4: Ejecutar Análisis**

**Opción A: Usar script automatizado (RECOMENDADO)**

**Windows:**
```cmd
run_sonar_analysis.bat
```

**Linux/Mac:**
```bash
chmod +x run_sonar_analysis.sh
./run_sonar_analysis.sh
```

**Opción B: Ejecutar manualmente**

```bash
# 1. Instalar dependencias
cd backend
pip install pytest-cov pytest-xdist

# 2. Ejecutar tests con coverage
pytest --cov=apps --cov=core --cov=shared --cov-report=xml:coverage.xml --junitxml=test-results.xml

# 3. Ejecutar análisis SonarQube
cd ..
sonar-scanner -Dsonar.login=$SONAR_TOKEN -Dsonar.host.url=http://localhost:9000
```

---

## 📊 **INTERPRETAR RESULTADOS**

### **Dashboard Principal**

Accede a http://localhost:9000/dashboard?id=tipsterbyte_fx

**Métricas principales:**

| Métrica             | Descripción                 | Objetivo |
| ------------------- | --------------------------- | -------- |
| **Bugs**            | Errores potenciales         | 0        |
| **Vulnerabilities** | Problemas de seguridad      | 0        |
| **Code Smells**     | Código difícil de mantener  | < 100    |
| **Coverage**        | % código cubierto por tests | > 70%    |
| **Duplications**    | % código duplicado          | < 3%     |
| **Maintainability** | Rating de mantenibilidad    | A        |

---

### **Quality Gate**

El **Quality Gate** define los umbrales de calidad:

- ✅ **Passed**: El código cumple los estándares
- ❌ **Failed**: El código NO cumple los estándares

**Umbrales por defecto:**
- Coverage > 70%
- Duplications < 3%
- 0 Bugs críticos
- 0 Vulnerabilidades

---

## 🔧 **CONFIGURACIÓN AVANZADA**

### **Archivo sonar-project.properties**

Ubicado en la raíz del proyecto. Configuración principal:

```properties
# Proyecto
sonar.projectKey=tipsterbyte_fx
sonar.projectName=TipsterByte FX

# Código fuente
sonar.sources=backend/apps,backend/core,backend/shared
sonar.exclusions=**/__pycache__/**,**/.pytest_cache/**

# Tests
sonar.tests=backend/apps,backend/core/tests
sonar.test.inclusions=**/test_*.py,**/tests/**

# Coverage
sonar.python.coverage.reportPaths=backend/coverage.xml
```

---

### **Excluir Archivos del Análisis**

Para excluir archivos o directorios, agrega a `sonar.exclusions`:

```properties
sonar.exclusions=**/migrations/**,**/__init__.py,**/.git/**
```

---

## 🐛 **TROUBLESHOOTING**

### **Error: "sonar-scanner: command not found"**

**Solución:** Instalar sonar-scanner

```bash
# Opción 1: pip
pip install sonar-scanner

# Opción 2: Descargar manualmente
# https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
```

---

### **Error: "Cannot connect to Docker daemon"**

**Solución:** Verificar que Docker está corriendo

```bash
# Verificar estado
docker ps

# Iniciar Docker Desktop (Windows/Mac)
# O iniciar servicio Docker (Linux)
sudo systemctl start docker
```

---

### **Error: "SonarQube is not accessible"**

**Solución:** Verificar que SonarQube está corriendo

```bash
# Verificar contenedor
docker ps | grep sonarqube

# Ver logs
docker logs sonarqube_tipsterbyte

# Reiniciar
docker-compose restart sonarqube
```

---

### **Error: "Coverage report not found"**

**Solución:** Verificar que se generó el reporte

```bash
cd backend
ls -la coverage.xml

# Si no existe, ejecutar tests con coverage
pytest --cov=apps --cov=core --cov=shared --cov-report=xml:coverage.xml
```

---

### **Token Inválido o Expirado**

**Solución:** Generar nuevo token

1. Accede a http://localhost:9000/account/security
2. Revoca el token antiguo
3. Genera un nuevo token
4. Actualiza la variable de entorno

---

## 📈 **MEJORES PRÁCTICAS**

### **1. Ejecutar Análisis Regularmente**

- ✅ Antes de cada commit
- ✅ Después de cada pull request
- ✅ Semanalmente en CI/CD

---

### **2. Mantener Coverage Alto**

```bash
# Ver coverage actual
cd backend
coverage report -m

# Generar reporte HTML
coverage html
# Abrir: backend/htmlcov/index.html
```

---

### **3. Revisar Code Smells**

1. Accede al dashboard
2. Ve a **Issues** → **Code Smells**
3. Ordena por **Severity**
4. Resuelve los de mayor impacto

---

### **4. Configurar Alertas**

En SonarQube UI:
1. Ve a **Administration** → **Configuration** → **General Settings**
2. Configura **Email** notifications
3. Define umbrales de alerta

---

## 🔄 **INTEGRACIÓN CON CI/CD**

### **GitHub Actions (Futuro)**

```yaml
# .github/workflows/sonar.yml
name: SonarCloud Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - run: |
        cd backend
        pip install -r requirements.txt
        pytest --cov=apps --cov=core --cov=shared --cov-report=xml:coverage.xml
    - uses: SonarSource/sonarcloud-github-action@master
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

---

## 📚 **REFERENCIAS**

- **Documentación oficial**: https://docs.sonarqube.org/
- **Reglas de Python**: https://rules.sonarsource.com/python/
- **Quality Gates**: https://docs.sonarqube.org/latest/user-guide/quality-gates/
- **Coverage.py**: https://coverage.readthedocs.io/

---

## ✅ **CHECKLIST DE IMPLEMENTACIÓN**

- [x] SonarQube instalado en Docker
- [x] Configuración `sonar-project.properties` creada
- [x] Scripts automatizados creados
- [x] Dependencias `pytest-cov` agregadas
- [ ] Token de autenticación generado
- [ ] Primer análisis ejecutado
- [ ] Quality Gate configurado
- [ ] Dashboard revisado
- [ ] Documentación compartida con equipo

---

## 🎯 **PRÓXIMOS PASOS**

1. **Generar token** en SonarQube UI
2. **Ejecutar primer análisis** con el script
3. **Revisar resultados** en el dashboard
4. **Configurar Quality Gate** personalizado
5. **Integrar con CI/CD** (GitHub Actions)
6. **Configurar alertas** por email

---

**Última actualización**: 23 de marzo de 2026
**Responsable**: Arquitecto de Software