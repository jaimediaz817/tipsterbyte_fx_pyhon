# ============================================================================
# CÓDIGOS DE PROCESOS - JERARQUÍA Y USO
# ============================================================================
#
# ARQUITECTURA:
# ┌─────────────────────────────────────────────────────────────────────┐
# │  PROCESS_EXTRACT_DATA_FUENTES (Orquestador General)                │
# │     │                                                               │
# │     ├── PROCESS_STANDINGS_EXTRACTION (Robot específico)            │
# │     ├── PROCESS_ODDS_WPLAY_EXTRACTION (Robot específico)           │
# │     └── PROCESS_CALENDAR_EXTRACTION (Robot específico)             │
# └─────────────────────────────────────────────────────────────────────┘
#
# USO:
# - PROCESS_EXTRACT_DATA_FUENTES: Ejecuta TODOS los robots (scheduler nocturno)
# - PROCESS_STANDINGS_EXTRACTION: Ejecuta SOLO standings (manual o scheduler)
# - PROCESS_ODDS_WPLAY_EXTRACTION: Ejecuta SOLO odds (manual o scheduler)
# - PROCESS_CALENDAR_EXTRACTION: Ejecuta SOLO calendar (manual o scheduler)
#
# FILTRADO:
# El orquestador usa DetalleFuenteExtraccion.process_id para filtrar:
# - Si process_code == PROCESS_EXTRACT_DATA_FUENTES → ejecuta TODOS
# - Si process_code == PROCESS_STANDINGS_EXTRACTION → filtra por process_id
# ============================================================================

# Proceso orquestador: ejecuta TODOS los robots de extracción
PROCESS_EXTRACT_DATA_FUENTES = "extract_data_fuentes"

# Procesos específicos: ejecutan UN solo tipo de robot
PROCESS_STANDINGS_EXTRACTION = "standings_extraction"
PROCESS_ODDS_WPLAY_EXTRACTION = "odds_wplay_extraction"
PROCESS_CALENDAR_EXTRACTION = "calendar_extraction"

# Proceso de limpieza de logs (independiente)
PROCESS_LOG_CLEANUP = "log_cleanup"
