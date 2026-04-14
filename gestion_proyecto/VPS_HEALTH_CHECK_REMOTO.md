# ✅ DOCUMENTACION OFICIAL - VPS HEALTH CHECK REMOTO
✅ **NO NECESITAS CONECTARTE A LA VPS**
✅ **NO NECESITAS COPIAR NINGUN ARCHIVO**
✅ **NO NECESITAS NADA INSTALADO EN EL SERVIDOR**
✅ **TODO FUNCIONA AUTOMATICAMENTE**

---

## 🎯 DESCRIPCION

Sistema que permite ejecutar el diagnostico de VPS en CUALQUIER servidor remoto sin tener que acceder manualmente por SSH.

El script `vps_health_check.sh` NUNCA ABANDONA TU ORDENADOR. Se envía directamente por la conexión SSH en tiempo real, se ejecuta 100% en memoria y no deja ningun rastro.

---

## 📋 ARQUITECTURA

| Capa       | Archivo                                                                                | Descripción                                                                |
| ---------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| 🟢 Agente   | `scripts/linux/vps_health_check.sh`                                                    | Script real de diagnostico. **Es la unica fuente de verdad oficial**       |
| 🔵 Core     | `backend/core/ssh/remote_script_executor.py`                                           | Ejecutor SSH universal bajo nivel. No requiere nada en el servidor destino |
| 🟡 Servicio | `backend/apps/platform_config/application/services/remote_vps_health_check_service.py` | Logica de negocio y validaciones                                           |
| 🔴 Lanzador | `ejecutar_health_check_vps_principal.py`                                               | Script listo para ejecutar directamente desde consola                      |

---

## 🚀 COMO USAR

### ✅ Paso 1: Ubicacion
Siempre ejecutar desde la RAIZ DEL PROYECTO:
```
c:\Users\jdiaz\Documents\JDiaz-PC-DESKTOP-2\proyectos_jdiaz_pc_local\TIPSTERBYTE\tipsterByte_fx
```

### ✅ Paso 2: Ejecutar
```bash
python ejecutar_health_check_vps_principal.py
```

✅ **NO HAY QUE MODIFICAR NADA. NO HAY QUE PONER CREDENCIALES.**

---

## 🎯 COMO FUNCIONA INTERNAMENTE

1.  Python lee el archivo `vps_health_check.sh` COMPLETO a la memoria RAM
2.  Se conecta automaticamente por SSH a la VPS principal usando las credenciales del `config.py`
3.  Envia TODO el contenido del script bash directamente por stdin
4.  En la VPS se ejecuta `bash -s` que recibe el codigo y lo ejecuta sin escribir nada a disco
5.  Toda la salida stdout y stderr regresa de regreso
6.  Se cierra la conexion.

✅ **EN NINGUN MOMENTO EXISTE EL ARCHIVO .sh EN LA VPS.**

---

## 💻 USO DESDE CUALQUIER PARTE DEL CODIGO

```python
from backend.apps.platform_config.application.services.remote_vps_health_check_service import RemoteVpsHealthCheckService

# ✅ Para VPS principal:
resultado = RemoteVpsHealthCheckService.execute_on_remote_vps()

# ✅ Para cualquier otra VPS:
resultado = RemoteVpsHealthCheckService.execute_on_remote_vps(
    hostname="1.2.3.4",
    username="root",
    password="xxx"
)
```

---

## 📊 Datos que devuelve

| Campo                              | Descripción                                 | Tipo    |
| ---------------------------------- | ------------------------------------------- | ------- |
| `resultado.success`                | Estado final de la ejecución                | `bool`  |
| `resultado.exit_code`              | Código de salida nativo de bash             | `int`   |
| `resultado.stdout`                 | Salida COMPLETA del diagnostico             | `str`   |
| `resultado.stderr`                 | Errores y advertencias si se produjeron     | `str`   |
| `resultado.execution_time_seconds` | Tiempo total transcurrido                   | `float` |
| `resultado.hostname`               | Dirección IP / Hostname del servidor remoto | `str`   |

---

## ✅ CARACTERISTICAS

✅ Funciona en cualquier Ubuntu / Debian
✅ No requiere dependencias en el servidor objetivo
✅ No modifica absolutamente nada
✅ No deja historial en .bash_history
✅ No requiere permisos especiales
✅ Tiempo promedio de ejecucion: 3 segundos
✅ Compatible con autenticacion por contraseña y por llave privada

---

## ⚙️ CONFIGURACION

Todas las credenciales estan en `backend/core/config.py`:
```python
VPS_MAIN_HOST = "143.110.239.197"
VPS_MAIN_PORT = 22
VPS_MAIN_USER = "jdiaz"
VPS_MAIN_PASSWORD = "18402120"
VPS_MAIN_PRIVATE_KEY = "ruta a clave privada"
```

---

## 📌 NOTAS IMPORTANTES

1.  **Nunca modifiques el script .sh directamente en la VPS**. La unica version valida es la que tienes aqui en local.
2.  Cuando cambias algo en `vps_health_check.sh` automaticamente corre la version nueva en todos los servidores.
3.  Este mismo patron se puede usar para ejecutar CUALQUIER script bash en cualquier servidor.