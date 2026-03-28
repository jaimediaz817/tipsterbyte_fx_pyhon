# 🔍 DIAGNÓSTICO: Pruebas Unitarias para LigasSeeder

## 📋 Estado Actual

### ❌ **PROBLEMA IDENTIFICADO**
No existen pruebas unitarias para `LigasSeeder` antes de lanzar oficialmente el consumo de la API-Football (100 requests/día limitados).

---

## 🎯 **OBJETIVO**
Crear pruebas unitarias limpias, sin complicaciones y con criterios fuertes de diseño para validar el comportamiento del `LigasSeeder` **ANTES** de usar la API real.

---

## 📊 **ANÁLISIS DE COBERTURA ACTUAL**

### ✅ **Componentes con Tests:**
- `test_geografia_seeder.py` - ✅ Completo (4 tests)
- `conftest.py` - ✅ Configuración de fixtures

### ❌ **Componentes SIN Tests:**
- `LigasSeeder` - ❌ Sin cobertura
- `LigasSeeder._obtener_ligas_por_pais()` - ❌ Sin cobertura
- `LigasSeeder._procesar_liga()` - ❌ Sin cobertura

---

## 🏗️ **ARQUITECTURA DE PRUEBAS PROPUESTA**

### **Principios de Diseño:**
1. **AAA Pattern:** Arrange → Act → Assert
2. **Mocks aislados:** Solo mockear dependencias externas (HTTP, DB)
3. **Datos determinísticos:** Respuestas mockeadas consistentes
4. **Cobertura de casos:** Éxito, error, idempotencia, edge cases

### **Tests a Implementar:**

| Test                                     | Descripción                                | Prioridad |
| ---------------------------------------- | ------------------------------------------ | --------- |
| `test_obtener_ligas_por_pais_exitoso`    | Verifica obtención correcta de ligas       | 🔴 Alta    |
| `test_obtener_ligas_por_pais_error_http` | Verifica manejo de errores HTTP            | 🔴 Alta    |
| `test_procesar_liga_crea_nueva`          | Verifica creación de liga nueva            | 🔴 Alta    |
| `test_procesar_liga_actualiza_existente` | Verifica actualización de liga existente   | 🔴 Alta    |
| `test_run_procesa_multiples_paises`      | Verifica procesamiento de múltiples países | 🟡 Media   |
| `test_run_es_idempotente`                | Verifica que no duplica registros          | 🟡 Media   |
| `test_run_con_error_hace_rollback`       | Verifica rollback en caso de error         | 🔴 Alta    |
| `test_mapeo_tipo_liga`                   | Verifica mapeo "League"→"A", "Cup"→"B"     | 🟡 Media   |

---

## 🔧 **DATOS MOCK NECESARIOS**

### **Respuesta API-Football (mock):**
```python
MOCK_API_RESPONSE = [
    {
        "league": {
            "id": 140,
            "name": "La Liga",
            "type": "League",
            "logo": "https://media.api-sports.io/football/leagues/140.png"
        }
    },
    {
        "league": {
            "id": 141,
            "name": "Copa del Rey",
            "type": "Cup",
            "logo": "https://media.api-sports.io/football/leagues/141.png"
        }
    }
]
```

### **DTOs Mock:**
- `LigaDTO` con `id_api_externa`, `logo_url`, `tipo_liga`
- `PaisDTO` con `codigo_iso` válido

---

## 📝 **COMANDOS DE EJECUCIÓN**

```bash
# Ejecutar solo tests del LigasSeeder
pytest backend/apps/leagues_manager/tests/test_ligas_seeder.py -v

# Ejecutar con cobertura
pytest backend/apps/leagues_manager/tests/test_ligas_seeder.py --cov=scripts.db.seeders.sql.ligas_seeder

# Ejecutar todos los tests de seeders
pytest backend/apps/leagues_manager/tests/test_*_seeder.py -v
```

---

## ⚠️ **CONSIDERACIONES CRÍTICAS**

1. **NO usar API real en tests:** Todos los tests deben mockear `httpx.Client`
2. **NO escribir en DB:** Usar mocks de `Session` y `LeaguesService`
3. **Validar métricas:** Verificar contadores de creados/actualizados
4. **Validar rollback:** Asegurar que errores llamen a `db.rollback()`

---

## ✅ **CRITERIOS DE ACEPTACIÓN**

- [ ] Todos los tests pasan sin errores
- [ ] Cobertura ≥ 80% del código de `LigasSeeder`
- [ ] No hay llamadas a API real
- [ ] No hay escritura en DB
- [ ] Tests son idempotentes (se pueden ejecutar múltiples veces)
- [ ] Tests son rápidos (< 1 segundo total)