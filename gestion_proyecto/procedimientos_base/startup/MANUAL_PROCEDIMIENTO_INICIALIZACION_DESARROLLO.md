# 📘 MANUAL PROCEDIMIENTO INICIALIZACIÓN ENTORNO DESARROLLO
> TipsterByte FX - Versión Oficial 2026

---

## ✅ PROCEDIMIENTO ESTANDAR PASO A PASO
Este es el procedimiento oficial y único que se DEBE ejecutar siempre al inicializar el proyecto por primera vez o cuando se requiera resetear completamente el entorno de desarrollo.

---

## 🚩 PRE-REQUISITOS
1. Tener docker y docker-compose instalados
2. Contenedores levantados: `docker-compose up -d`
3. Ubicarte siempre dentro de la carpeta `/backend`
4. Entorno virtual activado
5. Dependencias instaladas: `pip install -r requirements.txt`

---

## 📋 PASO 1: RESET TOTAL DEL PROYECTO (ESTADO CERO)
> ✅ Este comando borra TODO: tablas, migraciones, datos, colecciones MongoDB. Irreversible.

```bash
# 1. Ingresar al menú de estado del proyecto
python manage.py project status
```

✅ Dentro del menú:
1. Selecciona la opción **`2`** (🔴 Resetear el proyecto)
2. Selecciona la opción **`6`** (☢️ Reset TOTAL)
3. Confirma la advertencia de seguridad
4. Espera que termine el proceso automático

✅ Lo que se ejecuta internamente:
```
✅ Borra todas las tablas PostgreSQL
✅ Elimina todos los archivos de migración
✅ Dropea completamente la base de datos MongoDB
✅ Limpia cache y archivos temporales
```

---

## 📋 PASO 2: VERIFICACIÓN Y CONFIGURACIÓN AUTOMÁTICA
Después del reset, volvemos a ejecutar el mismo comando:

```bash
python manage.py project status
```

✅ Ahora selecciona la opción **`1`** (📋 Verificar/Configurar el proyecto)

✅ El sistema ejecutará automáticamente estos pasos en orden:

| Paso | Acción                | Descripción                                                    |
| ---- | --------------------- | -------------------------------------------------------------- |
| 1/5  | ✅ Verificación Docker | Comprueba que PostgreSQL y MongoDB están corriendo             |
| 2/5  | ✅ Migraciones SQL     | Detecta tablas faltantes, crea archivo de migración, lo aplica |
| 3/5  | ✅ Seeders SQL         | Detecta que no hay datos, pregunta si quieres ejecutar seeders |
| 4/5  | ✅ Esquema MongoDB     | Inicializa todas las colecciones e índices                     |
| 5/5  | ✅ Seeders MongoDB     | Carga datos iniciales de ejemplo                               |

---

## ⚠️ PREGUNTAS QUE TE HARÁ EL SISTEMA
Durante la ejecución te aparecerán estas confirmaciones:

> ❓ ¿Deseas crear el archivo de migración ahora?
> ✅ **SIEMPRE RESPONDE `Y`**

> ❓ ¿Deseas aplicar las migraciones ahora?
> ✅ **SIEMPRE RESPONDE `Y`**

> ❓ ¿Deseas ejecutar los seeders SQL ahora?
> ✅ **SIEMPRE RESPONDE `Y`**

> ❓ ¿Deseas inicializar el esquema de MongoDB ahora?
> ✅ **SIEMPRE RESPONDE `Y`**

> ❓ ¿Deseas ejecutar los seeders de MongoDB ahora?
> ✅ **SIEMPRE RESPONDE `Y`**

---

## ✅ FINALIZACIÓN EXITOSA
Cuando todo termine correctamente verás este mensaje:
```
🎉 ¡El proyecto está completamente configurado y listo!
✅ Inicia el servidor con `python manage.py server run`
```

---

## 🚀 PASO 3: INICIAR SERVIDOR
```bash
python manage.py server run
```

✅ Servidor disponible en: `http://localhost:8000`
✅ Documentación Swagger: `http://localhost:8000/docs`

---

## 🔄 COMANDOS RÁPIDOS ALTERNATIVOS
Si ya conoces el procedimiento puedes ejecutar los comandos directamente:

| Acción                   | Comando                                                                         |
| ------------------------ | ------------------------------------------------------------------------------- |
| Reset total              | `python manage.py sql state reset --hard && python manage.py nosql state reset` |
| Crear migración          | `python manage.py sql create-migration -m "mensaje"`                            |
| Aplicar migraciones      | `python manage.py sql migrate`                                                  |
| Ejecutar seeders SQL     | `python manage.py sql seed`                                                     |
| Inicializar MongoDB      | `python manage.py nosql init-schema`                                            |
| Ejecutar seeders MongoDB | `python manage.py nosql seed`                                                   |
| Ver estado completo      | `python manage.py project config`                                               |

---

## ❌ ERRORES COMUNES Y SOLUCIONES

| Error                  | Solución                                               |
| ---------------------- | ------------------------------------------------------ |
| Tabla ya existe        | Ejecutar `python manage.py sql state clear-migrations` |
| Alembic desincronizado | Ejecutar `python manage.py sql stamp head`             |
| MongoDB sin conexión   | Verificar credenciales en .env.dev                     |
| Seeders no ejecutan    | Asegurarte que las migraciones se aplicaron primero    |

---

## 📌 NOTAS IMPORTANTES
1. ⚠️ **NUNCA USES ESTE PROCEDIMIENTO EN PRODUCCIÓN**
2. Siempre ejecuta los comandos desde la carpeta `/backend`
3. No interrumpas el proceso mientras se están ejecutando los seeders
4. Si tienes dudas en cualquier paso, cancela y vuelve a empezar
5. Este procedimiento es el mismo para Windows, Linux y MacOS

---

> ✅ Ultima actualización: 17 Abril 2026
> Documentado desde el flujo oficial implementado en `project_cli.py`