# 🎯 PLAN PRE-FASE 6: Sistema de Exportación/Importación de Logs

**Fecha:** 2026-03-22
**Estado:** EN ANÁLISIS
**Problema:** Tablas `process_run` y `process_run_logs` crecen sin control (7,254+ registros)

---

## 📋 **CONTEXTO Y PROBLEMA**

### **Situación Actual:**
- Tabla `process_run_logs`: **7,254 registros** y creciendo
- Cada ejecución del scheduler genera **~15-21 logs** (3 robots × 5-7 logs cada uno)
- Scheduler cada minuto: **900-1,260 logs/hora** → **21,600-30,240 logs/día**
- Proyección mensual: **~750,000 logs** en producción

### **Problema de Eliminar Logs:**
- ❌ **Pérdida de trazabilidad histórica**
- ❌ **Imposible rastrear problemas pasados**
- ❌ **Pérdida de datos para auditoría**
- ❌ **Incumplimiento de posibles requerimientos de compliance**

### **Solución Propuesta:**
✅ **Exportar a CSV antes de limpiar** → **Importar desde CSV cuando se necesite**

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **Flujo de Datos:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   BD Principal  │───▶│  Exportar CSV    │───▶│  Archivo CSV    │
│ (process_runs,  │    │  (logs antiguos) │    │  (histórico)    │
│  process_run_   │    └──────────────────┘    └─────────────────┘
│  logs)          │                                      │
└─────────────────┘                                      │
         ▲                                               │
         │            ┌──────────────────┐              │
         └────────────│  Importar CSV    │◀─────────────┘
                      │  (consultar      │
                      │   histórico)     │
                      └──────────────────┘
```

### **Componentes:**

#### **1. Exportador CSV (`LogCSVExporter`)**
- Exporta `process_runs` y `process_run_logs` a CSV
- Mantiene relaciones entre tablas
- Genera archivos con timestamp
- Comprime archivos antiguos (gzip)

#### **2. Importador CSV (`LogCSVImporter`)**
- Importa desde CSV a BD
- Verifica IDs existentes (evita duplicados)
- Mantiene integridad referencial
- Validación de datos

#### **3. Gestor de Archivos (`LogArchiveManager`)**
- Organiza archivos por fecha
- Limpia archivos antiguos
- Comprime archivos grandes
- Indexa para búsqueda rápida

#### **4. Servicio de Retención (`LogRetentionService`)**
- Coordina exportación + limpieza
- Configuración por ambiente
- Monitoreo de crecimiento

---

## 📊 **ESTRUCTURA DE ARCHIVOS CSV**

### **Archivo: `process_runs_YYYY-MM-DD.csv`**
```csv
id,run_id,process_id,status,started_at,ended_at
1,run-001,1,success,2026-03-22 10:00:00,2026-03-22 10:05:00
2,run-002,1,failed,2026-03-22 11:00:00,2026-03-22 11:03:00
```

### **Archivo: `process_run_logs_YYYY-MM-DD.csv`**
```csv
id,run_id,step,level,message,input,output,timestamp
1,run-001,START,info,Iniciando robot,url=http://example.com,,2026-03-22 10:00:00
2,run-001,SCRAPING,info,Extrayendo datos,,data=123,2026-03-22 10:01:00
3,run-001,END,info,Robot completado,,,2026-03-22 10:05:00
```

### **Estructura de Directorios:**
```
backend/data/logs_archive/
├── 2026-03/
│   ├── process_runs_2026-03-22.csv
│   ├── process_run_logs_2026-03-22.csv
│   ├── process_runs_2026-03-21.csv.gz
│   └── process_run_logs_2026-03-21.csv.gz
├── 2026-02/
│   └── ...
└── index.json  # Índice de archivos disponibles
```

---

## 🔧 **IMPLEMENTACIÓN TÉCNICA**

### **1. Exportador CSV**

```python
# backend/core/services/log_csv_exporter.py
import csv
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from loguru import logger

