@echo off
cls

echo ==================================================
echo 🔍 EJECUTANDO COVERAGE COMPLETO TIPSTERBYTE FX
echo ==================================================
echo.

cd /d "%~dp0\..\..\backend"

echo 🧹 Borrando cache anterior de coverage...
if exist .coverage del /f /q .coverage
if exist coverage.xml del /f /q coverage.xml
echo.

echo 🚀 Ejecutando tests con coverage...
echo.
python -m coverage run -m pytest -xvs
echo.

if %errorlevel% equ 0 (
    echo ✅ Tests finalizados correctamente
    echo.
    echo 📊 Generando reporte de cobertura...
    echo.
    python -m coverage report
    echo.
    echo 📄 Generando archivo XML para SonarQube...
    python -m coverage xml
    echo.
    echo ✅ Coverage finalizado correctamente
) else (
    echo ❌ Error en la ejecucion de los tests
    exit /b 1
)

echo.
echo ==================================================
echo ✅ PROCESO TERMINADO
echo ==================================================
echo.
pause