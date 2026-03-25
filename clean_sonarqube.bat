@echo off
REM ================================
REM SCRIPT DE LIMPIEZA COMPLETA SONARQUBE
REM Proyecto: TipsterByte FX
REM ================================

echo.
echo ========================================
echo  LIMPIEZA COMPLETA DE SONARQUBE
echo ========================================
echo.

echo [1/6] Deteniendo SonarQube...
docker-compose --profile dev down sonarqube
if errorlevel 1 (
    echo [WARNING] Error al detener SonarQube, continuando...
) else (
    echo [OK] SonarQube detenido
)

echo.
echo [2/7] Eliminando contenedor de SonarQube...

echo [INFO] Eliminando contenedor sonarqube_tipsterbyte...
docker rm sonarqube_tipsterbyte -f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Contenedor no encontrado o ya eliminado
) else (
    echo [OK] Contenedor eliminado
)

echo.
echo [3/7] Eliminando imagenes de SonarQube...

echo [INFO] Eliminando imagen sonarqube:lta-community...
docker rmi sonarqube:lta-community -f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Imagen sonarqube:lta-community no encontrada
) else (
    echo [OK] Imagen sonarqube:lta-community eliminada
)

echo [INFO] Eliminando imagen sonarqube:10-community...
docker rmi sonarqube:10-community -f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Imagen sonarqube:10-community no encontrada
) else (
    echo [OK] Imagen sonarqube:10-community eliminada
)

echo [INFO] Eliminando imagen sonarqube:10.5.1-community...
docker rmi sonarqube:10.5.1-community -f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Imagen sonarqube:10.5.1-community no encontrada
) else (
    echo [OK] Imagen sonarqube:10.5.1-community eliminada
)

echo [INFO] Eliminando imagen sonarqube:community...
docker rmi sonarqube:community -f >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Imagen sonarqube:community no encontrada
) else (
    echo [OK] Imagen sonarqube:community eliminada
)

echo [INFO] Eliminando TODAS las imagenes de sonarqube...
for /f "tokens=3" %%i in ('docker images ^| findstr "sonarqube"') do docker rmi %%i -f >nul 2>&1
echo [OK] Proceso de eliminacion de imagenes completado

echo.
echo [4/7] Eliminando volumenes de SonarQube...

echo [INFO] Eliminando sonarqube_data...
docker volume rm tipsterbyte_fx_sonarqube_data -f
if errorlevel 1 (
    echo [WARNING] Volumen sonarqube_data no encontrado o en uso
) else (
    echo [OK] sonarqube_data eliminado
)

echo [INFO] Eliminando sonarqube_extensions...
docker volume rm tipsterbyte_fx_sonarqube_extensions -f
if errorlevel 1 (
    echo [WARNING] Volumen sonarqube_extensions no encontrado o en uso
) else (
    echo [OK] sonarqube_extensions eliminado
)

echo [INFO] Eliminando sonarqube_logs...
docker volume rm tipsterbyte_fx_sonarqube_logs -f
if errorlevel 1 (
    echo [WARNING] Volumen sonarqube_logs no encontrado o en uso
) else (
    echo [OK] sonarqube_logs eliminado
)

echo.
echo [5/7] Verificando PostgreSQL...
docker ps | findstr db_pg_tipsterbyte_fx_dev >nul
if errorlevel 1 (
    echo [WARNING] PostgreSQL no esta corriendo
    echo [INFO] Iniciando PostgreSQL...
    docker-compose --profile dev up -d postgres_tipsterbyte_dev
    timeout /t 10 /nobreak >nul
) else (
    echo [OK] PostgreSQL esta corriendo
)

echo.
echo [6/7] Recreando base de datos sonarqube...
echo [INFO] Terminando conexiones activas...
docker exec db_pg_tipsterbyte_fx_dev psql -U postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'sonarqube';" >nul 2>&1

echo [INFO] Eliminando base de datos existente...
docker exec db_pg_tipsterbyte_fx_dev psql -U postgres -d postgres -c "DROP DATABASE IF EXISTS sonarqube;" >nul 2>&1

echo [INFO] Creando nueva base de datos...
docker exec db_pg_tipsterbyte_fx_dev psql -U postgres -d postgres -c "CREATE DATABASE sonarqube;"
if errorlevel 1 (
    echo [ERROR] No se pudo crear la base de datos sonarqube
    pause
    exit /b 1
) else (
    echo [OK] Base de datos sonarqube creada
)

echo.
echo [7/7] Iniciando SonarQube con configuracion limpia...
docker-compose --profile dev up -d sonarqube
if errorlevel 1 (
    echo [ERROR] No se pudo iniciar SonarQube
    pause
    exit /b 1
) else (
    echo [OK] SonarQube iniciado
)

echo.
echo [7/7] Esperando a que SonarQube este listo...
echo [INFO] Esto puede tardar 90-120 segundos...

timeout /t 60 /nobreak >nul
echo [INFO] Esperando 60 segundos mas...
timeout /t 60 /nobreak >nul

echo.
echo [INFO] Verificando estado de SonarQube...
docker ps | findstr sonarqube_tipsterbyte >nul
if errorlevel 1 (
    echo [ERROR] SonarQube no esta corriendo
    echo [INFO] Revisa los logs: docker logs sonarqube_tipsterbyte
    pause
    exit /b 1
) else (
    echo [OK] SonarQube esta corriendo
)

echo.
echo ========================================
echo  LIMPIEZA COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo [INFO] SonarQube esta disponible en: http://localhost:9000
echo [INFO] Usuario: admin
echo [INFO] Contrasena: admin
echo.
echo [INFO] Pasos siguientes:
echo   1. Accede a http://localhost:9000
echo   2. Inicia sesion con admin/admin
echo   3. Cambia la contrasena
echo   4. Genera un token en My Account -^> Security
echo   5. Ejecuta: set SONAR_TOKEN=tu_token
echo   6. Ejecuta: run_sonar_analysis.bat
echo.
echo [INFO] Para ver logs en tiempo real:
echo   docker logs -f sonarqube_tipsterbyte
echo.
pause