class LogCSVExporter:
    """Exporta logs antiguos a archivos CSV."""
    
    def __init__(self, db: Session, archive_dir: str = "data/logs_archive"):
        self.db = db
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def export_old_logs(self, days: int = 7) -> dict:
        """
        Exporta logs más antiguos que 'days' días a CSV.
        
        Returns:
            dict: Estadísticas de exportación
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        logger.info(f"📤 Exportando logs anteriores a {cutoff_date.date()}...")
        
        # 1. Exportar process_runs
        runs_exported = self._export_process_runs(cutoff_date)
        
        # 2. Exportar process_run_logs
        logs_exported = self._export_process_run_logs(cutoff_date)
        
        # 3. Comprimir archivos antiguos
        self._compress_old_files()
        
        # 4. Actualizar índice
        self._update_index()
        
        stats = {
            "runs_exported": runs_exported,
            "logs_exported": logs_exported,
            "cutoff_date": cutoff_date.isoformat(),
            "archive_dir": str(self.archive_dir)
        }
        
        logger.success(
            f"✅ Exportación completada: "
            f"{runs_exported} runs, {logs_exported} logs"
        )
        
        return stats
    
    def _export_process_runs(self, cutoff_date: datetime) -> int:
        """Exporta process_runs antiguos a CSV."""
        from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
        
        # Obtener runs antiguos
        old_runs = self.db.query(ProcessRun).filter(
            ProcessRun.started_at < cutoff_date
        ).all()
        
        if not old_runs:
            logger.info("No hay process_runs antiguos para exportar")
            return 0
        
        # Crear archivo CSV
        date_str = cutoff_date.strftime("%Y-%m-%d")
        filename = f"process_runs_{date_str}.csv"
        filepath = self.archive_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'run_id', 'process_id', 'status', 
                'started_at', 'ended_at'
            ])
            
            for run in old_runs:
                writer.writerow([
                    run.id,
                    run.run_id,
                    run.process_id,
                    run.status,
                    run.started_at.isoformat() if run.started_at else None,
                    run.ended_at.isoformat() if run.ended_at else None
                ])
        
        logger.info(f"📁 Exportados {len(old_runs)} process_runs a {filename}")
        return len(old_runs)
    
    def _export_process_run_logs(self, cutoff_date: datetime) -> int:
        """Exporta process_run_logs antiguos a CSV."""
        from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
        
        # Obtener logs antiguos
        old_logs = self.db.query(ProcessRunLog).filter(
            ProcessRunLog.timestamp < cutoff_date
        ).all()
        
        if not old_logs:
            logger.info("No hay process_run_logs antiguos para exportar")
            return 0
        
        # Crear archivo CSV
        date_str = cutoff_date.strftime("%Y-%m-%d")
        filename = f"process_run_logs_{date_str}.csv"
        filepath = self.archive_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'run_id', 'step', 'level', 'message',
                'input', 'output', 'timestamp'
            ])
            
            for log in old_logs:
                writer.writerow([
                    log.id,
                    log.run_id,
                    log.step,
                    log.level,
                    log.message,
                    log.input,
                    log.output,
                    log.timestamp.isoformat() if log.timestamp else None
                ])
        
        logger.info(f"📁 Exportados {len(old_logs)} process_run_logs a {filename}")
        return len(old_logs)
    
    def _compress_old_files(self):
        """Comprime archivos CSV antiguos para ahorrar espacio."""
        for csv_file in self.archive_dir.glob("*.csv"):
            # Comprimir archivos de más de 7 días
            file_age = datetime.now() - datetime.fromtimestamp(csv_file.stat().st_mtime)
            if file_age.days > 7:
                gz_file = csv_file.with_suffix('.csv.gz')
                with open(csv_file, 'rb') as f_in:
                    with gzip.open(gz_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                csv_file.unlink()  # Eliminar archivo original
                logger.debug(f"🗜️ Comprimido: {csv_file.name} → {gz_file.name}")
    
    def _update_index(self):
        """Actualiza el índice de archivos disponibles."""
        index_file = self.archive_dir / "index.json"
        
        # Escanear archivos disponibles
        files = []
        for file in self.archive_dir.glob("*.csv*"):
            stat = file.stat()
            files.append({
                "filename": file.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "compressed": file.suffix == '.gz'
            })
        
        # Guardar índice
        import json
        with open(index_file, 'w') as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "total_files": len(files),
                "files": sorted(files, key=lambda x: x["modified"], reverse=True)
            }, f, indent=2)
```

### **2. Importador CSV**

```python
# backend/core/services/log_csv_importer.py
import csv
import gzip
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from loguru import logger

class LogCSVImporter:
    """Importa logs desde archivos CSV a la base de datos."""
    
    def __init__(self, db: Session, archive_dir: str = "data/logs_archive"):
        self.db = db
        self.archive_dir = Path(archive_dir)
    
    def import_logs(self, filename: str, verify_ids: bool = True) -> dict:
        """
        Importa logs desde un archivo CSV.
        
        Args:
            filename: Nombre del archivo CSV
            verify_ids: Si verificar IDs existentes (evita duplicados)
        
        Returns:
            dict: Estadísticas de importación
        """
        filepath = self.archive_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {filepath}")
        
        logger.info(f"📥 Importando logs desde {filename}...")
        
        # Determinar tipo de archivo
        if "process_runs" in filename:
            stats = self._import_process_runs(filepath, verify_ids)
        elif "process_run_logs" in filename:
            stats = self._import_process_run_logs(filepath, verify_ids)
        else:
            raise ValueError(f"Tipo de archivo no reconocido: {filename}")
        
        logger.success(f"✅ Importación completada: {stats}")
        return stats
    
    def _import_process_runs(self, filepath: Path, verify_ids: bool) -> dict:
        """Importa process_runs desde CSV."""
        from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
        
        imported = 0
        skipped = 0
        errors = 0
        
        # Leer archivo (soporta .gz)
        if filepath.suffix == '.gz':
            opener = gzip.open
        else:
            opener = open
        
        with opener(filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Verificar si ya existe
                    if verify_ids:
                        existing = self.db.query(ProcessRun).filter(
                            ProcessRun.run_id == row['run_id']
                        ).first()
                        
                        if existing:
                            skipped += 1
                            continue
                    
                    # Crear registro
                    run = ProcessRun(
                        run_id=row['run_id'],
                        process_id=int(row['process_id']),
                        status=row['status'],
                        started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
                        ended_at=datetime.fromisoformat(row['ended_at']) if row['ended_at'] else None
                    )
                    
                    self.db.add(run)
                    imported += 1
                    
                except Exception as e:
                    errors += 1
                    logger.error(f"Error importando run {row.get('run_id')}: {e}")
        
        self.db.commit()
        
        return {
            "type": "process_runs",
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }
    
    def _import_process_run_logs(self, filepath: Path, verify_ids: bool) -> dict:
        """Importa process_run_logs desde CSV."""
        from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
        
        imported = 0
        skipped = 0
        errors = 0
        
        # Leer archivo (soporta .gz)
        if filepath.suffix == '.gz':
            opener = gzip.open
        else:
            opener = open
        
        with opener(filepath, 'rt', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # Verificar si ya existe (por run_id + step + timestamp)
                    if verify_ids:
                        existing = self.db.query(ProcessRunLog).filter(
                            ProcessRunLog.run_id == row['run_id'],
                            ProcessRunLog.step == row['step'],
                            ProcessRunLog.timestamp == datetime.fromisoformat(row['timestamp'])
                        ).first()
                        
                        if existing:
                            skipped += 1
                            continue
                    
                    # Crear registro
                    log = ProcessRunLog(
                        run_id=row['run_id'],
                        step=row['step'],
                        level=row['level'],
                        message=row['message'],
                        input=row['input'] if row['input'] else None,
                        output=row['output'] if row['output'] else None,
                        timestamp=datetime.fromisoformat(row['timestamp']) if row['timestamp'] else None
                    )
                    
                    self.db.add(log)
                    imported += 1
                    
                except Exception as e:
                    errors += 1
                    logger.error(f"Error importando log {row.get('run_id')}: {e}")
        
        self.db.commit()
        
        return {
            "type": "process_run_logs",
            "imported": imported,
            "skipped": skipped,
            "errors": errors
        }
    
    def list_available_files(self) -> list:
        """Lista archivos CSV disponibles para importar."""
        index_file = self.archive_dir / "index.json"
        
        if not index_file.exists():
            return []
        
        import json
        with open(index_file, 'r') as f:
            data = json.load(f)
        
        return data.get("files", [])
```

### **3. Gestor de Archivos**

```python
# backend/core/services/log_archive_manager.py
from pathlib import Path
from datetime import datetime, timedelta
import json
from loguru import logger

class LogArchiveManager:
    """Gestiona archivos de logs archivados."""
    
    def __init__(self, archive_dir: str = "data/logs_archive"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def cleanup_old_archives(self, days: int = 90):
        """Elimina archivos de archivo más antiguos que 'days' días."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted_count = 0
        for file in self.archive_dir.glob("*.csv*"):
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                file.unlink()
                deleted_count += 1
                logger.debug(f"🗑️ Eliminado archivo antiguo: {file.name}")
        
        logger.info(f"🧹 Limpieza de archivos: {deleted_count} archivos eliminados")
        return deleted_count
    
    def get_archive_stats(self) -> dict:
        """Obtiene estadísticas de los archivos archivados."""
        total_size = 0
        file_count = 0
        oldest_file = None
        newest_file = None
        
        for file in self.archive_dir.glob("*.csv*"):
            stat = file.stat()
            total_size += stat.st_size
            file_count += 1
            
            mtime = datetime.fromtimestamp(stat.st_mtime)
            if oldest_file is None or mtime < oldest_file:
                oldest_file = mtime
            if newest_file is None or mtime > newest_file:
                newest_file = mtime
        
        return {
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "oldest_file": oldest_file.isoformat() if oldest_file else None,
            "newest_file": newest_file.isoformat() if newest_file else None
        }
