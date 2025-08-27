
-> empalme con apps, repasar estructura y enfocarnos en la ejecución de comandos, explicar la carpeta.



=============================
- Un poco sobre clean architecture:
Definición breve:
Arquitectura limpia separa el núcleo del negocio de los detalles externos. 
Las dependencias apuntan hacia el dominio, lo que permite probar, 
cambiar infraestructura o UI sin romper reglas de negocio.

Panorama general (capas y responsabilidades):
- Dominio: entidades, objetos de valor, reglas invariantes.
- Aplicación: casos de uso (comandos/queries), orquestación, puertos (interfaces).
- Infraestructura: implementaciones de puertos (adapters), DB, APIs, files, mensajes.
- Presentación: API/CLI/Jobs, validación superficial, mapeo request/response.

Estructura sugerida (ejemplo):
```
src/
    domain/
        entities/
        value-objects/
        services/
        repositories/   # interfaces
    application/
        use-cases/
        dto/
        ports/          # in/out
    infrastructure/
        persistence/    # orm/sql/nosql
        adapters/       # repo/http/cache
        mappers/
    presentation/
        api/
        controllers/
    config/
```

Diagrama en línea (dependencias hacia adentro):
```
[ Presentación ] ---> [ Aplicación ] ---> [ Dominio ]
                                                     ^                   ^
                                                     |                   |
                                 [ Infraestructura (Adapters->Ports, DB, APIs) ]
```

Transcripción para dibujar (paso a paso):
1) Dibuja tres cajas en línea: “Presentación”, “Aplicación”, “Dominio”.
2) Flecha de Presentación a Aplicación: “Controllers convierten HTTP/CLI a comandos/queries”.
3) Flecha de Aplicación a Dominio: “Casos de uso invocan entidades/servicios de dominio”.
4) Dibuja una caja bajo Aplicación llamada “Infraestructura”.
5) Flecha de Infraestructura hacia Aplicación: “Adapters implementan Ports (interfaces)”.
6) Anota en Aplicación: “Ports (interfaces)”.
7) Anota en Infraestructura: “Repositorios, HTTP clients, DB”.
8) Repite flechas entrando al Dominio: “Nunca depende de fuera”.
9) Cierra con el flujo: Request -> Controller -> UseCase -> Port -> Adapter -> DB -> UseCase -> Response.
- contar analogía de la cabina de un avión
TAREAS A LA MANO:
- Descargar docker desktop
- Comparar con otro proyecto para ejecutar el comando
- Correr docker-compose up
- Clonar el repositorio

ejecutar comandos NO SQL, Luego SQL
repasar tareas de la línea base realizadas y cosas que faltan
agregar al stage area de git elementos para interactuar con la rama



algunas conclusiones parciales y hablar del video #3
=============================