# Solución: Conflicto de Autenticación Claude CLI

## Problema
La consola de Claude muestra la siguiente advertencia:
```
⚠Auth conflict: Using ANTHROPIC_API_KEY instead of Anthropic Console key. Either unset ANTHROPIC_API_KEY, or run `claude /logout`.
```

## Causa
Hay un conflicto entre dos métodos de autenticación:
1. **ANTHROPIC_API_KEY**: Variable de entorno configurada en el sistema
2. **Anthropic Console key**: Credencial almacenada localmente por el CLI de Claude

## Soluciones Posibles

### Opción 1: Eliminar la variable de entorno ANTHROPIC_API_KEY
```bash
# En Windows CMD
set ANTHROPIC_API_KEY=

# En PowerShell
$env:ANTHROPIC_API_KEY = ""

# Para eliminar permanentemente (Windows)
# Ir a: Configuración > Sistema > Información > Configuración avanzada del sistema > Variables de entorno
# Buscar y eliminar ANTHROPIC_API_KEY
```

### Opción 2: Ejecutar claude /logout
```bash
claude /logout
```
Esto eliminará la credencial almacenada y te permitirá iniciar sesión nuevamente.

## Recomendación
Si tienes una API key válida configurada como variable de entorno y prefieres usarla, puedes ignorar la advertencia. Sin embargo, si prefieres usar la autenticación del Console de Anthropic, ejecuta `claude /logout` y vuelve a iniciar sesión.

## Solución Específica para tu Caso

### Archivo de Configuración Encontrado
El archivo `.claude/settings.local.json` contiene:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_API_KEY": "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",
    "ANTHROPIC_MODEL": "openrouter/free"
  }
}
```

### Opciones de Solución

#### Opción A: Eliminar la variable ANTHROPIC_API_KEY del archivo local
Edita `.claude/settings.local.json` y elimina la línea `ANTHROPIC_API_KEY`:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "ANTHROPIC_MODEL": "openrouter/free"
  }
}
```

#### Opción B: Renombrar la variable
Cambia `ANTHROPIC_API_KEY` por otro nombre como `OPENROUTER_API_KEY`:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://openrouter.ai/api",
    "OPENROUTER_API_KEY": "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",
    "ANTHROPIC_MODEL": "openrouter/free"
  }
}
```

### Nota
La advertencia no impide el funcionamiento de Claude, solo indica que está usando un método de autenticación diferente al almacenado localmente. Si usas OpenRouter como proxy, necesitarás ajustar la configuración para que no interfiera con la autenticación nativa de Claude.
