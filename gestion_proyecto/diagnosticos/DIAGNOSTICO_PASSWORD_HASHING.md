# Diagnóstico: Migración de Password Hashing a Solución Profesional

**Fecha**: 2026-03-28
**Arquitecto**: Cline (AI Software Architect)
**Proyecto**: TipsterByte FX

---

## 1. Estado Actual de la Implementación

### 1.1 Stack de Hashing Actual
- **Algoritmo**: bcrypt (directo, sin wrapper de passlib)
- **Dependencia**: `passlib[bcrypt]` en requirements.txt (inconsistente con uso directo)
- **Ubicación**: `backend/apps/auth/infrastructure/security/password_handler.py`
- **Tests**: 5 tests unitarios en `backend/apps/auth/tests/test_password_handler.py`

### 1.2 Análisis de la Implementación Actual

```python
# Implementación actual - Problemas identificados:
salt = bcrypt.gensalt()  # Sin especificar rounds (usa default 12)
hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
```

**Problemas Detectados**:
1. ❌ **Sin configuración de work factor**: Usa default de 12 rounds
2. ❌ **Dependencia inconsistente**: passlib[bcrypt] instalado pero no usado
3. ❌ **Sin versionado de hashes**: No hay prefijo que indique versión/algoritmo
4. ❌ **Sin migración automática**: No hay mecanismo para re-hashear contraseñas viejas
5. ⚠️ **bcrypt tiene limitaciones**: Máximo 72 bytes de contraseña

---

## 2. Análisis Comparativo de Algoritmos Profesionales

### 2.1 Tabla Comparativa

| Característica        | bcrypt      | Argon2id                  | Scrypt         |
| --------------------- | ----------- | ------------------------- | -------------- |
| **Año**               | 1999        | 2015 (PHC Winner)         | 2009           |
| **Resistencia GPU**   | Moderada    | Excelente                 | Buena          |
| **Resistencia ASIC**  | Moderada    | Excelente                 | Buena          |
| **Memory-Hard**       | ❌ No        | ✅ Sí                      | ✅ Sí           |
| **Configurable**      | Solo rounds | Time, Memory, Parallelism | N, r, p        |
| **Max Password**      | 72 bytes    | Sin límite                | Sin límite     |
| **OWASP Recomendado** | ⚠️ Aceptable | ✅ Preferido               | ✅ Alternativa  |
| **NIST Recomendado**  | ⚠️ Aceptable | ✅ Preferido               | ✅ Alternativa  |
| **Python Support**    | bcrypt      | argon2-cffi               | hashlib.scrypt |
| **Madurez**           | 25+ años    | 11 años                   | 17 años        |

### 2.2 Recomendaciones de Estándares Internacionales

**OWASP (2024)**:
> "Use Argon2id con configuración mínima: 19MB memoria, 2 iteraciones, 1 grado de paralelismo"

**NIST SP 800-63B**:
> "Usar algoritmos de hashing con costo computacional suficiente: PBKDF2, bcrypt, scrypt, o Argon2"

**RFC 9106 (Argon2)**:
> "Argon2id es el modo recomendado para la mayoría de aplicaciones"

---

## 3. Recomendación de Arquitectura

### 3.1 Algoritmo Recomendado: **Argon2id**

**Razones**:
1. ✅ **Ganador del Password Hashing Competition** (estándar mundial)
2. ✅ **Memory-hard**: Resistente a ataques con GPU/ASIC
3. ✅ **Configuración flexible**: Tiempo, memoria, paralelismo
4. ✅ **Sin límite de longitud**: Acepta contraseñas de cualquier tamaño
5. ✅ **Recomendado por OWASP y NIST**
6. ✅ **Biblioteca madura**: argon2-cffi con 10+ años de desarrollo

### 3.2 Configuración Profesional Recomendada

```python
# Configuración Argon2id profesional
ARGON2_CONFIG = {
    "time_cost": 3,        # 3 iteraciones (OWASP: mínimo 2)
    "memory_cost": 65536,  # 64MB (OWASP: mínimo 19MB)
    "parallelism": 4,      # 4 hilos paralelos
    "hash_len": 32,        # 256 bits de hash
    "salt_len": 16,        # 128 bits de salt
}
```

### 3.3 Arquitectura de Migración

