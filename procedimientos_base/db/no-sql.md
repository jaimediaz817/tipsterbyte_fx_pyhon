He demostrado el uso completo de los comandos de backup y restore de MongoDB. Aquí está el resumen:

## **Comandos ejecutados:**

### **1. Ver ayuda del comando restore:**
```bash
cd backend; python manage.py nosql state restore --help
```

**Salida:**
```
Usage: manage.py nosql state restore [OPTIONS]

Restaura la BD MongoDB desde un backup ejecutando mongorestore.
Ejemplo de uso:
    python manage.py nosql state restore --file backups/mongo_backups/backup_mibd_20240610_120000.gz

Options:
  --file, -f PATH  Ruta opcional al archivo de backup de MongoDB a restaurar.
  --help           Show this message and exit.
```

### **2. Crear un backup:**
```bash
cd backend; python manage.py nosql state backup
```

**Formato del nombre del archivo generado:**
```
backup_tipsterbyte_fx_nosql_db_YYYYMMDD_HHMMSS.gz
```

Ejemplo: `backup_tipsterbyte_fx_nosql_db_20260323_153500.gz`

### **3. Restaurar un backup específico:**
```bash
cd backend; python manage.py nosql state restore --file backups\mongo_backups\backup_tipsterbyte_fx_nosql_db_20260323_153500.gz
```

### **4. Restaurar el último backup (sin especificar archivo):**
```bash
cd backend; python manage.py nosql state restore
```
*(Busca automáticamente el backup más reciente en `backups/mongo_backups/`)*

## **Flujo completo de trabajo:**

1. **Crear backup:** `python manage.py nosql state backup`
2. **Verificar backups:** `dir backups\mongo_backups`
3. **Restaurar backup específico:** `python manage.py nosql state restore --file backups\mongo_backups\backup_tipsterbyte_fx_nosql_db_20260323_153500.gz`
4. **Restaurar último backup:** `python manage.py nosql state restore`

**Nota:** Los comandos requieren que Docker esté corriendo con el contenedor de MongoDB activo.