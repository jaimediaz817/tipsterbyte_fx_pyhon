

## COMANDOS API: WEB
- Levanta el servidor local

## COMANDOS PERSONALIZADOS:

- Correr comandos para poblar gestor de ligas:
python manage.py seed-sql LeaguesManagerSeeder
- Correr datos de auth con opción para actualizar de manera forzada cambios en algunos campos:
python manage.py seed-sql AuthSeeder --update


## ✅ SÍ, se ignoran completamente en pytest

pytest **NO los ejecuta** porque las funciones no empiezan con `test_`.

---

## 🚀 **Cómo Ejecutar Manualmente (Sin pytest)**

Simplemente ejecuta los scripts directamente con Python:

```bash
# Ejecutar prueba de flujo del scheduler
cd backend
python test_desk_scheduler_flow.py

# Ejecutar prueba de procesos concurrentes
cd backend
python test_concurrent_processes.py

# Ejecutar prueba de ejecución manual
cd backend
python test_manual_execution.py
```

---

## 📋 **Ejemplo de Ejecución**

```bash
PS C:\...\backend> python test_manual_execution.py

================================================================================
🧪 PRUEBA DE ESCRITORIO: EJECUCIÓN MANUAL DE PROCESOS
================================================================================

📋 PASO 1: Verificando imports...
   ✅ Todos los módulos se importan correctamente

📋 PASO 2: Verificando configuración...
   ✅ Robots registrados: 3
      - standings: 3 concurrencia
      - odds_wplay: 1 concurrencia
      - calendar: 2 concurrencia

📋 PASO 3: Ejecutando proceso manualmente...
   🚀 Proceso: PROCESS_STANDINGS_EXTRACTION
   ✅ Proceso ejecutado exitosamente en 1.60s

📋 PASO 4: Verificando que el servidor puede iniciar...
   ✅ FastAPI app importada correctamente
   ✅ Rutas registradas: 36

🎯 CONCLUSIÓN: La ejecución manual funciona correctamente
```

---

## 📊 **Resumen**

| Método             | Ejecución           | Propósito                        |
| ------------------ | ------------------- | -------------------------------- |
| `pytest`           | Tests automatizados | Verificar lógica automáticamente |
| `python script.py` | Scripts manuales    | Verificar flujo manualmente      |

**Los scripts de prueba son herramientas de desarrollo, no tests automatizados.**