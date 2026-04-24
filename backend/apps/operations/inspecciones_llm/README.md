# 🤖 Agente Supervisor TipsterByte FX
✅ **Tercer miembro oficial del equipo**

Opera completamente en background 24/7 sin intervencion humana. Es autonomo, no se duerme, nunca olvida nada y siempre cumple.

---

## 🎯 Arquitectura Oficial
```
inspecciones_llm/
├── domain/
│   └── interfaces/
│       └── i_tarea_agente.py       ✅ Contrato base inmodificable ISP
├── application/
│   └── cargador_tareas.py          ✅ Descubrimiento automatico OCP
├── tareas/
│   └── *.py                        ✅ Todas las tareas son plugins
├── agente_supervisor.py            ✅ Nucleo singleton del agente
├── dashboard_servidor.py           ✅ Servidor web dashboard puerto 9999
├── ejecutar_agente.py              ✅ Punto de entrada
└── README.md
```

---

## ✅ Principios de Arquitectura Cumplidos
| Principio SOLID             | Cumplimiento                                                                   |
| --------------------------- | ------------------------------------------------------------------------------ |
| ✅ **Single Responsibility** | Cada tarea tiene una unica responsabilidad                                     |
| ✅ **Open/Closed**           | Abierto para extender, cerrado para modificar. Agregar tareas NO MODIFICA NADA |
| ✅ **Liskov Substitution**   | Todas las tareas son intercambiables                                           |
| ✅ **Interface Segregation** | Interfaz minima, solo 4 metodos obligatorios                                   |
| ✅ **Dependency Inversion**  | Nada depende de nada. Todas las dependencias van hacia la interfaz             |

---

## 🚀 Como ejecutar
```bash
python inspecciones_llm/ejecutar_agente.py
```

Cuando arranque veras:
```
✅ Dashboard Agente Supervisor disponible en: http://localhost:9999
```

Abre esa direccion en el navegador y ya tienes control total.

---

## 📋 Como agregar una NUEVA tarea
✅ **PASO 1**: Crea un nuevo archivo en `inspecciones_llm/tareas/mi_nueva_tarea.py`

✅ **PASO 2**: Implementa exactamente esta estructura:
```python
from inspecciones_llm.domain.interfaces.i_tarea_agente import ITareaAgente

class MiNuevaTarea(ITareaAgente):

    @property
    def id(self) -> str:
        return "mi_nueva_tarea_001"
    
    @property
    def nombre(self) -> str:
        return "Nombre que se ve en el dashboard"
    
    @property
    def descripcion(self) -> str:
        return "Descripcion detallada de lo que hace"
    
    @property
    def intervalo_segundos(self) -> int:
        return 3600  # Cada cuanto se ejecuta en segundos (ej: 3600 = 1 hora)

    async def ejecutar(self) -> None:
        # TODO: Aqui va TODA la logica de tu tarea
        pass
```

✅ **PASO 3**: Listo. No tienes que hacer NADA mas.
> El agente detectara automaticamente la nueva tarea, la cargara y empezara a ejecutarla en el proximo ciclo. No tienes que registrarla en ningun sitio, no tienes que modificar ningun otro archivo.

---

## 🎛️ Control desde el Dashboard
Accede a `http://localhost:9999` para:
✅ Ver todas las tareas cargadas
✅ Activar / Desactivar tareas en tiempo real
✅ Modificar intervalo de ejecucion al instante
✅ Ejecutar cualquier tarea manualmente
✅ Ver historial y logs de cada ejecucion
✅ Aceptar o Rechazar acciones que requieren aprobacion
✅ Ver estado actual del agente y metricas

---

## ✅ Tareas Incluidas
| Tarea                        | Descripcion                                                                                                                                                          | Intervalo |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| 🩺 `monitoreo_vps_automatico` | Ejecuta Health Check contra VPS principal, guarda metricas en MongoDB, controla tamaño de coleccion, crea backups automaticos y solicita aprobacion antes de limpiar | 5 minutos |

---

## 🎯 Caracteristicas
✅ Ciclo de vida infinito con backoff inteligente
✅ Resiste cualquier excepcion y fallo
✅ Se recupera automaticamente
✅ Dashboard web sin dependencias externas
✅ Actualizacion automatica cada 10 segundos
✅ Solo accesible desde localhost
✅ No consume practicamente recursos
✅ Se detiene de forma segura con CTRL+C

---

## 📏 Reglas Inquebrantables
1. ❌ NUNCA MODIFIQUES `i_tarea_agente.py`
2. ❌ NUNCA MODIFIQUES `cargador_tareas.py`
3. ❌ NUNCA MODIFIQUES EL NUCLEO DEL AGENTE
4. ✅ SIEMPRE agrega nueva funcionalidad creando un nuevo archivo en `/tareas/`

> Cumpliendo estas 4 reglas este sistema sera mantenible y escalable para siempre.