```
┌─────────────────────────────────────────────────────────────┐
│                    PASSWORD HANDLER v2.0                      │
├─────────────────────────────────────────────────────────────┤
│  Capa de Abstracción (PasswordHasher)                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  hash_password(password: str) -> str                    │ │
│  │  verify_password(plain: str, hashed: str) -> bool       │ │
│  │  needs_rehash(hashed: str) -> bool                      │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Backends de Hashing                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Argon2id   │  │   bcrypt     │  │   scrypt     │      │
│  │  (Principal) │  │  (Legacy)    │  │  (Opcional)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Migración Automática                                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  - Detección de hash legacy                             │ │
│  │  - Re-hash transparente en login                        │ │
│  │  - Logging de migraciones                               │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Plan de Implementación

### 4.1 Fases de Migración

**Fase 1: Preparación** ⏱️ 30 min
- [ ] Instalar dependencia `argon2-cffi`
- [ ] Crear nueva implementación con Argon2id
- [ ] Mantener compatibilidad con bcrypt existente

**Fase 2: Implementación** ⏱️ 45 min
- [ ] Crear `PasswordHasherV2` con Argon2id
- [ ] Implementar detección de hash legacy
- [ ] Implementar migración automática transparente
- [ ] Crear tests de validación

**Fase 3: Testing** ⏱️ 30 min
- [ ] Tests unitarios de Argon2id
- [ ] Tests de migración de hashes bcrypt
- [ ] Tests de backward compatibility
- [ ] Benchmarks de rendimiento

**Fase 4: Documentación** ⏱️ 15 min
- [ ] Documentar decisión arquitectónica
- [ ] Actualizar README de seguridad
- [ ] Crear guía de configuración

### 4.2 Estrategia de Migración de Datos

```python
# Migración transparente en login
async def verify_password(plain_password: str, stored_hash: str) -> bool:
    # 1. Verificar si es hash legacy (bcrypt)
    if stored_hash.startswith("$2b$") or stored_hash.startswith("$2a$"):
        is_valid = verify_bcrypt(plain_password, stored_hash)
        if is_valid:
            # 2. Re-hash con Argon2id en background
            new_hash = hash_with_argon2id(plain_password)
            await update_user_hash(user_id, new_hash)
            logger.info(f"🔄 Hash migrado de bcrypt a Argon2id para usuario")
        return is_valid
    
    # 3. Hash actual (Argon2id)
    return verify_argon2id(plain_password, stored_hash)
```

---

## 5. Configuración por Entorno

### 5.1 Variables de Entorno (.env)

```bash
# Password Hashing Configuration
PASSWORD_HASHER=argon2id  # argon2id | bcrypt | scrypt

# Argon2id Configuration
ARGON2_TIME_COST=3
ARGON2_MEMORY_COST=65536  # 64MB
ARGON2_PARALLELISM=4

# bcrypt Configuration (legacy)
BCRYPT_ROUNDS=14  # Mayor que default de 12
```

### 5.2 Configuración por Entorno

| Entorno     | Argon2 Memory | Argon2 Time | bcrypt Rounds |
| ----------- | ------------- | ----------- | ------------- |
| Development | 32MB          | 2           | 12            |
| Testing     | 16MB          | 1           | 10            |
| Production  | 64MB          | 3           | 14            |

---

## 6. Métricas de Éxito

### 6.1 KPIs de Seguridad
- ✅ Hash usando algoritmo memory-hard (Argon2id)
- ✅ Configuración alineada con OWASP 2024
- ✅ Migración automática de hashes legacy
- ✅ Sin límite de longitud de contraseña

### 6.2 KPIs de Rendimiento
- Hash time: < 500ms (production)
- Verify time: < 500ms (production)
- Migración transparente sin downtime

---

## 7. Conclusión y Decisión

### Decisión Arquitectónica

**SE RECOMIENDA**: Migrar de bcrypt a **Argon2id**

**Justificación**:
1. **Seguridad superior**: Memory-hard, resistente a ataques modernos
2. **Estándar internacional**: Recomendado por OWASP, NIST, RFC 9106
3. **Flexibilidad**: Configuración ajustable por entorno
4. **Futuro-proof**: Diseñado para amenazas actuales y futuras
5. **Backward compatible**: Migración transparente sin impacto al usuario

**Riesgos Mitigados**:
- ✅ Migración automática en login
- ✅ Fallback a bcrypt para hashes existentes
- ✅ Tests exhaustivos antes de desplegar
- ✅ Rollback posible manteniendo ambos algoritmos

---

**Próximos Pasos**: Proceder con implementación de Fase 1
