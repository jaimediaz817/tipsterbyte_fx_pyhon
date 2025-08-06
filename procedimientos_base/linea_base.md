# HUS - TAREAS

## Objetivos Semanales: Checklist de Casos de Uso y Propuestas de Valor

A continuación se presentan los objetivos semanales organizados como checklist. Cada ítem representa un caso de uso o propuesta de valor a implementar:

### Semana 1 - FINAL JULIO

- [x] **Crear un script de migración de base de datos**  
    _Implementar un script que permita crear y aplicar migraciones a la base de datos utilizando Alembic._
- [x] **Organizar las bases SQL sueltas**  
    _Ubicar y estructurar los archivos SQL en la raíz de `core/db/sql/...` para mejorar la gestión y el acceso._

### Semana 2 - COMIENZO AGOSTO

04 AGOSTO

- [x] **Actualizar el README**  
    _Incluir instrucciones claras sobre cómo utilizar el script de migración y los comandos de gestión de base de datos._
- [x] **probar de nuevo los comandos en ambos motores de BD**
    _Verificar que los comandos de migración y gestión de base de datos funcionen correctamente tanto en PostgreSQL como en MongoDB._
- [ ] **Entender y aplicar cambios incrementales en la ejecución de procesos en paralelo**  
    _Investigar y aplicar técnicas para ejecutar procesos de migración y seeders de forma paralela,
     mejorando la eficiencia del sistema._
- [ ] **Entender y aplicar cambios incrementales en la ejecución de procesos en paralelo**
- [ ] **Scheduler de Scraper #1 fuente deportiva equipos por liga**
    _Implementar un sceduler responsable de llevar a cabo primer proceso de scraper que es consultar una web deportiva para saber que equipos ascienden y descienden, con ello de paso se busca autopoblar de paso las tablas pertinentes como país y equipos por liga de dicho páis._

> **Pautas para mantener este formato en Markdown:**
>
> - Utiliza listas de verificación (`- [ ]`) para marcar el progreso de cada objetivo.
> - Agrega descripciones breves para cada objetivo.
> - Organiza los objetivos por semana o sprint.
> - Actualiza el checklist conforme avances en cada tarea.
