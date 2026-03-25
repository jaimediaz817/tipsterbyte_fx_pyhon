#!/bin/bash

# ================================
# SCRIPT DE ANÁLISIS SONARQUBE
# Proyecto: TipsterByte FX
# ================================

set -e  # Salir si hay algún error

echo ""
echo "========================================"
echo " ANÁLISIS DE CALIDAD - SONARQUBE"
echo "========================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "sonar-project.properties" ]; then
    echo -e "${RED}[ERROR]${NC} No se encontró sonar-project.properties"
    echo -e "${YELLOW}[INFO]${NC} Ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Verificar que Docker está corriendo
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Docker no está corriendo o no tienes permisos"
    echo -e "${YELLOW}[INFO]${NC} Inicia Docker y vuelve a intentar"
    exit 1
fi

echo -e "${GREEN}[1/4]${NC} Verificando SonarQube en Docker..."
if docker ps | grep -q sonarqube_tipsterbyte; then
    echo -e "${GREEN}[OK]${NC} SonarQube está corriendo"
else
    echo -e "${YELLOW}[INFO]${NC} Iniciando SonarQube..."
    docker-compose up -d sonarqube
    echo -e "${YELLOW}[INFO]${NC} Esperando 30 segundos para que SonarQube inicie..."
    sleep 30
fi

echo ""
echo -e "${GREEN}[2/4]${NC} Instalando dependencias de testing..."
cd backend
pip install pytest-cov pytest-xdist -q
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Falló la instalación de dependencias"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Dependencias instaladas"

echo ""
echo -e "${GREEN}[3/4]${NC} Ejecutando tests con coverage..."
python -m pytest --cov=apps --cov=core --cov=shared --cov-report=xml:coverage.xml --junitxml=test-results.xml -v
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Algunos tests fallaron, pero continuando con el análisis..."
fi
echo -e "${GREEN}[OK]${NC} Tests ejecutados y coverage generado"

echo ""
echo -e "${GREEN}[4/4]${NC} Ejecutando análisis de SonarQube..."
cd ..

if [ -z "$SONAR_TOKEN" ]; then
    echo -e "${YELLOW}[WARNING]${NC} Variable SONAR_TOKEN no configurada"
    echo -e "${YELLOW}[INFO]${NC} Genera un token en: http://localhost:9000/account/security"
    echo -e "${YELLOW}[INFO]${NC} Luego ejecuta: export SONAR_TOKEN=tu_token_aqui"
    echo ""
    echo -e "${YELLOW}[INFO]${NC} Ejecutando análisis sin token (modo público)..."
    sonar-scanner -Dsonar.host.url=http://localhost:9000
else
    echo -e "${YELLOW}[INFO]${NC} Usando token de autenticación..."
    sonar-scanner -Dsonar.login=$SONAR_TOKEN -Dsonar.host.url=http://localhost:9000
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Falló el análisis de SonarQube"
    echo -e "${YELLOW}[INFO]${NC} Verifica que SonarQube esté corriendo en http://localhost:9000"
    exit 1
fi

echo ""
echo "========================================"
echo -e "${GREEN} ANÁLISIS COMPLETADO EXITOSAMENTE${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}[INFO]${NC} Dashboard: http://localhost:9000"
echo -e "${YELLOW}[INFO]${NC} Proyecto: tipsterbyte_fx"
echo ""