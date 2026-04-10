@echo off
REM ================================
REM ANÁLISIS COMPLETO SONARQUBE
REM Proyecto: TipsterByte FX
REM ================================

echo.
echo ========================================
echo  ANALISIS COMPLETO SONARQUBE
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

echo [1/6] Verificando SonarQube en Docker...
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
echo [2/6] Instalando dependencias de testing...
cd backend
pip install pytest-cov -q
if errorlevel 1 (
    echo [ERROR] Falló la instalación de dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

echo.
echo [3/6] Ejecutando tests con coverage...
python -m pytest --cov=apps --cov=core --cov=shared --cov-report=xml:coverage.xml --junitxml=test-results.xml -v
if errorlevel 1 (
    echo [WARNING] Algunos tests fallaron, pero continuando con el análisis...
)
echo [OK] Tests ejecutados y coverage generado

echo.
echo [4/6] Verificando sonar-scanner...
cd ..
set SONAR_SCANNER_PATH=C:\sonar-scanner\bin\sonar-scanner.bat

if not exist "%SONAR_SCANNER_PATH%" (
    echo [ERROR] No se encontró sonar-scanner en %SONAR_SCANNER_PATH%
    echo [INFO] Descarga desde: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
    pause
    exit /b 1
)
echo [OK] sonar-scanner encontrado en C:\sonar-scanner

echo.
echo [5/6] Configurando token y ejecutando análisis...

REM Verificar si ya existe un token configurado
if "%SONAR_TOKEN%"=="" goto NO_TOKEN
echo [INFO] Usando token de autenticación...
echo [INFO] Token: %SONAR_TOKEN:~0,10%...
"%SONAR_SCANNER_PATH%" -Dsonar.token=%SONAR_TOKEN% -Dsonar.host.url=http://localhost:9000
goto ANALYSIS_DONE

:NO_TOKEN
echo [WARNING] Variable SONAR_TOKEN no configurada
echo [INFO] Genera un token en: http://localhost:9000/account/security
echo [INFO] Luego ejecuta: set SONAR_TOKEN=tu_token_aqui
echo.
echo [INFO] Ejecutando análisis sin token (modo público)...
"%SONAR_SCANNER_PATH%" -Dsonar.host.url=http://localhost:9000

:ANALYSIS_DONE

if errorlevel 1 (
    echo [ERROR] Falló el análisis de SonarQube
    echo [INFO] Verifica que SonarQube esté corriendo en http://localhost:9000
    pause
    exit /b 1
)

echo.
echo [6/6] Abriendo dashboard...
echo [OK] Análisis completado exitosamente
echo.
echo ========================================
echo  ANALISIS COMPLETADO
echo ========================================
echo.
echo [INFO] Dashboard: http://localhost:9000
echo [INFO] Proyecto: tipsterbyte_fx
echo.
echo [INFO] Abriendo navegador...
start http://localhost:9000/dashboard?id=tipsterbyte_fx

echo.
echo ¡Listo! El análisis está completo y el dashboard se abrirá en tu navegador.
echo.
pause