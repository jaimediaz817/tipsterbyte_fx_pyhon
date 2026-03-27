"""
Test de Integración: Analizador de Crecimiento de Logs
======================================================

Analiza los archivos de logs para identificar cuáles tienen actividad
y cuáles están estancados, útil para decidir cuáles deprecar/eliminar.

Uso:
    pytest backend/services/tests/test_log_growth_analyzer.py -v -s
"""

import os
import sys
import time as time_module
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import pytest

# Agregar directorio backend al path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from core.paths import LOGS_ROOT


@dataclass
class LogFileInfo:
    """Información de un archivo de log."""

    file_path: Path
    name: str
    initial_size_bytes: int = 0
    final_size_bytes: int = 0
    initial_mtime: float = 0.0
    final_mtime: float = 0.0
    growth_bytes: int = 0
    growth_percentage: float = 0.0
    days_since_last_modified: float = 0.0
    is_active: bool = False
    is_growing: bool = False
    category: str = "unknown"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": str(self.file_path),
            "initial_size_mb": round(self.initial_size_bytes / (1024 * 1024), 2),
            "final_size_mb": round(self.final_size_bytes / (1024 * 1024), 2),
            "growth_mb": round(self.growth_bytes / (1024 * 1024), 2),
            "growth_percentage": round(self.growth_percentage, 2),
            "days_since_modified": round(self.days_since_last_modified, 1),
            "is_active": self.is_active,
            "is_growing": self.is_growing,
            "category": self.category,
        }


@dataclass
class LogGrowthReport:
    """Reporte de análisis de crecimiento de logs."""

    analysis_start: datetime = field(default_factory=datetime.now)
    analysis_end: Optional[datetime] = None
    duration_seconds: float = 0.0
    total_files_analyzed: int = 0
    active_files: list[LogFileInfo] = field(default_factory=list)
    stagnant_files: list[LogFileInfo] = field(default_factory=list)
    growing_files: list[LogFileInfo] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "analysis_start": self.analysis_start.isoformat(),
            "analysis_end": (
                self.analysis_end.isoformat() if self.analysis_end else None
            ),
            "duration_seconds": round(self.duration_seconds, 2),
            "total_files_analyzed": self.total_files_analyzed,
            "active_files_count": len(self.active_files),
            "stagnant_files_count": len(self.stagnant_files),
            "growing_files_count": len(self.growing_files),
            "active_files": [f.to_dict() for f in self.active_files],
            "stagnant_files": [f.to_dict() for f in self.stagnant_files],
            "growing_files": [f.to_dict() for f in self.growing_files],
            "recommendations": self.recommendations,
        }

    def print_summary(self):
        """Imprime un resumen legible del reporte."""
        print("\n" + "=" * 80)
        print("REPORTE DE ANALISIS DE CRECIMIENTO DE LOGS")
        print("=" * 80)
        print(f"\nDuracion del analisis: {self.duration_seconds:.1f} segundos")
        print(f"Total archivos analizados: {self.total_files_analyzed}")
        print(f"Archivos activos (modificados recientemente): {len(self.active_files)}")
        print(f"Archivos en crecimiento: {len(self.growing_files)}")
        print(f"Archivos estancados (sin actividad): {len(self.stagnant_files)}")

        if self.growing_files:
            print("\nARCHIVOS EN CRECIMIENTO:")
            print("-" * 80)
            for f in sorted(
                self.growing_files, key=lambda x: x.growth_bytes, reverse=True
            ):
                print(f"  - {f.name}")
                print(
                    f"    Crecimiento: +{f.growth_bytes / (1024 * 1024):.2f} MB ({f.growth_percentage:.1f}%)"
                )
                print(
                    f"    Ultima modificacion: hace {f.days_since_last_modified:.1f} dias"
                )

        if self.stagnant_files:
            print("\nARCHIVOS ESTANCADOS (CANDIDATOS A DEPRECACION):")
            print("-" * 80)
            for f in sorted(
                self.stagnant_files,
                key=lambda x: x.days_since_last_modified,
                reverse=True,
            ):
                print(f"  - {f.name}")
                print(f"    Tamano: {f.final_size_bytes / (1024 * 1024):.2f} MB")
                print(
                    f"    Sin actividad desde hace: {f.days_since_last_modified:.1f} dias"
                )
                print(f"    Categoria: {f.category}")

        if self.active_files:
            print("\nARCHIVOS ACTIVOS:")
            print("-" * 80)
            for f in sorted(
                self.active_files, key=lambda x: x.final_size_bytes, reverse=True
            ):
                print(f"  - {f.name}")
                print(f"    Tamano: {f.final_size_bytes / (1024 * 1024):.2f} MB")
                print(
                    f"    Ultima modificacion: hace {f.days_since_last_modified:.1f} dias"
                )

        if self.recommendations:
            print("\nRECOMENDACIONES:")
            print("-" * 80)
            for rec in self.recommendations:
                print(f"  - {rec}")

        print("\n" + "=" * 80)


