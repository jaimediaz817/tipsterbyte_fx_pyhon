# Guía de Inicialización del Proyecto desde Cero

Sigue estos pasos en orden para configurar completamente el entorno de desarrollo local después de un reseteo o una clonación inicial.

---

### **Paso 0: Prerrequisito - Docker**

Asegúrate de que los contenedores de las bases de datos (PostgreSQL y MongoDB) estén en ejecución.

*   **Ubicación:** Raíz del proyecto (donde se encuentra `docker-compose.yml`).
*   **Comando:**
    ```bash
    docker-compose up -d
    ```

---

### **Paso 1: Diagnóstico Inicial**

Utiliza el comando de estado para verificar la configuración actual y determinar el primer paso necesario.

*   **Ubicación:** Carpeta `backend/`.
*   **Comando:**
    ```bash
    python manage.py project status
    ```
    *La salida te guiará al siguiente paso lógico, que probablemente será crear las migraciones SQL.*

---

### **Paso 2: Inicialización de PostgreSQL (SQL)**

Este proceso consta de tres fases: crear el archivo de migración, aplicarlo a la base de datos y poblarla con datos iniciales.

1.  **Crear la Migración Inicial**
    *Genera el archivo de migración basado en los modelos SQL definidos en el código.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py sql create-migration -m "initial project structure"
        ```

2.  **Aplicar la Migración a la Base de Datos**
    *Ejecuta el script de migración para crear todas las tablas, índices y relaciones en la base de datos PostgreSQL.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py sql migrate
        ```

3.  **Poblar la Base de Datos (Seeders)**
    *Inserta los datos iniciales necesarios para el funcionamiento de la aplicación (roles, usuarios por defecto, etc.).*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py seed-sql
        ```

---

### **Paso 3: Inicialización de MongoDB (NoSQL)**

Este proceso inicializa el esquema creando las colecciones e índices necesarios.

1.  **Inicializar el Esquema NoSQL**
    *Crea las colecciones e índices en MongoDB basados en los modelos de Beanie.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py nosql init-schema
        ```

2.  **(Opcional) Poblar la Base de Datos NoSQL**
    *Si existen seeders para MongoDB, ejecútalos para insertar datos iniciales.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py nosql seed
        ```

---

### **Paso 4: Verificación Final y Arranque**

1.  **Verificar el Estado del Proyecto**
    *Ejecuta el comando de estado una última vez. Debería confirmar que todo está configurado correctamente.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py project status
        ```
    *Si la salida es `🎉 ¡El proyecto está completamente configurado y listo para funcionar!`, puedes continuar.*

2.  **Iniciar el Servidor**
    *Levanta el servidor de la aplicación FastAPI.*
    *   **Ubicación:** Carpeta `backend/`.
    *   **Comando:**
        ```bash
        python manage.py server run
        ```