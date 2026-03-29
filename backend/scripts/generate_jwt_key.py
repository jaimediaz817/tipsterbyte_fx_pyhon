#!/usr/bin/env python3
"""
Script para generar una clave secreta JWT segura
Uso: python backend/scripts/generate_jwt_key.py
"""

import secrets
import string


def generate_jwt_secret_key(length: int = 64) -> str:
    """
    Genera una clave secreta JWT segura

    Args:
        length: Longitud de la clave (default: 64 caracteres)

    Returns:
        Clave secreta aleatoria
    """
    # Caracteres permitidos (letras, números, símbolos seguros)
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"

    # Generar clave aleatoria
    secret_key = "".join(secrets.choice(characters) for _ in range(length))

    return secret_key


def main():
    """Función principal"""
    print("=" * 60)
    print("🔐 GENERADOR DE CLAVE SECRETA JWT")
    print("=" * 60)
    print()

    # Generar claves de diferentes longitudes
    print("📋 Opciones de longitud:")
    print("  1. 32 caracteres (mínimo recomendado)")
    print("  2. 64 caracteres (recomendado)")
    print("  3. 128 caracteres (máxima seguridad)")
    print()

    choice = input("Selecciona una opción (1/2/3) [default: 2]: ").strip()

    if choice == "1":
        length = 32
    elif choice == "3":
        length = 128
    else:
        length = 64

    # Generar clave
    secret_key = generate_jwt_secret_key(length)

    print()
    print("=" * 60)
    print("✅ CLAVE GENERADA EXITOSAMENTE")
    print("=" * 60)
    print()
    print(f"🔑 Tu clave secreta JWT ({length} caracteres):")
    print()
    print(f"   {secret_key}")
    print()
    print("=" * 60)
    print()
    print("📝 INSTRUCCIONES:")
    print("  1. Copia la clave generada")
    print("  2. Abre el archivo: backend/.env")
    print("  3. Reemplaza el valor de JWT_SECRET_KEY:")
    print(f"     JWT_SECRET_KEY={secret_key}")
    print()
    print("⚠️  IMPORTANTE:")
    print("  - Guarda esta clave en un lugar seguro")
    print("  - NO la compartas ni la subas a repositorios")
    print("  - Usa claves DIFERENTES para desarrollo y producción")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
