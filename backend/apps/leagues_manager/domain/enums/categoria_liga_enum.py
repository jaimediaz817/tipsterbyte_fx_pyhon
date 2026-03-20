import enum

class CategoriaLigaEnum(str, enum.Enum):
    """
    Define las categorías estandarizadas para las ligas.
    
    - A: Primera división o máxima categoría.
    - B: Segunda división.
    - C: Tercera división.
    - D: Cuarta división o categorías inferiores.
    
    Estas categorías ayudan a clasificar las ligas según su nivel competitivo.
    """
    A = "A"
    B = "B"
    C = "C"
    D = "D"