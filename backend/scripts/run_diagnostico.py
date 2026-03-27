#!/usr/bin/env python
"""Wrapper para ejecutar diagnóstico visual de forma limpia."""

import subprocess
import sys
import os


def main():
    """Ejecuta el diagnóstico visual ocultando logs DEBUG."""
    script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "diagnose_processes_visual.py"
    )

    # Ejecutar el script redirigiendo stderr para ocultar logs DEBUG
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    )

    # Mostrar solo la salida estándar (sin logs DEBUG)
    if result.stdout:
        print(result.stdout)

    # Si hay error, mostrarlo
    if result.returncode != 0:
        print(f"\nError al ejecutar diagnóstico (código {result.returncode})")
        if result.stderr:
            print(result.stderr)
        return result.returncode

    return 0


if __name__ == "__main__":
    sys.exit(main())
