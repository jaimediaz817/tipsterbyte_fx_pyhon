#!/bin/bash
# ==============================================================
# TIPSTERBYTE FX - VPS HEALTH CHECK AGENT
# ==============================================================
# AGENTE STANDALONE - NO NECESITA NADA INSTALADO
# Funciona en CUALQUIER Ubuntu / Debian SIN dependencias
# No requiere Python, no requiere librerias, no modifica nada
# ==============================================================

clear

# Colores ANSI para terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

echo -e "${BLUE}"
echo "======================================================================"
echo " 🔷 TIPSTERBYTE FX - AGENTE DE INSPECCION VPS"
echo " 🔷 Diagnostico base del servidor - STANDALONE SIN DEPENDENCIAS"
echo " 🔷 Ejecutado: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================================"
echo -e "${NC}"

echo -e "\n📋 INFORMACION BASICA DEL SERVIDOR:"
echo "-----------------------------------------"

# Informacion del sistema
OS_INFO=$(lsb_release -d 2>/dev/null | cut -f2)
[ -z "$OS_INFO" ] && OS_INFO=$(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
echo -e "✅ Sistema Operativo: $OS_INFO"
echo -e "✅ Hostname: $(hostname)"
echo -e "✅ Arquitectura: $(uname -m)"
echo -e "✅ Kernel: $(uname -r)"
echo -e "✅ Tiempo encendido: $(uptime -p)"
echo -e "✅ Carga del sistema: $(uptime | awk -F'load average:' '{ print $2 }')"

echo -e "\n💾 MEMORIA RAM:"
echo "-----------------------------------------"

# Memoria RAM
MEM_TOTAL=$(free -h --si | awk '/Mem:/ {print $2}')
MEM_USED=$(free -h --si | awk '/Mem:/ {print $3}')
MEM_FREE=$(free -h --si | awk '/Mem:/ {print $4}')
MEM_AVAILABLE=$(free -h --si | awk '/Mem:/ {print $7}')
MEM_PERCENT=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')

if [ $MEM_PERCENT -lt 70 ]; then
    MEM_COLOR=$GREEN
elif [ $MEM_PERCENT -lt 85 ]; then
    MEM_COLOR=$YELLOW
else
    MEM_COLOR=$RED
fi

echo -e "   Total:       $MEM_TOTAL"
echo -e "   Usada:       $MEM_USED"
echo -e "   Libre:       $MEM_FREE"
echo -e "   Disponible:  $MEM_AVAILABLE"
echo -e "   Uso:         ${MEM_COLOR}${MEM_PERCENT}%${NC}"

echo -e "\n💽 ESPACIO EN DISCO:"
echo "-----------------------------------------"

df -h --output=source,size,used,avail,pcent,target | grep -E '^/dev/' | while read line; do
    DEV=$(echo $line | awk '{print $1}')
    SIZE=$(echo $line | awk '{print $2}')
    USED=$(echo $line | awk '{print $3}')
    AVAIL=$(echo $line | awk '{print $4}')
    PERCENT=$(echo $line | awk '{print $5}' | tr -d '%')
    MOUNT=$(echo $line | awk '{print $6}')
    
    if [ $PERCENT -lt 70 ]; then
        COLOR=$GREEN
    elif [ $PERCENT -lt 85 ]; then
        COLOR=$YELLOW
    else
        COLOR=$RED
    fi
    
    echo -e "   ${MOUNT}: ${SIZE} total | ${USED} usado | ${AVAIL} libre | ${COLOR}${PERCENT}%${NC}"
done

echo -e "\n⚙️  PROCESADORES (CPU):"
echo "-----------------------------------------"
CPU_CORES=$(nproc --all)
CPU_MODEL=$(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2 | xargs)
CPU_USAGE=$(top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\([0-9.]*\)%* id.*/\1/' | awk '{print 100 - $1}')

echo -e "   Modelo: $CPU_MODEL"
echo -e "   Nucleos: $CPU_CORES nucleos logicos"
echo -e "   Uso actual: ${CPU_USAGE}%"

echo -e "\n🌐 RED:"
echo "-----------------------------------------"
echo -e "   IP Publica: $(curl -s ifconfig.me 2>/dev/null || echo 'No detectada')"
echo -e "   Conectividad Internet: "
if ping -c 1 google.com > /dev/null 2>&1; then
    echo -e "   ✅ Conectividad a internet OK"
else
    echo -e "   ❌ SIN CONECTIVIDAD A INTERNET"
fi

echo -e "\n🚀 RECURSOS DISPONIBLES PARA LA APLICACION:"
echo "-----------------------------------------"

# Calcular recomendacion
RAM_NUM=$(free --si | awk '/Mem:/ {print $2}')
if [ $RAM_NUM -lt 2000000 ]; then
    echo -e "   ${RED}⚠️  ADVERTENCIA: Menos de 2GB RAM - NO RECOMENDADO para TipsterByte FX${NC}"
    echo -e "   ${YELLOW}   Necesitas minimo 4GB RAM, recomendado 8GB${NC}"
elif [ $RAM_NUM -lt 4000000 ]; then
    echo -e "   ${YELLOW}⚠️  RAM al limite, funciona pero tendras problemas de rendimiento${NC}"
else
    echo -e "   ${GREEN}✅ RAM suficiente para correr TipsterByte FX sin problemas${NC}"
fi

DISK_ROOT=$(df / --output=pcent | tail -1 | tr -d ' %')
if [ $DISK_ROOT -gt 90 ]; then
    echo -e "   ${RED}❌ DISCO CASI LLENO - NO PUEDES INSTALAR NADA AUN${NC}"
fi

echo -e "\n"
echo -e "${BLUE}======================================================================${NC}"
echo -e "📊 RESUMEN FINAL DE ESTADO DE LA VPS:"
echo -e ""
echo -e "✅ ESTE INFORME ES LO QUE DEBES COPIAR Y PEGAR EN CHAT"
echo -e ""
echo -e "Instrucciones:"
echo -e "  1. Selecciona TODO este texto desde el inicio del informe"
echo -e "  2. Copialo completo (Ctrl+Shift+C en SSH)"
echo -e "  3. Pegalo directamente aqui en el chat"
echo -e "  4. Yo analizare y te dire si esta VPS sirve o que necesitas cambiar"
echo -e "${BLUE}======================================================================${NC}"
echo -e "\n"