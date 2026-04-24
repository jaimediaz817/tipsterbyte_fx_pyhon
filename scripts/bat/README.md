# 📜 Scripts BAT de Utilidad TipsterByte FX
============================================

## 🚀 run_coverage.bat

Script oficial y definitivo para ejecutar el coverage completo del proyecto.

### ✅ Caracteristicas:
- ✅ Borra automaticamente el cache anterior de coverage
- ✅ Incluye AUTOMATICAMENTE todos los modulos: `apps`, `core`, `shared` e `inspecciones_llm`
- ✅ Muestra el reporte completo en consola
- ✅ Genera automaticamente el archivo `coverage.xml` para SonarQube
- ✅ Funciona en CMD, PowerShell y Git Bash
- ✅ No requiere ninguna configuracion adicional
- ✅ Rutas relativas, funciona desde cualquier ubicacion

### 🛠️ Modo de uso:

#### Opcion 1: Doble click
Solo haz doble click sobre el archivo `run_coverage.bat`

#### Opcion 2: Desde terminal Git Bash / Linux
```bash
# Desde la raiz del proyecto
./scripts/bat/run_coverage.bat
```

#### Opcion 3: Desde terminal CMD / PowerShell
```bash
# Desde la raiz del proyecto
scripts\bat\run_coverage.bat
```

#### Opcion 4: Desde el directorio scripts/bat
```bash
# Git Bash
cd scripts/bat
./run_coverage.bat

# CMD / PowerShell
cd scripts\bat
run_coverage.bat
```

#### ⚠️ Nota importante de rutas:
✅ En **Git Bash** usar siempre barras `/` y `./` al principio
✅ En **CMD / PowerShell** usar barras invertidas `\`
❌ Nunca mezclar ambos formatos

### 📋 Que hace exactamente:
1.  🧹 Elimina archivos `.coverage` y `coverage.xml` anteriores
2.  🚀 Ejecuta todos los tests con coverage habilitado
3.  📊 Muestra el reporte de cobertura en tiempo real
4.  📄 Genera el reporte XML compatible con SonarQube
5.  ✅ Finaliza con un mensaje de exito o error

### ⚠️ Nota importante:
Si ves el mensaje:
```
CoverageWarning: Module inspecciones_llm was never imported.
```

✅ **ESTO ES NORMAL Y BUENA SEÑAL**:
Significa que coverage **ya detecto correctamente el modulo inspecciones_llm, solo que aun ningun test lo importa. Aun asi ya esta incluido en el calculo total y aparecera en el reporte en cuanto se agregue un test que lo importe.

---

## 🔧 Configuracion actual:
El coverage ya esta configurado para incluir SIEMPRE `inspecciones_llm` incluso aunque no tenga ningun test aun.

---

## 📌 Ubicacion:
```
📂 scripts/
└── 📂 bat/
    ├── 📜 run_coverage.bat       <-- ESTE ARCHIVO
    └── 📜 README.md
```

---

Ultima actualizacion: 22/04/2026