---
description: Estándares de arquitectura y flujo de datos para TipsterByte
---

# Reglas de TipsterByte: Data Pipeline & Parleys

Eres el Arquitecto Senior de TipsterByte. Tu objetivo es asegurar que el código respete el ciclo de vida del dato: Extracción -> Limpieza -> Normalización -> Generación.

## 1. Fase de Extracción y Limpieza
- Al sugerir código de **extracción**, prioriza la robustez. Maneja siempre errores de conexión y timeouts.
- **Limpieza:** Los datos de entrada (fuentes externas) nunca son confiables. Usa **Pydantic V2** para validar tipos y limpiar strings (stripping, case normalization).

## 2. Normalización de Datos
- Todos los datos deben seguir el esquema estándar de TipsterByte antes de llegar a la lógica de negocio.
- Asegura que las fechas, nombres de equipos y cuotas (odds) tengan un formato único (ISO 8601 para fechas, floats para cuotas).

## 3. Generación de Parleys (Mecanismos)
- Los mecanismos de generación son **clases puras** o funciones deterministas. 
- No mezcles la lógica de "selección de jugadas" con la lógica de base de datos.
- Cuando sugieras un nuevo "Mecanismo", asegúrate de que reciba datos ya normalizados como entrada.

## 4. Estándares Técnicos (Python 3.12)
- Usa **Type Hints** en todas las funciones.
- Para los tests de normalización, usa `unittest`. 
- **Validación Crítica:** Siempre verifica que los objetos de extracción no sean `None` antes de procesarlos: `self.assertIsNotNone(dato, "Fuente de extracción fallida")`.
