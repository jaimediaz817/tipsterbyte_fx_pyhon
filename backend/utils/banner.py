"""
Módulo de banner para TipsterByte FX.
Proporciona funciones para mostrar el banner ASCII art en color verde.
"""

import io
import sys
from typing import Optional

# --- BANNER ASCII ART ---
TIPSTERBYTE_BANNER = """
\033[92m
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                           ║
║   ████████╗██╗██████╗ ███████╗████████╗███████╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗ ║
║   ╚══██╔══╝██║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝ ║
║      ██║   ██║██████╔╝███████╗   ██║   █████╗  ██████╔╝██████╔╝ ╚████╔╝    ██║   █████╗   ║
║      ██║   ██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗██╔══██╗  ╚██╔╝     ██║   ██╔══╝   ║
║      ██║   ██║██║     ███████║   ██║   ███████╗██║  ██║██████╔╝   ██║      ██║   ███████╗ ║
║      ╚═╝   ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═════╝    ╚═╝      ╚═╝   ╚══════╝ ║
║                                                                                           ║
║                         ★  F X  ★   Backend Management System                             ║
║                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
\033[0m
"""


def show_banner():
    """Muestra el banner ASCII art de TIPSTERBYTE en color verde."""
    try:
        # Configurar codificación UTF-8 para Windows
        if sys.platform == "win32":
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        print(TIPSTERBYTE_BANNER)
    except (UnicodeEncodeError, AttributeError, Exception):
        # Fallback: mostrar banner sin caracteres especiales
        print("=" * 80)
        print("TIPSTERBYTE FX - Backend Management System")
        print("=" * 80)


def show_banner_with_message(message: Optional[str] = None):
    """
    Muestra el banner ASCII art de TIPSTERBYTE en color verde con un mensaje opcional.

    Args:
        message: Mensaje adicional a mostrar después del banner
    """
    show_banner()
    if message:
        print(f"\033[92m{message}\033[0m")
        print()


def show_banner_for_command(command_name: str):
    """
    Muestra el banner ASCII art de TIPSTERBYTE en color verde con el nombre del comando.

    Args:
        command_name: Nombre del comando que se está ejecutando
    """
    show_banner()
    print(f"\033[92m Ejecutando comando: {command_name}\033[0m")
    print()