class LogGrowthAnalyzer:
    """
    Analizador de crecimiento de archivos de logs.

    Monitorea archivos de logs durante un período de tiempo
    para identificar cuáles tienen actividad y cuáles no.
    """

    def __init__(
        self,
        logs_dir: Optional[Path] = None,
        monitor_duration_seconds: float = 5.0,
        stagnant_threshold_days: float = 7.0,
        growth_threshold_bytes: int = 1024,  # 1 KB mínimo para considerar crecimiento
    ):
        self.logs_dir = logs_dir or LOGS_ROOT
        self.monitor_duration_seconds = monitor_duration_seconds
        self.stagnant_threshold_days = stagnant_threshold_days
        self.growth_threshold_bytes = growth_threshold_bytes
        self.log_files: dict[str, LogFileInfo] = {}

    def _categorize_log_file(self, file_path: Path) -> str:
        """Categoriza un archivo de log basado en su nombre y ubicación."""
        name = file_path.name.lower()

        if "general_app" in name:
            return "application"
        elif "system" in name:
            return "system"
        elif "robot" in name or "robots" in name:
            return "robot"
        elif "scheduler" in name:
            return "scheduler"
        elif "cleanup" in name:
            return "cleanup"
        elif ".zip" in name or ".gz" in name:
            return "archived"
        else:
            return "other"

    def _scan_log_files(self) -> dict[str, LogFileInfo]:
        """Escanea y recopila informacion inicial de todos los archivos de log."""
        log_files = {}

        if not self.logs_dir.exists():
            print(f"Directorio de logs no existe: {self.logs_dir}")
            return log_files

        for file_path in self.logs_dir.rglob("*"):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    info = LogFileInfo(
                        file_path=file_path,
                        name=file_path.name,
                        initial_size_bytes=stat.st_size,
                        final_size_bytes=stat.st_size,
                        initial_mtime=stat.st_mtime,
                        final_mtime=stat.st_mtime,
                        days_since_last_modified=(time_module.time() - stat.st_mtime)
                        / (24 * 3600),
                        category=self._categorize_log_file(file_path),
                    )
                    log_files[file_path.name] = info
                except (OSError, PermissionError) as e:
                    print(f"No se pudo acceder a {file_path.name}: {e}")

        return log_files

    def _update_file_info(self, info: LogFileInfo):
        """Actualiza la información de un archivo de log."""
        try:
            if info.file_path.exists():
                stat = info.file_path.stat()
                info.final_size_bytes = stat.st_size
                info.final_mtime = stat.st_mtime
                info.growth_bytes = info.final_size_bytes - info.initial_size_bytes

                if info.initial_size_bytes > 0:
                    info.growth_percentage = (
                        info.growth_bytes / info.initial_size_bytes
                    ) * 100

                info.days_since_last_modified = (time_module.time() - stat.st_mtime) / (
                    24 * 3600
                )

                # Clasificar archivo
                info.is_active = (
                    info.days_since_last_modified <= self.stagnant_threshold_days
                )
                info.is_growing = info.growth_bytes >= self.growth_threshold_bytes

        except (OSError, PermissionError):
            pass

    def analyze(self) -> LogGrowthReport:
        """
        Ejecuta el análisis de crecimiento de logs.

        Returns:
            LogGrowthReport con los resultados del análisis
        """
        report = LogGrowthReport()

        print(f"\nIniciando analisis de logs en: {self.logs_dir}")
        print(f"Duracion del monitoreo: {self.monitor_duration_seconds} segundos")
        print(f"Umbral de estancamiento: {self.stagnant_threshold_days} dias")
        print(f"Umbral de crecimiento: {self.growth_threshold_bytes} bytes")

        # Fase 1: Escaneo inicial
        print("\nFase 1: Capturando estado inicial...")
        self.log_files = self._scan_log_files()
        print(f"   Encontrados {len(self.log_files)} archivos de log")

        if not self.log_files:
            print("   No se encontraron archivos de log para analizar")
            report.analysis_end = datetime.now()
            return report

        # Fase 2: Monitoreo
        print(
            f"\nFase 2: Monitoreando durante {self.monitor_duration_seconds} segundos..."
        )
        time_module.sleep(self.monitor_duration_seconds)

        # Fase 3: Actualizacion y analisis
        print("\nFase 3: Analizando cambios...")
        for info in self.log_files.values():
            self._update_file_info(info)

        # Clasificar archivos
        for info in self.log_files.values():
            if info.is_growing:
                report.growing_files.append(info)
            elif info.is_active:
                report.active_files.append(info)
            else:
                report.stagnant_files.append(info)

        # Generar recomendaciones
        report.recommendations = self._generate_recommendations(report)

        # Finalizar reporte
        report.analysis_end = datetime.now()
        report.duration_seconds = (
            report.analysis_end - report.analysis_start
        ).total_seconds()
        report.total_files_analyzed = len(self.log_files)

        return report

    def _generate_recommendations(self, report: LogGrowthReport) -> list[str]:
        """Genera recomendaciones basadas en el analisis."""
        recommendations = []

        if report.stagnant_files:
            stagnant_names = [f.name for f in report.stagnant_files]
            recommendations.append(
                f"Considerar eliminar o deprecar {len(report.stagnant_files)} archivos "
                f"sin actividad: {', '.join(stagnant_names[:5])}"
                + ("..." if len(stagnant_names) > 5 else "")
            )

        if report.growing_files:
            total_growth_mb = sum(f.growth_bytes for f in report.growing_files) / (
                1024 * 1024
            )
            recommendations.append(
                f"{len(report.growing_files)} archivos estan creciendo activamente "
                f"(+{total_growth_mb:.2f} MB total). Considerar rotacion de logs."
            )

        # Verificar archivos muy grandes
        large_files = [
            f
            for f in report.active_files + report.growing_files
            if f.final_size_bytes > 50 * 1024 * 1024  # > 50 MB
        ]
        if large_files:
            recommendations.append(
                f"{len(large_files)} archivos superan 50 MB. "
                "Considerar compresion o archivado."
            )

        if not recommendations:
            recommendations.append("No se detectaron problemas evidentes en los logs.")

        return recommendations


