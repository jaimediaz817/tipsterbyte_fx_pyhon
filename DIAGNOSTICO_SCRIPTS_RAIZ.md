# 🔍 DIAGNÓSTICO: Archivos de Scripts en Raíz del Proyecto

**Fecha**: 25 de marzo de 2026  
**Analista**: Arquitecto de Software  
**Nivel de Impacto**: 🟡 MEDIO (Crecimiento descontrolado)

---

## 📊 ESTADO ACTUAL

### Archivos .bat en raíz (5 archivos):
```
clean_sonarqube.bat
coverage_report.bat
install_sonar_scanner.bat
run_full_analysis.bat
run_sonar_analysis.bat
```

### Archivos .sh en raíz (2 archivos):
```
install_sonar_scanner.sh
run_sonar_analysis.sh
```

### Archivos .ps1 en raíz (1 archivo):
```
download_sonar.ps1
```

### Scripts Python sueltos:
```
scripts/generate_coverage_report.py  (SIN DOCUMENTACIÓN)
```

**Total**: 9 archivos de scripts dispersos en raíz

---

## ⚠️ PROBLEMAS IDENTIFICADOS

### 1. **Raíz contaminada** 🔴
- La raíz del proyecto tiene 9 archivos de scripts
- Mezcla de lenguajes: .bat, .sh, .ps1, .py
- Difícil encontrar archivos de configuración reales

### 2. **Falta de documentación** 🔴
- `scripts/generate_coverage_report.py` NO tiene documentación
- No se sabe cómo usarlo: `python scripts/generate_coverage_report.py --threshold 100`
- Usuarios nuevos no saben qué scripts existen

### 3. **Inconsistencia de nombres** 🟡
- Algunos empiezan con `run_`
- Otros con `install_`
- Otros con `clean_`
- Sin convención clara

### 4. **Scripts multiplataforma dispersos** 🟡
- `.bat` (Windows)
- `.sh` (Linux/Mac)
- `.ps1` (PowerShell)
- Todos en raíz sin organización

### 5. **Scripts Python en carpeta equivocada** 🟡
- `scripts/generate_coverage_report.py` está en `scripts/`
- Pero no hay documentación de su existencia
- Otros scripts similares podrían existir sin saberse

---

## 💡 SOLUCIONES PROPUESTAS

### **Opción A: Carpeta `scripts_bat/`** (Simple)
```
scripts_bat/
├── clean_sonarqube.bat
├── coverage_report.bat
├── install_sonar_scanner.bat
├── run_full_analysis.bat
└── run_sonar_analysis.bat
```

**Ventajas**:
- ✅ Simple de implementar
- ✅ Solo mueve archivos .bat

**Desventajas**:
- ❌ No resuelve el problema de .sh y .ps1
- ❌ No documenta scripts Python
- ❌ Solución parcial

---

### **Opción B: Carpeta `scripts/` unificada** (Recomendada) ⭐
```
scripts/
├── README.md                    # Documentación maestra
├── bat/                         # Scripts Windows
│   ├── clean_sonarqube.bat
│   ├── coverage_report.bat
│   ├── install_sonar_scanner.bat
│   ├── run_full_analysis.bat
│   └── run_sonar_analysis.bat
├── sh/                          # Scripts Linux/Mac
│   ├── install_sonar_scanner.sh
│   └── run_sonar_analysis.sh
├── ps1/                         # Scripts PowerShell
│   └── download_sonar.ps1
└── python/                      # Scripts Python
    ├── generate_coverage_report.py
    └── [otros scripts futuros]
```

**Ventajas**:
- ✅ Organización completa por lenguaje
- ✅ Un solo lugar para todos los scripts
- ✅ Fácil de documentar con README.md
- ✅ Escalable para futuro
- ✅ Consistente con estructura `backend/commands/`

**Desventajas**:
- ⚠️ Requiere actualizar rutas en algunos archivos

---

### **Opción C: Mantener `scripts/` existente + crear subcarpetas** (Híbrida)
```
scripts/
├── README.md
├── generate_coverage_report.py   # Ya existe
├── bat/
│   └── [archivos .bat]
├── sh/
│   └── [archivos .sh]
└── ps1/
    └── [archivos .ps1]
```

