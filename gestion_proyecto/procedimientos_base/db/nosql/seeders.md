## 📋 Lista Completa de Comandos Seed

### **Comandos SQL (PostgreSQL)**

**1. Ejecutar TODOS los seeders (en orden de dependencias):**
```bash
python manage.py sql seed
```

**2. Ejecutar seeder específico:**
```bash
# Seeder de Platform Config (PRIORIDAD 0 - se ejecuta primero)
python manage.py sql seed PlatformConfigSeeder

# Seeder de Autenticación (PRIORIDAD 1)
python manage.py sql seed AuthSeeder

# Seeder de Leagues Manager (PRIORIDAD 2 - depende de PlatformConfig)
python manage.py sql seed LeaguesManagerSeeder
```

**3. Forzar actualización de registros existentes:**
```bash
python manage.py sql seed --update
python manage.py sql seed PlatformConfigSeeder --update
```

### **Comandos NoSQL (MongoDB)**

**4. Ejecutar seeder de MongoDB:**
```bash
python manage.py nosql seed
```

### **Orden de Ejecución Recomendado**

```bash
# 1. Primero migrar la base de datos
python manage.py sql migrate

# 2. Ejecutar seeders SQL (en orden automático)
python manage.py sql seed

# 3. Ejecutar seeder MongoDB (opcional)
python manage.py nosql seed
```

### **¿Qué puebla cada seeder?**

| Seeder                   | Contenido                                            |
| ------------------------ | ---------------------------------------------------- |
| **PlatformConfigSeeder** | Procesos, procesos programados (SCHEDULED_PROCESSES) |
| **AuthSeeder**           | Roles, usuario administrador                         |
| **LeaguesManagerSeeder** | Ligas, torneos, fuentes de extracción                |
| **MongoDB Seeder**       | Datos de ejemplo para MongoDB                        |

### **Verificar Estado Después de Seeders**
```bash
python manage.py sql state stats
```

**Esta documentación debería estar en el README.md del proyecto para mejorar la usabilidad.**