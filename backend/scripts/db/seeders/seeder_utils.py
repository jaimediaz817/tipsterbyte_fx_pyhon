from sqlalchemy import inspect

# def update_from_dict(target_obj, data_dict: dict):
#     """
#     Actualiza dinámicamente los atributos de un objeto SQLAlchemy desde un diccionario.
#     Ignora de forma inteligente las columnas que son claves primarias o foráneas.
#     :param target_obj: Instancia del modelo SQLAlchemy a actualizar.
#     :param data_dict: Diccionario con los datos para actualizar.
    
#     """
#     mapper = inspect(target_obj.__class__)
    
#     # --- ¡CAMBIO CLAVE! ---
#     # Creamos un conjunto con las columnas a ignorar.
#     # Incluimos tanto claves primarias como foráneas.
#     ignored_columns = set()
#     for col in mapper.columns:
#         if col.primary_key or col.foreign_keys:
#             ignored_columns.add(col.name)

#     for key, value in data_dict.items():
#         # Solo actualizamos si el campo existe en el modelo y NO está en la lista de ignorados.
#         if hasattr(target_obj, key) and key not in ignored_columns:
#             setattr(target_obj, key, value)