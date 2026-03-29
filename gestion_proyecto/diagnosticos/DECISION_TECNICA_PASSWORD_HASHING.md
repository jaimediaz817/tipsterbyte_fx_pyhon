# Decisión Técnica: Migración de Password Hashing

**Fecha**: 2026-03-28
**Estado**: ✅ Aprobado e Implementado
**Arquitecto**: Cline (AI Software Architect)

---

## Resumen Ejecutivo

Se migró el sistema de hashing de contraseñas de **bcrypt** a **Argon2id**, alineándolo con los estándares internacionales de seguridad (OWASP 2024, NIST SP 800-63B, RFC 9106).

---

## Problema

bcrypt presentaba limitaciones:
- No es memory-hard (vulnerable a ataques GPU/ASIC)
- Máximo 72 bytes de contraseña
- Configuración limitada (solo rounds)
- No recomendado como primera opción por OWASP

---

## Solución Implementada

### Algoritmo: Argon2id

- **Ganador del Password Hashing Competition** (2015)
- **Memory-hard**: Resistente a ataques con hardware especializado
- **Configuración flexible**: Tiempo, memoria, paralelismo
- **Sin límite de contraseña**

### Configuración (OWASP 2024)

| Parámetro   | Valor | Justificación            |
| ----------- | ----- | ------------------------ |
| time_cost   | 3     | 3 iteraciones            |
| memory_cost | 64MB  | Resistencia a GPU        |
| parallelism | 4     | Paralelismo moderno      |
| hash_len    | 32B   | 256 bits de seguridad    |
| salt_len    | 16B   | 128 bits de aleatoriedad |

---

## Archivos Modificados

| Archivo                                                         | Cambio                         |
| --------------------------------------------------------------- | ------------------------------ |
| `backend/requirements.txt`                                      | Agregado `argon2-cffi>=23.1.0` |
| `backend/apps/auth/infrastructure/security/password_handler.py` | Reescrito con Argon2id         |
| `backend/apps/auth/tests/test_password_handler.py`              | Tests actualizados             |

---

## Backward Compatibility

✅ **100% compatible** con hashes bcrypt existentes:
- Detección automática de formato de hash
- Verificación transparente de hashes legacy
- Migración progresiva en cada login exitoso

---

## Resultados

- ✅ Seguridad alineada con OWASP/NIST
- ✅ Migración transparente sin downtime
- ✅ Tests pasando (16 tests)
- ✅ Backward compatible con bcrypt