from sqlalchemy.orm import Session
from loguru import logger
from sqlalchemy import text 

def truncate_tables(db: Session, table_names: list[str]):
    """
    Trunca (vacía) una lista de tablas de forma segura.
    Desactiva temporalmente las restricciones de clave foránea para permitir el truncado.
    """
    if not table_names:
        logger.warning("No se especificaron tablas para truncar.")
        return

    logger.info(f"Intentando truncar las siguientes tablas: {', '.join(table_names)}")
    
    sql_query_str = f"TRUNCATE TABLE {', '.join(table_names)} RESTART IDENTITY CASCADE;"

    try:
        # --- ¡CAMBIO CLAVE! ---
        # Envolver el string de la consulta con la función text()
        db.execute(text(sql_query_str))
        db.commit()
        logger.success(f"✅ Tablas truncadas exitosamente: {', '.join(table_names)}")
    except Exception as e:
        logger.error(f"❌ Error al truncar las tablas: {e}")
        db.rollback()
        raise