class TestLogGrowthAnalyzer:
    """Tests para el analizador de crecimiento de logs."""

    def test_analyze_real_logs(self):
        """
        Test principal: Analiza los logs reales del proyecto.

        Este test monitorea los logs reales durante unos segundos
        para identificar cuales tienen actividad.
        """
        print("\n" + "=" * 80)
        print("TEST: Analisis de Crecimiento de Logs Reales")
        print("=" * 80)

        # Crear analizador con configuración para logs reales
        analyzer = LogGrowthAnalyzer(
            logs_dir=LOGS_ROOT,
            monitor_duration_seconds=5.0,  # Monitorear 5 segundos
            stagnant_threshold_days=7.0,  # 7 días sin actividad = estancado
            growth_threshold_bytes=1024,  # 1 KB mínimo para considerar crecimiento
        )

        # Ejecutar análisis
        report = analyzer.analyze()

        # Imprimir resumen
        report.print_summary()

        # Verificaciones basicas
        assert (
            report.total_files_analyzed > 0
        ), "No se encontraron archivos para analizar"
        assert report.analysis_end is not None, "El analisis no finalizo correctamente"
        assert report.duration_seconds > 0, "La duracion del analisis debe ser positiva"

        # Verificar que al menos tenemos categorizacion
        all_files = report.active_files + report.stagnant_files + report.growing_files
        assert (
            len(all_files) == report.total_files_analyzed
        ), "Todos los archivos deben estar categorizados"

        print("\nTEST COMPLETADO EXITOSAMENTE")
        print("=" * 80)

    def test_analyze_with_custom_directory(self, tmp_path):
        """
        Test con directorio temporal para pruebas controladas.
        """
        print("\n" + "=" * 80)
        print("TEST: Analisis con Directorio Temporal")
        print("=" * 80)

        # Crear archivos de log simulados
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()

        # Archivo activo (modificado recientemente)
        active_log = logs_dir / "active.log"
        active_log.write_text("Línea de log activa\n" * 100)

        # Archivo estancado (simular antigüedad)
        stagnant_log = logs_dir / "stagnant.log"
        stagnant_log.write_text("Log antiguo\n" * 50)
        old_time = time_module.time() - (30 * 24 * 3600)  # 30 días atrás
        os.utime(str(stagnant_log), (old_time, old_time))

        # Archivo en crecimiento
        growing_log = logs_dir / "growing.log"
        growing_log.write_text("Log inicial\n" * 10)

        # Crear analizador
        analyzer = LogGrowthAnalyzer(
            logs_dir=logs_dir,
            monitor_duration_seconds=2.0,
            stagnant_threshold_days=7.0,
        )

        # Simular crecimiento durante el monitoreo
        def simulate_growth():
            time_module.sleep(1)
            growing_log.write_text("Log expandido\n" * 100)

        import threading

        growth_thread = threading.Thread(target=simulate_growth)
        growth_thread.start()

        # Ejecutar análisis
        report = analyzer.analyze()
        growth_thread.join()

        # Verificaciones
        assert report.total_files_analyzed == 3
        report.print_summary()

        print("\nTEST COMPLETADO EXITOSAMENTE")
        print("=" * 80)


if __name__ == "__main__":
    # Ejecutar test manualmente
    pytest.main([__file__, "-v", "-s"])
