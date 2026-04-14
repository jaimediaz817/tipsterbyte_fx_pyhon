# 📋 Inventario Tests Unitarios - Aplicación Template Estándar

> 📌 **OBLIGATORIO**: Todos los tests unitarios deben tener el template estándar aplicado. Este archivo sirve como registro de progreso y guía de implementación.

---

## ✅ Template Oficial Estándar para CUALQUIER Test Unitario

### 🚀 Cabecera Universal (Copiar y Pegar SIEMPRE)
```python
import sys
from pathlib import Path

# ✅ SOLUCION PERMANENTE PATH: Funciona en TODOS los entornos
ROOT_PROYECTO = Path(__file__).resolve().parents[3]
if str(ROOT_PROYECTO) not in sys.path:
    sys.path.insert(0, str(ROOT_PROYECTO))

# ✅ Cargar automaticamente variables de entorno
from dotenv import load_dotenv
load_dotenv(ROOT_PROYECTO / ".env")
```

### 📌 Reglas Invólucrables:
1. **SIEMPRE** es el PRIMER código despues de los imports
2. **NUNCA** modificar, ni adaptar, ni cambiar los números de parents
3. **NUNCA** usar `os.path.dirname()` anidados
4. **NUNCA** contar manualmente directorios

---

## 🧪 Comandos de Ejecución Manual

| Modo                     | Comando Exacto                      | Resultado Esperado                          |
| ------------------------ | ----------------------------------- | ------------------------------------------- |
| Ejecución individual     | `python ruta/al/archivo_test.py`    | ✅ Funciona desde CUALQUIER carpeta          |
| VS Code Testing Explorer | Boton Play ▶️                        | ✅ Se detecta y corre correctamente          |
| Pytest global            | `pytest backend/`                   | ✅ Corre todos los tests sin errores de path |
| Pytest especifico        | `pytest ruta/al/archivo_test.py -v` | ✅ Ejecucion verbosa                         |

---

## 📝 Procedimiento para aplicar el template a un test nuevo:

1. Abrir el archivo de test
2. Eliminar CUALQUIER codigo existente de path / sys.path
3. Pegar el template completo **arriba de TODO** despues de los imports
4. Guardar archivo
5. Verificar ejecutando manualmente: `python ruta/archivo.py`
6. Registrar aqui abajo en el listado

---

## 📊 Registro de Tests Procesados

| Estado  | Archivo                                                                 | Fecha Aplicación | Verificado Manual | Comando Ejecución                                                              |
| ------- | ----------------------------------------------------------------------- | ---------------- | ----------------- | ------------------------------------------------------------------------------ |
| ✅ LISTO | `backend/apps/platform_config/tests/test_vps_health_check_unit.py`      | 13/04/2026       | ✅ SI              | `python backend/apps/platform_config/tests/test_vps_health_check_unit.py`      |
| ✅ LISTO | `backend/apps/leagues_manager/tests/test_semaphore_singleton_visual.py` | 13/04/2026       | ✅ SI              | `python backend/apps/leagues_manager/tests/test_semaphore_singleton_visual.py` |

---

## 📈 Estadísticas de Progreso

```
✅ Aplicados: 2 / 1227
🔲 Pendientes: 1225
📊 Progreso: 0.16%
```

> 📌 Numero DEFINITIVO: Total de archivos test unitarios en carpetas `/tests/` : **1227 archivos**
> ✅ Filtrado correcto: Solo archivos dentro de carpetas llamadas `tests`, excluyendo __init__.py y __pycache__

---

## ❌ Errores Comunes a Evitar

| Error                                   | Solución                                               |
| --------------------------------------- | ------------------------------------------------------ |
| `ModuleNotFoundError`                   | Falta el template o esta mal colocado                  |
| Solo funciona en VS Code                | Verificar que el template es EXACTO sin modificaciones |
| No carga variables .env                 | Verificar ruta al .env en el template                  |
| Funciona desde una carpeta pero no otra | El template soluciona esto automaticamente             |