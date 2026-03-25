@echo off
REM ================================
REM REPORTE DE COBERTURA DETALLADO
REM Proyecto: TipsterByte FX
REM ================================

echo.
echo ========================================
echo  REPORTE DE COBERTURA POR ARCHIVO
echo ========================================
echo.

REM Verificar que existe coverage.xml
if not exist "backend\coverage.xml" (
    echo [ERROR] No se encontro backend\coverage.xml
    echo [INFO] Ejecuta primero run_sonar_analysis.bat para generar el reporte
    pause
    exit /b 1
)

echo [INFO] Generando reporte detallado de cobertura...
echo.

python scripts\generate_coverage_report.py backend\coverage.xml

echo.
echo ========================================
echo  REPORTE COMPLETADO
echo ========================================
echo.
echo [INFO] Para ver el coverage interactivo en SonarQube:
echo   http://localhost:9000/dashboard?id=tipsterbyte_fx
echo.
pause