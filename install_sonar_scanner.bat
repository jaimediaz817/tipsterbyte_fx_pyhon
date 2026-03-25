@echo off
REM ================================
REM INSTALAR SONAR SCANNER
REM ================================

echo.
echo ========================================
echo  INSTALANDO SONAR SCANNER
echo ========================================
echo.

REM Verificar que PowerShell está disponible
where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell no está disponible
    pause
    exit /b 1
)

echo [INFO] Descargando Sonar Scanner...

REM Descargar sonar-scanner usando PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-windows-x64.zip' -OutFile 'sonar-scanner.zip'}"

if errorlevel 1 (
    echo [ERROR] Falló la descarga
    pause
    exit /b 1
)

echo [OK] Descarga completada
echo [INFO] Extrayendo...

REM Extraer usando PowerShell
powershell -Command "& {Expand-Archive -Path 'sonar-scanner.zip' -DestinationPath '.' -Force}"

if errorlevel 1 (
    echo [ERROR] Falló la extracción
    pause
    exit /b 1
)

echo [OK] Extracción completada

REM Mover a carpeta permanente
echo [INFO] Instalando en C:\sonar-scanner...
if exist "C:\sonar-scanner" rmdir /s /q "C:\sonar-scanner"
move sonar-scanner-cli-5.0.1.3006-windows-x64 C:\sonar-scanner

REM Agregar al PATH del usuario
echo [INFO] Configurando PATH...
setx PATH "%PATH%;C:\sonar-scanner\bin" /M

REM Limpiar
del sonar-scanner.zip

echo.
echo [OK] Sonar Scanner instalado exitosamente
echo.
echo [INFO] Verificando instalación...
C:\sonar-scanner\bin\sonar-scanner --version

echo.
echo ========================================
echo  INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo IMPORTANTE: Cierra y vuelve a abrir la terminal
echo para que los cambios en PATH surtan efecto
echo.
pause