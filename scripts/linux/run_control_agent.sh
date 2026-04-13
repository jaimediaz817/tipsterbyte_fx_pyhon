#!/bin/bash
# TipsterByte Control Agent - Script de ejecucion para Ubuntu / Linux
# Este script se puede ejecutar en CUALQUIER ubicacion de la VPS

set -e

echo "🔷 Iniciando TipsterByte Control Agent..."
echo "🔷 Buscando archivo .env automaticamente..."

# Buscar archivo .env en ubicaciones comunes
ENV_PATHS=(
    "./.env"
    "../.env"
    "../../.env"
    "/opt/tipsterbyte/.env"
    "$HOME/tipsterbyte/.env"
    "/var/www/tipsterbyte/.env"
)

FOUND_ENV=""
for path in "${ENV_PATHS[@]}"; do
    if [ -f "$path" ]; then
        FOUND_ENV="$path"
        echo "✅ Archivo .env encontrado en: $FOUND_ENV"
        break
    fi
done

if [ -z "$FOUND_ENV" ]; then
    echo "⚠️  No se encontro archivo .env, el agente usara valores por defecto"
    echo "ℹ️  Puedes pasar la ruta al .env como parametro: ./run_control_agent.sh /ruta/a/.env"
fi

# Verificar si tenemos el ejecutable compilado o usamos python
if [ -f "./tipsterbyte_control_agent" ]; then
    echo "✅ Usando ejecutable standalone compilado"
    chmod +x ./tipsterbyte_control_agent
    ./tipsterbyte_control_agent "$@"
elif command -v python3 &> /dev/null; then
    echo "✅ Usando Python 3 del sistema"
    if [ ! -f "./tipsterbyte_control_agent.py" ]; then
        echo "⬇️  Descargando agente automaticamente..."
        curl -s -O https://raw.githubusercontent.com/jaimediaz817/tipsterbyte_fx_pyhon/main/scripts/linux/tipsterbyte_control_agent.py
    fi
    python3 tipsterbyte_control_agent.py "$@"
else
    echo "❌ No se encontro ni ejecutable ni Python 3 en el sistema"
    echo "ℹ️  Instala python3 primero: apt update && apt install python3 python3-pip -y"
    exit 1
fi

echo ""
echo "======================================================================"
echo "📋 INSTRUCCIONES:"
echo "   1. Selecciona TODO el texto de arriba desde el inicio del informe"
echo "   2. Copialo completo (Ctrl+Shift+C)"
echo "   3. Pegalo directamente en el chat de Cline"
echo "   4. Espera el analisis automatico y las recomendaciones"
echo "======================================================================"