```

### **4. Servicio de Retención Integrado**

```python
# backend/core/services/log_retention_service.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger

class LogRetentionService:
    """Servicio completo de retención de logs."""
    
    def __init__(self, db: Session, config: dict):
        self.db = db
        self.config = config
        
        # Inicializar componentes
        from .log_csv_exporter import LogCSVExporter
        from .log_csv_importer import LogCSVImporter
        from .log_archive_manager import LogArchiveManager
        
        self.exporter = LogCSVExporter(db, config.get("archive_dir", "data/logs_archive"))
        self.importer = LogCSVImporter(db, config.get("archive_dir", "data/logs_archive"))
        self.manager = LogArchiveManager(config.get("archive_dir", "data/logs_archive"))
    
    def run_retention_process(self):
        """
        Ejecuta proceso completo de retención:
        1. Exportar logs antiguos a CSV
        2. Eliminar logs antiguos de BD
        3. Limpiar archivos antiguos
        """
        logger.info("🔄 Iniciando proceso de retención de logs...")
        
        # 1. Exportar logs antiguos
        retention_days = self.config.get("retention_days", 7)
        export_stats = self.exporter.export_old_logs(days=retention_days)
        
        # 2. Eliminar logs antiguos de BD
        deleted_count = self._delete_old_logs_from_db(retention_days)
        
        # 3. Limpiar archivos antiguos
        archive_retention = self.config.get("archive_retention_days", 90)
        cleaned_count = self.manager.cleanup_old_archives(days=archive_retention)
        
        # 4. Obtener estadísticas finales
        final_stats = self.manager.get_archive_stats()
        
        logger.success(
            f"✅ Retención completada: "
            f"{export_stats['runs_exported']} runs exportados, "
            f"{export_stats['logs_exported']} logs exportados, "
            f"{deleted_count} logs eliminados de BD, "
            f"{cleaned_count} archivos limpiados"
        )
        
        return {
            "export": export_stats,
            "deleted_from_db": deleted_count,
            "files_cleaned": cleaned_count,
            "archive_stats": final_stats
        }
    
    def _delete_old_logs_from_db(self, days: int) -> int:
        """Elimina logs antiguos de la base de datos."""
        from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        deleted = self.db.query(ProcessRunLog).filter(
            ProcessRunLog.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted
    
    def search_logs_in_archive(self, query: dict) -> list:
        """
        Busca logs en archivos CSV.
        
        Args:
            query: Diccionario con criterios de búsqueda
                - run_id: str (opcional)
                - step: str (opcional)
                - level: str (opcional)
                - date_from: str (opcional, formato YYYY-MM-DD)
                - date_to: str (opcional, formato YYYY-MM-DD)
        
        Returns:
            list: Logs encontrados
        """
        results = []
        
        # Buscar en archivos CSV
        for file in self.importer.list_available_files():
            if file["compressed"]:
                continue  # Saltar archivos comprimidos por ahora
            
            file_results = self._search_in_file(file["filename"], query)
            results.extend(file_results)
        
        return results
    
    def _search_in_file(self, filename: str, query: dict) -> list:
        """Busca en un archivo CSV específico."""
        import csv
        from pathlib import Path
        
        filepath = self.manager.archive_dir / filename
        results = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                match = True
                
                # Filtrar por run_id
                if "run_id" in query and query["run_id"]:
                    if row.get("run_id") != query["run_id"]:
                        match = False
                
                # Filtrar por step
                if "step" in query and query["step"]:
                    if row.get("step") != query["step"]:
                        match = False
                
                # Filtrar por level
                if "level" in query and query["level"]:
                    if row.get("level") != query["level"]:
                        match = False
                
                # Filtrar por fecha
                if "date_from" in query and query["date_from"]:
                    log_date = row.get("timestamp", "")[:10]  # YYYY-MM-DD
                    if log_date < query["date_from"]:
                        match = False
                
                if "date_to" in query and query["date_to"]:
                    log_date = row.get("timestamp", "")[:10]
                    if log_date > query["date_to"]:
                        match = False
                
                if match:
                    results.append(row)
        
        return results
```

---

## 🖥️ **COMANDOS CLI**

### **Comando Principal: `manage_logs`**

```python
# backend/commands/db/admin/manage_logs.py
import click
from core.db.sql.database_sql import SessionLocal
from core.services.log_retention_service import LogRetentionService
from core.config_environments import EnvironmentConfig

@click.group()
def manage_logs():
    """Gestiona logs de procesos (exportar, importar, limpiar)."""
    pass

@manage_logs.command()
@click.option('--days', default=7, help='Días de retención')
@click.option('--archive-dir', default='data/logs_archive', help='Directorio de archivos')
def export(days: int, archive_dir: str):
    """Exporta logs antiguos a CSV."""
    with SessionLocal() as session:
        config = EnvironmentConfig()
        service = LogRetentionService(session, {
            "archive_dir": archive_dir,
            "retention_days": days
        })
        
        stats = service.exporter.export_old_logs(days=days)
        click.echo(f"✅ Exportación completada: {stats}")

@manage_logs.command()
@click.argument('filename')
@click.option('--verify-ids/--no-verify-ids', default=True, help='Verificar IDs existentes')
def import_logs(filename: str, verify_ids: bool):
    """Importa logs desde CSV a BD."""
    with SessionLocal() as session:
        config = EnvironmentConfig()
        service = LogRetentionService(session, {
            "archive_dir": "data/logs_archive"
        })
        
        stats = service.importer.import_logs(filename, verify_ids=verify_ids)
        click.echo(f"✅ Importación completada: {stats}")

@manage_logs.command()
@click.option('--days', default=7, help='Días de retención')
@click.option('--archive-days', default=90, help='Días de retención de archivos')
def cleanup(days: int, archive_days: int):
    """Ejecuta limpieza completa (exportar + eliminar + limpiar archivos)."""
    with SessionLocal() as session:
        config = EnvironmentConfig()
        service = LogRetentionService(session, {
            "archive_dir": "data/logs_archive",
            "retention_days": days,
            "archive_retention_days": archive_days
        })
        
        stats = service.run_retention_process()
        click.echo(f"✅ Limpieza completada: {stats}")

@manage_logs.command()
def list():
    """Lista archivos CSV disponibles."""
    with SessionLocal() as session:
        config = EnvironmentConfig()
        service = LogRetentionService(session, {
            "archive_dir": "data/logs_archive"
        })
        
        files = service.importer.list_available_files()
        
        if not files:
            click.echo("No hay archivos disponibles")
            return
        
        click.echo(f"📁 Archivos disponibles ({len(files)}):")
        for file in files:
            size_mb = file['size_bytes'] / (1024 * 1024)
            click.echo(f"  - {file['filename']} ({size_mb:.2f} MB, {file['modified']})")

@manage_logs.command()
@click.option('--run-id', help='Buscar por run_id')
@click.option('--step', help='Buscar por step')
@click.option('--level', help='Buscar por level')
@click.option('--date-from', help='Fecha desde (YYYY-MM-DD)')
@click.option('--date-to', help='Fecha hasta (YYYY-MM-DD)')
def search(run_id: str, step: str, level: str, date_from: str, date_to: str):
    """Busca logs en archivos CSV."""
    with SessionLocal() as session:
        config = EnvironmentConfig()
        service = LogRetentionService(session, {
            "archive_dir": "data/logs_archive"
        })
        
        query = {}
        if run_id:
            query["run_id"] = run_id
        if step:
            query["step"] = step
        if level:
            query["level"] = level
        if date_from:
            query["date_from"] = date_from
        if date_to:
            query["date_to"] = date_to
        
        results = service.search_logs_in_archive(query)
        
        if not results:
            click.echo("No se encontraron resultados")
            return
        
        click.echo(f"🔍 Encontrados {len(results)} resultados:")
        for result in results[:10]:  # Mostrar solo primeros 10
            click.echo(f"  [{result.get('timestamp')}] {result.get('run_id')} - {result.get('step')}: {result.get('message')}")
        
        if len(results) > 10:
            click.echo(f"  ... y {len(results) - 10} resultados más")

if __name__ == '__main__':
    manage_logs()
```

---

## 📅 **CONFIGURACIÓN POR AMBIENTE**

### **`.env.local`**
```env
# Logs
LOG_RETENTION_DAYS=3
LOG_ARCHIVE_RETENTION_DAYS=30
LOG_ARCHIVE_DIR=data/logs_archive
AUTO_CLEANUP_ENABLED=false

# Scheduler
SCHEDULER_ENABLED=false
```

### **`.env.staging`**
```env
# Logs
LOG_RETENTION_DAYS=7
LOG_ARCHIVE_RETENTION_DAYS=60
LOG_ARCHIVE_DIR=data/logs_archive
AUTO_CLEANUP_ENABLED=true
CLEANUP_CRON="0 3 * * 0"  # Domingos a 3 AM

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=5
```

### **`.env.production`**
```env
# Logs
LOG_RETENTION_DAYS=30
LOG_ARCHIVE_RETENTION_DAYS=180
LOG_ARCHIVE_DIR=/var/log/tipsterbyte/archive
AUTO_CLEANUP_ENABLED=true
CLEANUP_CRON="0 2 * * *"  # Diario a 2 AM

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=1
```

---

## 🧪 **TESTS UNITARIOS**

```python
# backend/core/tests/test_log_retention.py
import pytest
from unittest.mock import MagicMock, patch
from core.services.log_csv_exporter import LogCSVExporter
from core.services.log_csv_importer import LogCSVImporter

class TestLogCSVExporter:
    """Tests para el exportador CSV."""
    
    def test_export_old_logs(self, tmp_path):
        """✅ Exporta logs antiguos correctamente."""
        # Arrange
        mock_db = MagicMock()
        exporter = LogCSVExporter(mock_db, str(tmp_path))
        
        # Act
        stats = exporter.export_old_logs(days=7)
        
        # Assert
        assert "runs_exported" in stats
        assert "logs_exported" in stats

class TestLogCSVImporter:
    """Tests para el importador CSV."""
    
    def test_import_logs_verify_ids(self, tmp_path):
        """✅ Importa logs verificando IDs."""
        # Arrange
        mock_db = MagicMock()
        importer = LogCSVImporter(mock_db, str(tmp_path))
        
        # Crear archivo CSV de prueba
        csv_file = tmp_path / "process_runs_test.csv"
        csv_file.write_text("id,run_id,process_id,status,started_at,ended_at\n1,run-001,1,success,2026-03-22T10:00:00,2026-03-22T10:05:00")
        
        # Act
        stats = importer.import_logs("process_runs_test.csv", verify_ids=True)
        
        # Assert
        assert stats["imported"] == 1
        assert stats["skipped"] == 0
```

---

## 📊 **MÉTRICAS Y MONITOREO**

### **Dashboard de Retención:**
```python
# backend/core/services/retention_metrics.py
class RetentionMetrics:
    """Métricas de retención de logs."""
    
    @staticmethod
    def get_retention_dashboard(db: Session) -> dict:
        """Obtiene dashboard completo de retención."""
        from apps.platform_config.infrastructure.models.sql.process_run import ProcessRun
        from apps.platform_config.infrastructure.models.sql.process_run_log import ProcessRunLog
        
        # Contar registros actuales
        total_runs = db.query(ProcessRun).count()
        total_logs = db.query(ProcessRunLog).count()
        
        # Calcular crecimiento diario
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        
        logs_yesterday = db.query(ProcessRunLog).filter(
            ProcessRunLog.timestamp >= yesterday
        ).count()
        
        # Estadísticas de archivos
        from .log_archive_manager import LogArchiveManager
        manager = LogArchiveManager()
        archive_stats = manager.get_archive_stats()
        
        return {
            "current": {
                "total_runs": total_runs,
                "total_logs": total_logs,
                "logs_last_24h": logs_yesterday
            },
            "archive": archive_stats,
            "growth_rate": {
                "logs_per_day": logs_yesterday,
                "projected_monthly": logs_yesterday * 30
            }
        }
```

---

## 🚀 **PLAN DE IMPLEMENTACIÓN**

### **Fase Pre-6.1: Sistema de Exportación** (2-3 días)
1. Crear `LogCSVExporter`
2. Implementar exportación de `process_runs`
3. Implementar exportación de `process_run_logs`
4. Compresión de archivos antiguos
5. Tests unitarios

### **Fase Pre-6.2: Sistema de Importación** (2-3 días)
1. Crear `LogCSVImporter`
2. Importación con verificación de IDs
3. Validación de integridad referencial
4. Búsqueda en archivos CSV
5. Tests unitarios

### **Fase Pre-6.3: Gestión de Archivos** (1-2 días)
1. Crear `LogArchiveManager`
2. Limpieza de archivos antiguos
3. Índice de archivos disponibles
4. Estadísticas de almacenamiento

### **Fase Pre-6.4: Integración y CLI** (1-2 días)
1. Crear `LogRetentionService`
2. Comandos CLI (`manage_logs`)
3. Configuración por ambiente
4. Dashboard de métricas

### **Fase Pre-6.5: Documentación y Testing** (1 día)
1. Documentación de uso
2. Tests de integración
3. Guía de migración

---

## ✅ **BENEFICIOS ESPERADOS**

1. **✅ Trazabilidad Histórica**: Logs preservados en CSV
2. **✅ Sin Pérdida de Datos**: Importación cuando se necesite
3. **✅ BD Optimizada**: Solo logs recientes en BD activa
4. **✅ Búsqueda Rápida**: Índice de archivos CSV
5. **✅ Compresión**: Archivos .gz para ahorrar espacio
6. **✅ Auditoría**: Histórico completo disponible
7. **✅ Producción Estable**: Crecimiento controlado

---

## 📝 **EJEMPLO DE USO**

### **Exportar logs antiguos:**
```bash
python -m commands.db.admin.manage_logs export --days 7
```

### **Importar logs para consulta:**
```bash
python -m commands.db.admin.manage_logs import process_run_logs_2026-03-15.csv
```

### **Buscar logs específicos:**
```bash
python -m commands.db.admin.manage_logs search --run-id run-001 --step SCRAPING
```

### **Limpieza completa:**
```bash
python -m commands.db.admin.manage_logs cleanup --days 7 --archive-days 90
```

---

## 🎯 **PRÓXIMO PASO**

Implementar **Fase Pre-6.1: Sistema de Exportación CSV**

Esto resolverá el problema de crecimiento sin perder trazabilidad histórica.