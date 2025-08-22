import enum

class ProcessStatus(str, enum.Enum):
    """
    Define los posibles estados de un proceso.
    
    Hereda de 'str' para que sus valores se serialicen como strings
    en la base de datos y en las respuestas de la API, manteniendo
    la compatibilidad.
    """
    PENDING   = "pending"
    COMPLETED = "completed"
    FAILED    = "failed"
    RUNNING   = "running"  # Ejemplo de cómo podrías añadir más estados