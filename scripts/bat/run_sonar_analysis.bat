@echo off
REM ================================
REM SCRIPT DE ANÁLISIS SONARQUBE
REM Proyecto: TipsterByte FX
REM ================================

echo.
echo ========================================
echo  ANÁLISIS DE CALIDAD - SONARQUBE
echo ========================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "sonar-project.properties" (
    echo [ERROR] No se encontró sonar-project.properties
    echo [INFO] Ejecuta este script desde la raíz del proyecto
    pause
    exit /b 1
)

REM Verificar que Docker está corriendo
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no está corriendo o no tienes permisos
    echo [INFO] Inicia Docker Desktop y vuelve a intentar
    pause
    exit /b 1
)

echo [1/4] Verificando SonarQube en Docker...
docker ps | findstr sonarqube_tipsterbyte >nul
if errorlevel 1 (
    echo [INFO] Iniciando SonarQube...
    docker-compose up -d sonarqube
    echo [INFO] Esperando 30 segundos para que SonarQube inicie...
    timeout /t 30 /nobreak >nul
) else (
    echo [OK] SonarQube está corriendo
)

echo.
echo [2/4] Instalando dependencias de testing...
cd backend
pip install pytest-cov pytest-xdist -q
if errorlevel 1 (
    echo [ERROR] Falló la instalación de dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

echo.
echo [3/4] Ejecutando tests con coverage...
python -m pytest --cov --cov-config=.coveragerc --cov-report=xml:coverage.xml --junitxml=test-results.xml -v
if errorlevel 1 (
    echo [WARNING] Algunos tests fallaron, pero continuando con el análisis...
)
echo [OK] Tests ejecutados y coverage generado

echo.
echo [4/4] Ejecutando análisis de SonarQube...
cd ..

REM Usar ruta completa de sonar-scanner (ya instalado en C:\sonar-scanner)
set SONAR_SCANNER_PATH=C:\sonar-scanner\bin\sonar-scanner.bat

if not exist "%SONAR_SCANNER_PATH%" (
    echo [ERROR] No se encontró sonar-scanner en %SONAR_SCANNER_PATH%
    echo [INFO] Verifica que sonar-scanner esté instalado correctamente
    pause
    exit /b 1
)

if "%SONAR_TOKEN%"=="" (
    echo [WARNING] Variable SONAR_TOKEN no configurada
    echo [INFO] Genera un token en: http://localhost:9000/account/security
    echo [INFO] Luego ejecuta: set SONAR_TOKEN=tu_token_aqui
    echo.
    echo [INFO] Ejecutando análisis sin token (modo público)...
    "%SONAR_SCANNER_PATH%" "-Dsonar.host.url=http://localhost:9000"
) else (
    echo [INFO] Usando token de autenticación...
    echo [INFO] Token: %SONAR_TOKEN:~0,10%...
    "%SONAR_SCANNER_PATH%" "-Dsonar.token=%SONAR_TOKEN%" "-Dsonar.host.url=http://localhost:9000"
)

if errorlevel 1 (
    echo [ERROR] Falló el análisis de SonarQube
    echo [INFO] Verifica que SonarQube esté corriendo en http://localhost:9000
    pause
    exit /b 1
)

echo.
echo ========================================
echo  ANÁLISIS COMPLETADO EXITOSAMENTE
echo ========================================
echo.
echo [INFO] Dashboard: http://localhost:9000
echo [INFO] Proyecto: tipsterbyte_fx
echo.
pause