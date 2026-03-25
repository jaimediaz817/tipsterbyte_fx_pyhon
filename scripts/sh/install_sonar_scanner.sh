#!/bin/bash

echo "========================================"
echo " INSTALANDO SONAR SCANNER"
echo "========================================"

# Detectar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macosx"
else
    echo "Sistema operativo no soportado: $OSTYPE"
    exit 1
fi

echo "Sistema detectado: $OS"

# Crear directorio de instalación
INSTALL_DIR="$HOME/sonar-scanner"
mkdir -p "$INSTALL_DIR"

# Descargar sonar-scanner
echo "Descargando sonar-scanner..."
if command -v wget > /dev/null 2>&1; then
    wget -q "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-$OS-x64.zip" -O sonar-scanner.zip
elif command -v curl > /dev/null 2>&1; then
    curl -sL "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-5.0.1.3006-$OS-x64.zip" -o sonar-scanner.zip
else
    echo "Error: Se requiere wget o curl para descargar"
    exit 1
fi

# Extraer
echo "Extrayendo..."
unzip -q sonar-scanner.zip
mv sonar-scanner-cli-5.0.1.3006-$OS-x64/* "$INSTALL_DIR/"
rm -rf sonar-scanner-cli-5.0.1.3006-$OS-x64 sonar-scanner.zip

# Hacer ejecutable
chmod +x "$INSTALL_DIR/bin/sonar-scanner"

# Agregar al PATH
SHELL_RC="$HOME/.bashrc"
if [[ "$OSTYPE" == "darwin"* ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

echo "" >> "$SHELL_RC"
echo "# Sonar Scanner" >> "$SHELL_RC"
echo "export PATH=\"\$PATH:$INSTALL_DIR/bin\"" >> "$SHELL_RC"

echo ""
echo "========================================"
echo " INSTALACIÓN COMPLETADA"
echo "========================================"
echo ""
echo "Directorio: $INSTALL_DIR"
echo ""
echo "Para aplicar los cambios, ejecuta:"
echo "  source $SHELL_RC"
echo ""
echo "O cierra y vuelve a abrir la terminal"
echo ""