**Ventajas**:
- ✅ Aprovecha carpeta `scripts/` existente
- ✅ Menos cambios

**Desventajas**:
- ⚠️ Mezcla Python con otros en nivel superior

---

## 🎯 RECOMENDACIÓN DEL ARQUITECTO

### **SOLUCIÓN RECOMENDADA: Opción B**

**Razones**:
1. **Consistencia**: Similar a `backend/commands/` organizado por grupos
2. **Escalabilidad**: Fácil agregar más scripts en futuro
3. **Documentación**: Un solo README.md central
4. **Multiplataforma**: Soporta Windows, Linux, Mac, PowerShell
5. **Descubribilidad**: Developers saben dónde buscar

### **Impacto de Migración**:

| Archivo                               | Cambio Requerido                  | Impacto    |
| ------------------------------------- | --------------------------------- | ---------- |
| `docker-compose.yml`                  | Ninguno                           | ✅          |
| `README.md`                           | Actualizar referencias            | 🟡 Bajo     |
| `pyproject.toml`                      | Ninguno                           | ✅          |
| Scripts .bat                          | Mover + actualizar rutas internas | 🟡 Medio    |
| Scripts .sh                           | Mover + actualizar rutas internas | 🟡 Medio    |
| `scripts/generate_coverage_report.py` | Documentar                        | 🟢 Muy bajo |

---

## 📋 PLAN DE MIGRACIÓN

### Paso 1: Crear estructura
```bash
mkdir -p scripts/bat scripts/sh scripts/ps1 scripts/python
```

### Paso 2: Mover archivos
```bash
move *.bat scripts/bat/
move *.sh scripts/sh/
move *.ps1 scripts/ps1/
```

### Paso 3: Crear documentación
```markdown
# scripts/README.md

## Scripts Disponibles

### Windows (.bat)
- `run_full_analysis.bat` - Ejecuta análisis completo SonarQube
- `run_sonar_analysis.bat` - Ejecuta solo SonarQube
- `coverage_report.bat` - Genera reporte de cobertura
- `install_sonar_scanner.bat` - Instala SonarQube scanner
- `clean_sonarqube.bat` - Limpia configuración SonarQube

### Linux/Mac (.sh)
- `run_sonar_analysis.sh` - Ejecuta SonarQube
- `install_sonar_scanner.sh` - Instala scanner

### PowerShell (.ps1)
- `download_sonar.ps1` - Descarga SonarQube

### Python
- `python/generate_coverage_report.py` - Genera reporte coverage
  Uso: `python scripts/python/generate_coverage_report.py --threshold 100`
```

### Paso 4: Actualizar referencias
- Actualizar `README.md` principal
- Verificar CI/CD si aplica

---

## 📊 ESTIMACIÓN DE ESFUERZO

| Tarea                     | Tiempo     | Dificultad     |
| ------------------------- | ---------- | -------------- |
| Crear estructura carpetas | 2 min      | Baja           |
| Mover archivos            | 5 min      | Baja           |
| Crear README.md scripts   | 15 min     | Baja           |
| Actualizar referencias    | 10 min     | Media          |
| Testing de scripts        | 15 min     | Media          |
| **Total**                 | **47 min** | **Baja-Media** |

---

## ✅ BENEFICIOS ESPERADOS

1. **Raíz limpia**: Solo archivos de configuración esenciales
2. **Descubribilidad**: Developers encuentran scripts fácil
3. **Documentación**: README.md central explica todo
4. **Multiplataforma**: Soporte completo Windows/Linux/Mac
5. **Escalabilidad**: Fácil agregar nuevos scripts
6. **Profesionalismo**: Estructura organizada y mantenible

---

## 🎯 CONCLUSIÓN

**Estado actual**: 🟡 Crecimiento descontrolado  
**Solución recomendada**: Opción B (scripts/ unificada)  
**Impacto**: Bajo-Medio  
**Beneficio**: Alto (organización + documentación)  
**Prioridad**: 🟡 Media (hacer antes de que crezca más)

**Veredicto**: ✅ **IMPLEMENTAR OPCIÓN B**

---

*Diagnóstico generado por análisis de arquitectura de software*