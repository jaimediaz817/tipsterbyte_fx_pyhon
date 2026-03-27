# Contexto de TipsterByte
- **Objetivo:** Plataforma de extracción, normalización y generación de parleys.
- **Stack:** Python 3.12, FastAPI, PostgreSQL (Docker), SonarQube.
- **Regla de Oro:** Todo código nuevo debe incluir tests (pytest) para subir ese 41% de coverage.
- **Geografía:** Usamos la API de restcountries.com para comenzar obteniendo paises y continentes y luego atacar ligas y tal, un breve ejemplo: https://restcountries.com/v3.1/all?fields=name,continents,region,subregion,cca2