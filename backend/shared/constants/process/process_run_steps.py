
# ============================================================
# PASOS ESTÁNDAR DE UN HILO DE EJECUCIÓN (process_run_log.step)
# ============================================================
# Cada constante representa un paso dentro de la ejecución de un
# hilo individual de scraping (un par torneo + detalle_fuente).
# Se usan en process_run_logs.step para garantizar valores uniformes
# y evitar strings libres que dificulten filtrado y auditoría.
# ============================================================


STEP_INIT = "STEP_INIT"
"""
Inicio del hilo.
Se registra al arrancar el procesamiento de un (torneo, detalle_fuente) concreto.
Confirma que el hilo fue creado y recibió sus parámetros correctamente.
"""

STEP_FETCH_URL = "STEP_FETCH_URL"
"""
Petición HTTP a la fuente externa.
Se registra al realizar la solicitud a la URL del detalle_fuente_extraccion.
En caso de error (timeout, 4xx, 5xx) el log quedará con level='error'.
"""

STEP_PARSE = "STEP_PARSE"
"""
Parseo del contenido recibido (HTML, JSON, etc).
Se registra tras recibir la respuesta y extraer los datos estructurados.
Un error aquí indica que la estructura de la fuente cambió o la respuesta es inesperada.
"""

STEP_VALIDATE = "STEP_VALIDATE"
"""
Validación de los datos extraídos antes de persistirlos.
Se verifica que los campos obligatorios existan y tengan el formato correcto.
Un error aquí no implica fallo de red, sino datos inconsistentes o incompletos.
"""

STEP_SAVE = "STEP_SAVE"
"""
Persistencia de los datos validados en la base de datos.
Se registra al ejecutar la escritura (INSERT / UPDATE) en las tablas destino.
Un error aquí puede indicar conflictos de FK, duplicados o problemas de transacción.
"""

STEP_COMPLETED = "STEP_COMPLETED"
"""
Finalización exitosa del hilo.
Se registra solo si todos los pasos anteriores terminaron sin errores críticos.
Su ausencia en el log de un run indica que el hilo no llegó a completarse.
"""
